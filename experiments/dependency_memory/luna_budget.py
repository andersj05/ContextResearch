"""Serial Luna credit-equivalent reservations; never an invoice or billing client.

The reservation uses the published model maxima and a conservative input-rate
margin. Actual requests must have a separately enforced 32,768-byte body cap.
The app-server usage object is checked after completion. Any uncertain failure
holds its reservation and stops the batch; no credit purchase or retry exists.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


MAX_ATTEMPTS = 96
MAX_INPUT_TOKENS = 1_050_000
MAX_OUTPUT_TOKENS = 128_000
LONG_CONTEXT_THRESHOLD = 272_000
MAX_BODY_BYTES = 32_768
MILLION = Decimal(1_000_000)
INPUT_RATE = Decimal("5")
CACHED_INPUT_RATE = Decimal("0.5")
CONSERVATIVE_INPUT_RATE = Decimal("6.25")
OUTPUT_RATE = Decimal("30")
PER_ATTEMPT_RESERVATION = (
    Decimal(MAX_INPUT_TOKENS) * CONSERVATIVE_INPUT_RATE
    + Decimal(MAX_OUTPUT_TOKENS) * OUTPUT_RATE
) / MILLION


class BudgetExceeded(RuntimeError):
    """A new dispatch cannot fit the prespecified ceiling."""


class BudgetStopped(RuntimeError):
    """An uncertain failure stopped the batch or an attempt is still pending."""


class InvalidUsage(ValueError):
    """Usage cannot safely release a credit-equivalent reservation."""


def _credit_fields(name: str, value: Decimal) -> dict[str, Any]:
    return {name: float(value), name + "_exact": str(value)}


def _tokens(usage: dict[str, Any], name: str, *, default: int | None = None) -> int:
    value = usage.get(name, default)
    if type(value) is not int or value < 0:
        raise InvalidUsage(f"{name} must be a non-negative integer")
    return value


def usage_estimates(usage: dict[str, Any]) -> dict[str, Any]:
    """Validate one complete app-server usage breakdown without changing state."""
    if not isinstance(usage, dict):
        raise InvalidUsage("Usage must be an object")
    inputs = _tokens(usage, "inputTokens")
    cached = _tokens(usage, "cachedInputTokens")
    outputs = _tokens(usage, "outputTokens")
    reasoning = _tokens(usage, "reasoningOutputTokens")
    cache_writes_reported = "cacheWriteInputTokens" in usage
    # Zero is only a validation fallback for the optional bucket. Preserve its
    # unknown measurement in saved evidence; the conservative charge uses all
    # input tokens and does not depend on an observed cache-write count.
    cache_writes = _tokens(usage, "cacheWriteInputTokens", default=0)
    if cached > inputs or cache_writes > inputs or cached + cache_writes > inputs:
        raise InvalidUsage("Cache buckets must fit within total input tokens")
    if reasoning > outputs:
        raise InvalidUsage("Reasoning tokens must fit within total output tokens")
    if inputs >= LONG_CONTEXT_THRESHOLD:
        raise InvalidUsage("Observed input exceeds the reviewed short-context envelope")
    if outputs > MAX_OUTPUT_TOKENS:
        raise InvalidUsage("Observed output exceeds the reviewed model maximum")
    if "totalTokens" in usage and _tokens(usage, "totalTokens") != inputs + outputs:
        raise InvalidUsage("Total tokens must equal input plus output tokens")
    conservative = (Decimal(inputs) * CONSERVATIVE_INPUT_RATE + Decimal(outputs) * OUTPUT_RATE) / MILLION
    basic = (Decimal(inputs - cached) * INPUT_RATE + Decimal(cached) * CACHED_INPUT_RATE
             + Decimal(outputs) * OUTPUT_RATE) / MILLION
    return {
        "usage": {
            "inputTokens": inputs, "cachedInputTokens": cached,
            "cacheWriteInputTokens": cache_writes if cache_writes_reported else None,
            "outputTokens": outputs,
            "reasoningOutputTokens": reasoning, "totalTokens": inputs + outputs,
        },
        **_credit_fields("conservative_credit_equivalent", conservative),
        **_credit_fields("basic_rate_credit_estimate", basic),
        "cache_write_tokens_reported": cache_writes_reported,
        "cache_write_pricing_unresolved": not cache_writes_reported or cache_writes > 0,
        "reasoning_already_in_output": True,
        "observed_credit_balance_debit": None,
        "observed_dollar_charge": None,
        "accounting_scope": "Token-derived planning equivalents; not an observed subscription invoice",
    }


class CreditBudget:
    """One outstanding generation at a time, reserved before dispatch.

    ``settle`` may release unused reservation only for complete valid usage.
    Invalid settlement leaves the reservation held. The caller then invokes
    ``fail`` and aborts. Authentication/account-query HTTP requests are not
    counted as generations; hidden provider work is not measured by this class.
    """

    ATTEMPT_LIMIT = MAX_ATTEMPTS

    def __init__(self, cap_credits: int | float | str | Decimal = 20, max_attempts: int = MAX_ATTEMPTS):
        if isinstance(cap_credits, bool):
            raise ValueError("Credit cap must be a finite non-negative number")
        try:
            cap = Decimal(str(cap_credits))
        except (InvalidOperation, ValueError) as error:
            raise ValueError("Credit cap must be a finite non-negative number") from error
        if not cap.is_finite() or cap < 0:
            raise ValueError("Credit cap must be a finite non-negative number")
        if type(max_attempts) is not int or not 0 <= max_attempts <= self.ATTEMPT_LIMIT:
            raise ValueError(f"Generation-attempt ceiling must be an integer from 0 to {self.ATTEMPT_LIMIT}")
        self.cap = cap
        self.max_attempts = max_attempts
        self.attempts = 0
        self.settled_attempts = 0
        self.failed_attempts = 0
        self._settled_equivalent = Decimal(0)
        self._uncertain_reservations = Decimal(0)
        self._pending: int | None = None
        self._stopped = False

    @property
    def committed(self) -> Decimal:
        pending = PER_ATTEMPT_RESERVATION if self._pending is not None else Decimal(0)
        return self._settled_equivalent + self._uncertain_reservations + pending

    def reserve(self) -> int:
        if self._stopped:
            raise BudgetStopped("Batch stopped after uncertain accounting")
        if self._pending is not None:
            raise BudgetStopped("A generation reservation is already pending")
        if self.attempts >= self.max_attempts:
            raise BudgetExceeded("Generation-attempt ceiling reached")
        if self.committed + PER_ATTEMPT_RESERVATION > self.cap:
            raise BudgetExceeded("Insufficient credit-equivalent budget for a complete reservation")
        self.attempts += 1
        self._pending = self.attempts
        return self._pending

    def _require_ticket(self, ticket: int) -> None:
        if type(ticket) is not int or self._pending is None or ticket != self._pending:
            raise ValueError("Ticket must identify the outstanding reservation")

    def settle(self, ticket: int, usage: dict[str, Any]) -> dict[str, Any]:
        self._require_ticket(ticket)
        metadata = usage_estimates(usage)
        actual = Decimal(metadata["conservative_credit_equivalent_exact"])
        if actual > PER_ATTEMPT_RESERVATION:
            raise InvalidUsage("Usage exceeds the reserved accounting envelope")
        self._settled_equivalent += actual
        self._pending = None
        self.settled_attempts += 1
        return {
            "ticket": ticket, "status": "settled", **metadata,
            **_credit_fields("released_credit_equivalent", PER_ATTEMPT_RESERVATION - actual),
            "budget": self.snapshot(),
        }

    def fail(self, ticket: int, reason: str = "transport_failure") -> dict[str, Any]:
        self._require_ticket(ticket)
        # Store a small category, never uncontrolled provider error text.
        if not isinstance(reason, str) or not reason or len(reason) > 64 or any(
            character not in "abcdefghijklmnopqrstuvwxyz_" for character in reason
        ):
            raise ValueError("Failure reason must be a short lowercase category")
        self._uncertain_reservations += PER_ATTEMPT_RESERVATION
        self._pending = None
        self._stopped = True
        self.failed_attempts += 1
        return {"ticket": ticket, "status": "reservation_retained", "reason": reason,
                "budget": self.snapshot()}

    def snapshot(self) -> dict[str, Any]:
        return {
            **_credit_fields("cap_credit_equivalent", self.cap),
            **_credit_fields("per_attempt_reservation", PER_ATTEMPT_RESERVATION),
            **_credit_fields("committed_credit_equivalent", self.committed),
            **_credit_fields("settled_credit_equivalent", self._settled_equivalent),
            **_credit_fields("uncertain_credit_reservations", self._uncertain_reservations),
            **_credit_fields("remaining_credit_equivalent", self.cap - self.committed),
            "generation_attempts": self.attempts,
            "generation_attempt_ceiling": self.max_attempts,
            "settled_attempts": self.settled_attempts,
            "failed_attempts": self.failed_attempts,
            "pending_ticket": self._pending,
            "stopped": self._stopped,
            "api_dollar_spend_authorized": 0,
            "api_key_fallback": False,
            "credit_purchases": 0,
            "reset_redemptions": 0,
            "reservation_assumptions": {
                "model": "gpt-5.6-luna", "input_model_maximum": MAX_INPUT_TOKENS,
                "output_model_maximum": MAX_OUTPUT_TOKENS,
                "required_request_body_byte_cap": MAX_BODY_BYTES,
                "required_observed_input_below": LONG_CONTEXT_THRESHOLD,
                "conservative_input_credits_per_million": float(CONSERVATIVE_INPUT_RATE),
                "output_credits_per_million": float(OUTPUT_RATE),
                "reasoning_included_in_output": True,
                "cache_write_margin_is_assumption": True,
                "transport_and_model_identity_require_separate_verification": True,
            },
        }
