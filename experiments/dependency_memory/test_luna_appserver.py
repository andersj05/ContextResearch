"""Offline protocol and accounting checks; no CLI process or network starts."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from artifact_workflow import Config
from luna_appserver import LunaClient, MODEL, PROVIDER, ResponseFormatError, TransportError, check_quota, quota_snapshot
from luna_budget import CreditBudget, InvalidUsage, PER_ATTEMPT_RESERVATION
from luna_isolation import expected_isolation_config
from pilot_interface import inspection_request


THREAD = "synthetic-thread"
TURN = "synthetic-turn"
USAGE = {"inputTokens": 1000, "cachedInputTokens": 100,
         "outputTokens": 40, "reasoningOutputTokens": 20, "totalTokens": 1040}


def limits(used=20, **overrides):
    row = {"primary": {"usedPercent": used, "windowDurationMins": 10080,
                       "resetsAt": 9999999999}, "secondary": None,
           "rateLimitReachedType": None, "spendControlReached": False,
           "individualLimit": None, "credits": {"hasCredits": True, "unlimited": False,
                                                "balance": "100"}}
    row.update(overrides)
    return {"ordinaryUsageAllowed": True, "rateLimits": row, "rateLimitsByLimitId": {"codex": row}}


def event(method, **params):
    return {"method": method, "params": {"threadId": THREAD, "turnId": TURN, **params}}


def successful_events(*, controlled_stop=True):
    result = [
        event("item/completed", item={"type": "agentMessage", "id": "answer", "text": '{"inspect":true}'}),
        event("thread/tokenUsage/updated", tokenUsage={"total": dict(USAGE), "last": dict(USAGE)}),
    ]
    turn = {"id": TURN, "status": "completed", "error": None}
    if controlled_stop:
        guard = {"codexErrorInfo": "sessionBudgetExceeded", "message": "synthetic guard"}
        result.append(event("error", error=guard, willRetry=False))
        turn.update(status="failed", error=guard)
    result.append(event("turn/completed", turn=turn))
    return result


class FakeServer:
    """Predetermined RPC replies and events with no provider implementation."""

    def __init__(self, *, events=None, auth="chatgpt", before=None, after=None, after_error=None,
                 config_change=None):
        self.events = deepcopy(successful_events() if events is None else events)
        self.auth = auth
        self.before = limits() if before is None else before
        self.after = limits(21) if after is None else after
        self.after_error = after_error
        self.config_change = config_change
        self.notifications = []
        self.calls = []
        self.closed = False
        self.quota_reads = 0
        self.client = None

    def initialize(self):
        self.calls.append(("initialize", None))

    def close(self):
        self.closed = True

    def rpc(self, method, params):
        self.calls.append((method, deepcopy(params)))
        if method == "account/read":
            return {"account": {"type": self.auth}}
        if method == "account/rateLimits/read":
            self.quota_reads += 1
            if self.quota_reads == 1:
                return deepcopy(self.before)
            if self.after_error:
                raise self.after_error
            return deepcopy(self.after)
        if method == "config/read":
            config = {
                **expected_isolation_config(),
                "model_provider": PROVIDER,
                "model_providers": {PROVIDER: {"requires_openai_auth": True,
                    "request_max_retries": 0, "stream_max_retries": 0,
                    "supports_websockets": False}},
            }
            if self.config_change:
                self.config_change(config)
            return {"config": config}
        if method == "thread/start":
            return {"model": MODEL, "modelProvider": PROVIDER, "runtimeWorkspaceRoots": [],
                    "thread": {"id": THREAD, "turns": []}}
        if method == "turn/start":
            # Financial/accounting reservation must precede any generation RPC.
            if self.client.budget.snapshot()["pending_ticket"] is None:
                raise AssertionError("Generation was dispatched without a reservation")
            return {"turn": {"id": TURN}}
        raise AssertionError("Unexpected RPC: " + method)

    def receive(self, timeout=None):
        if not self.events:
            raise TransportError("synthetic_missing_completion")
        return self.events.pop(0)


def make_client():
    # Constructor attestation has its own wire/binary audit. These tests isolate
    # the generation protocol and never load an installed executable.
    client = LunaClient.__new__(LunaClient)
    client.executable = "synthetic-executable-never-run"
    client.audit = {"launch_ready": True}
    client.budget = CreditBudget()
    client.timeout = 2
    client.last_metadata = {}
    client.stopped = False
    client.isolation_overrides = ()
    client.thread_parameters = lambda cwd, provider: {"cwd": cwd, "modelProvider": provider}
    client.turn_parameters = lambda thread, request: {"threadId": thread, "public": request}
    return client


class LunaAppServerTests(unittest.TestCase):
    def setUp(self):
        self.request = inspection_request(Config(recovery_available=True))

    def invoke(self, server, client=None):
        client = client or make_client()
        server.client = client
        with patch("luna_appserver.AppServer", return_value=server):
            result = client.complete(self.request)
        return client, result

    def assert_failed_reserved(self, server):
        client = make_client()
        with self.assertRaises(TransportError):
            self.invoke(server, client)
        self.assertTrue(client.stopped)
        self.assertEqual(client.budget.attempts, 1)
        self.assertEqual(client.budget.committed, PER_ATTEMPT_RESERVATION)
        self.assertEqual(client.last_metadata["credit_accounting"]["status"], "reservation_retained")
        self.assertTrue(server.closed)
        return client

    def test_completed_json_with_controlled_harness_stop_is_accepted(self):
        server = FakeServer()
        client, answer = self.invoke(server)
        self.assertEqual(answer, {"inspect": True})
        self.assertEqual(client.last_metadata["harness_termination"], "session_budget_exceeded")
        self.assertEqual(client.last_metadata["credit_accounting"]["status"], "settled")
        self.assertEqual(client.budget.settled_attempts, 1)
        self.assertFalse(client.stopped)
        self.assertTrue(server.closed)
        self.assertEqual(sum(method == "turn/start" for method, _ in server.calls), 1)
        self.assertIsNone(client.last_metadata["usage"]["cache_write_input_tokens"])
        self.assertFalse(client.last_metadata["cache_write_tokens_reported"])
        self.assertIsNone(client.last_metadata["credit_accounting"]["usage"]["cacheWriteInputTokens"])
        self.assertFalse(client.last_metadata["credit_accounting"]["cache_write_tokens_reported"])
        self.assertTrue(client.last_metadata["credit_accounting"]["cache_write_pricing_unresolved"])

    def test_invalid_json_is_a_settled_policy_failure_and_next_request_can_run(self):
        for text in ("{", '{"inspect":true,"inspect":false}', '{"inspect":NaN}'):
            with self.subTest(text=text):
                events = successful_events()
                events[0]["params"]["item"]["text"] = text
                server, client = FakeServer(events=events), make_client()
                with self.assertRaisesRegex(ResponseFormatError, "invalid_response_json"):
                    self.invoke(server, client)
                self.assertFalse(client.stopped)
                self.assertTrue(server.closed)
                self.assertEqual(client.last_metadata["status"], "completed")
                self.assertEqual(client.last_metadata["response_status"], "invalid_json")
                self.assertEqual(client.last_metadata["credit_accounting"]["status"], "settled")
                self.assertEqual(client.budget.settled_attempts, 1)
                self.assertEqual(client.budget.snapshot()["uncertain_credit_reservations"], 0)
                self.assertIsNone(client.budget.snapshot()["pending_ticket"])
                _, answer = self.invoke(FakeServer(), client)
                self.assertEqual(answer, {"inspect": True})
                self.assertEqual(client.budget.settled_attempts, 2)
                self.assertNotIn("response_status", client.last_metadata)

    def test_invalid_json_with_missing_usage_still_stops_with_uncertain_reservation(self):
        events = successful_events()
        events[0]["params"]["item"]["text"] = "{"
        del events[1]["params"]["tokenUsage"]["total"]["outputTokens"]
        client = make_client()
        with self.assertRaises(InvalidUsage):
            self.invoke(FakeServer(events=events), client)
        self.assertTrue(client.stopped)
        self.assertEqual(client.budget.committed, PER_ATTEMPT_RESERVATION)
        self.assertEqual(client.budget.failed_attempts, 1)
        self.assertEqual(client.budget.settled_attempts, 0)
        self.assertNotIn("response_status", client.last_metadata)

    def test_both_runners_keep_invalid_json_in_denominator_and_continue_without_retry(self):
        from run_development_pilot import execute as execute_development
        from run_revision_diagnostic import execute as execute_revision

        for execute, response in ((execute_development, '{"inspect":true}'),
                                  (execute_revision, '{"keys":["job-0","job-1"]}')):
            with self.subTest(runner=execute.__module__):
                client = make_client()
                servers = []
                for text in ("{", response):
                    events = successful_events()
                    events[0]["params"]["item"]["text"] = text
                    server = FakeServer(events=events)
                    server.client = client
                    servers.append(server)
                with patch("luna_appserver.AppServer", side_effect=servers) as factory:
                    summary, ledger = execute(client, fake=True, cap=2)
                rows = ledger.rows if hasattr(ledger, "rows") else ledger
                self.assertEqual(factory.call_count, 2)
                self.assertEqual([row["status"] for row in rows], ["policy_failure", "completed"])
                self.assertEqual(rows[0]["error_type"], "ResponseFormatError")
                self.assertIsNone(rows[0]["response"])
                # Development intentionally repeats identical calibration
                # requests; advancing the scheduled case distinguishes that
                # planned replication from a retry of the failed case.
                case_field = "evaluator_id" if "evaluator_id" in rows[0] else "case_id"
                self.assertNotEqual(rows[0][case_field], rows[1][case_field])
                self.assertEqual(summary["attempt_status_counts"]["transport_failure"], 0)
                self.assertEqual(client.budget.settled_attempts, 2)
                self.assertFalse(client.stopped)
                for row in rows:
                    self.assertEqual(row["provider_metadata"]["credit_accounting"]["status"], "settled")
                if "rows" in summary:
                    self.assertEqual(len(summary["rows"]), 24)
                    self.assertEqual(sum(row["scheduled"] for row in summary["by_rule"]), 24)
                    self.assertEqual([row["status"] for row in summary["rows"][:2]],
                                     ["policy_failure", "completed"])
                else:
                    self.assertEqual((len(summary["stage_a"]), len(summary["stage_b"])), (12, 36))
                    self.assertEqual([row["status"] for row in summary["stage_a"][:2]],
                                     ["policy_failure", "completed"])

    def test_missing_one_generation_guard_stop_is_rejected(self):
        self.assert_failed_reserved(FakeServer(events=successful_events(controlled_stop=False)))

    def test_unrelated_provider_failure_is_not_a_controlled_stop(self):
        events = successful_events()
        events.insert(0, event("error", error={"codexErrorInfo": "streamDisconnected"}, willRetry=False))
        self.assert_failed_reserved(FakeServer(events=events))

    def test_controlled_stop_without_completed_answer_or_usage_is_rejected(self):
        base = successful_events()
        for method in ("item/completed", "thread/tokenUsage/updated"):
            with self.subTest(missing=method):
                self.assert_failed_reserved(FakeServer(events=[e for e in base if e["method"] != method]))

    def test_zero_input_cannot_release_a_nonempty_request_reservation(self):
        events = successful_events()
        value = {"inputTokens": 0, "cachedInputTokens": 0, "outputTokens": 40,
                 "reasoningOutputTokens": 20, "totalTokens": 40}
        events[1]["params"]["tokenUsage"] = {"total": value, "last": value}
        self.assert_failed_reserved(FakeServer(events=events))

    def test_missing_usage_counter_is_not_silently_replaced_with_zero(self):
        for field in ("cachedInputTokens", "outputTokens", "reasoningOutputTokens"):
            with self.subTest(field=field):
                events = successful_events()
                del events[1]["params"]["tokenUsage"]["total"][field]
                client = make_client()
                with self.assertRaises((InvalidUsage, TransportError)):
                    self.invoke(FakeServer(events=events), client)
                self.assertTrue(client.stopped)
                self.assertEqual(client.budget.committed, PER_ATTEMPT_RESERVATION)
                self.assertEqual(client.budget.failed_attempts, 1)

    def test_rerouted_model_is_rejected_before_credit_release(self):
        events = [event("model/rerouted", fromModel=MODEL, toModel="different-model"), *successful_events()]
        self.assert_failed_reserved(FakeServer(events=events))

    def test_wrong_turn_in_usage_or_completion_is_rejected(self):
        cases = []
        events = successful_events()
        events[1]["params"]["turnId"] = "other-turn"
        cases.append(events)
        events = successful_events()
        events[-1]["params"]["turn"]["id"] = "other-turn"
        cases.append(events)
        for events in cases:
            with self.subTest(events=events):
                self.assert_failed_reserved(FakeServer(events=events))

    def test_wrong_thread_is_rejected(self):
        events = successful_events()
        events[1]["params"]["threadId"] = "other-thread"
        self.assert_failed_reserved(FakeServer(events=events))

    def test_tool_item_stops_batch_with_full_reservation(self):
        events = [event("item/started", item={"type": "mcpToolCall", "id": "unexpected-tool"}), *successful_events()]
        client = self.assert_failed_reserved(FakeServer(events=events))
        with patch("luna_appserver.AppServer") as factory, self.assertRaises(TransportError):
            client.complete(self.request)
        factory.assert_not_called()

    def test_missing_quota_rpc_after_completion_stops_future_calls(self):
        server = FakeServer(after_error=TransportError("quota_after_unavailable"))
        client = make_client()
        with self.assertRaises(TransportError):
            self.invoke(server, client)
        self.assertEqual(client.budget.settled_attempts, 1)
        self.assertTrue(client.stopped)
        with patch("luna_appserver.AppServer") as factory, self.assertRaises(TransportError):
            client.complete(self.request)
        factory.assert_not_called()

    def test_empty_quota_after_completion_stops_future_calls(self):
        server = FakeServer(after={})
        client = make_client()
        with self.assertRaises(TransportError):
            self.invoke(server, client)
        self.assertTrue(client.stopped)

    def test_api_key_authentication_never_dispatches(self):
        server = FakeServer(auth="apiKey")
        client = make_client()
        with self.assertRaises(TransportError):
            self.invoke(server, client)
        self.assertEqual(client.budget.attempts, 0)
        self.assertFalse(any(method == "turn/start" for method, _ in server.calls))
        self.assertTrue(server.closed)

    def test_empty_or_eighty_percent_quota_never_dispatches(self):
        for before in ({}, limits(80), limits(100)):
            with self.subTest(before=before):
                server = FakeServer(before=before)
                client = make_client()
                with self.assertRaises(TransportError):
                    self.invoke(server, client)
                self.assertEqual(client.budget.attempts, 0)
                self.assertFalse(any(method == "turn/start" for method, _ in server.calls))

    def test_transfer_quota_policy_allows_85_but_stops_at_100(self):
        # The default remains conservative for the historical runners.
        with self.assertRaisesRegex(TransportError, "quota_guard_80_percent"):
            check_quota(quota_snapshot(limits(85)))
        client = make_client()
        client.quota_used_limit = 100
        _, answer = self.invoke(FakeServer(before=limits(85), after=limits(86)), client)
        self.assertEqual(answer, {"inspect": True})
        self.assertEqual(client.budget.settled_attempts, 1)
        self.assertEqual(client.last_metadata["quota_guard_used_percent"], 100)
        self.assertEqual(client.last_metadata["quota_before"]["codex"]["primary"]["usedPercent"], 85)
        self.assertEqual(client.last_metadata["quota_after"]["codex"]["primary"]["usedPercent"], 86)
        client = make_client()
        client.quota_used_limit = 100
        server = FakeServer(before=limits(100))
        with self.assertRaisesRegex(TransportError, "quota_guard_100_percent"):
            self.invoke(server, client)
        self.assertEqual(client.budget.attempts, 0)
        self.assertEqual(client.last_metadata["quota_before"]["codex"]["primary"]["usedPercent"], 100)
        self.assertFalse(any(method == "turn/start" for method, _ in server.calls))

    def test_quota_failure_snapshots_survive_before_and_after_checks(self):
        before_client = make_client()
        with self.assertRaises(TransportError):
            self.invoke(FakeServer(before=limits(85)), before_client)
        self.assertEqual(before_client.last_metadata["quota_before"]["codex"]["primary"]["usedPercent"], 85)
        after_client = make_client()
        after_client.quota_used_limit = 100
        with self.assertRaises(TransportError):
            self.invoke(FakeServer(before=limits(85), after=limits(100)), after_client)
        self.assertEqual(after_client.budget.settled_attempts, 1)
        self.assertEqual(after_client.last_metadata["quota_after"]["codex"]["primary"]["usedPercent"], 100)
        self.assertTrue(after_client.stopped)

    def test_new_quota_policy_keeps_provider_denials_and_rejects_unreviewed_limits(self):
        for fields in ({"rateLimitReachedType": "rate_limit_reached"},
                       {"spendControlReached": True},
                       {"individualLimit": {"remainingPercent": 0}}):
            with self.subTest(fields=fields), self.assertRaises(TransportError):
                check_quota(quota_snapshot(limits(85, **fields)), used_limit=100)
        for used_limit in (True, 0, 79, 81, 101, 100.0, "100", None):
            with self.subTest(used_limit=used_limit), self.assertRaises(ValueError):
                check_quota(quota_snapshot(limits(85)), used_limit=used_limit)
            with self.assertRaises(ValueError):
                LunaClient("never-read.exe", {}, quota_used_limit=used_limit)
        denied = limits(85)
        denied["ordinaryUsageAllowed"] = False
        client = make_client()
        client.quota_used_limit = 100
        with self.assertRaisesRegex(TransportError, "ordinary_usage_not_allowed"):
            self.invoke(FakeServer(before=denied), client)
        self.assertEqual(client.budget.attempts, 0)

    def test_reached_provider_limit_overrides_low_window_percentage(self):
        for fields in ({"rateLimitReachedType": "rate_limit_reached"},
                       {"spendControlReached": True},
                       {"individualLimit": {"remainingPercent": 0}}):
            with self.subTest(fields=fields), self.assertRaises(TransportError):
                check_quota(quota_snapshot(limits(20, **fields)))

    def test_explicit_ordinary_usage_denial_never_dispatches(self):
        before = limits()
        before["ordinaryUsageAllowed"] = False
        server = FakeServer(before=before)
        client = make_client()
        with self.assertRaises(TransportError):
            self.invoke(server, client)
        self.assertEqual(client.budget.attempts, 0)

    def test_provider_retry_or_endpoint_change_never_dispatches(self):
        for name, value in (("request_max_retries", 1), ("stream_max_retries", 1),
                            ("base_url", "https://example.invalid"), ("requires_openai_auth", False)):
            with self.subTest(name=name):
                server = FakeServer(config_change=lambda c, key=name, val=value:
                                    c["model_providers"][PROVIDER].update({key: val}))
                client = make_client()
                with self.assertRaises(TransportError):
                    self.invoke(server, client)
                self.assertEqual(client.budget.attempts, 0)

    def test_effective_isolation_drift_never_dispatches(self):
        changes = [
            lambda config: config["features"].update(shell_tool=True),
            lambda config: config["features"]["rollout_budget"].update(enabled=False),
            lambda config: config["features"]["rollout_budget"].update(prefill_token_weight=1),
            lambda config: config["mcp_servers"].update(extra={"enabled": True}),
        ]
        for change in changes:
            with self.subTest(change=change):
                server = FakeServer(config_change=change)
                client = make_client()
                with self.assertRaises((ValueError, TransportError)):
                    self.invoke(server, client)
                self.assertEqual(client.budget.attempts, 0)
                self.assertFalse(any(method == "turn/start" for method, _ in server.calls))


if __name__ == "__main__":
    unittest.main()
