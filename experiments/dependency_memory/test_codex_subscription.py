"""No model, account, network, or installed CLI required by these tests."""

import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import codex_subscription as subscription


def events(response=None, usage=None):
    return [
        {"type": "thread.started", "thread_id": "synthetic-thread"},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"id": "synthetic-item", "type": "agent_message", "text": json.dumps(response or {"inspect": True})}},
        {"type": "turn.completed", "usage": usage or {"input_tokens": 80, "cached_input_tokens": 20, "output_tokens": 10, "reasoning_output_tokens": 6}},
    ]


def encoded(value):
    return "\n".join(json.dumps(row) for row in value)


class SubscriptionGateTests(unittest.TestCase):
    def test_preparation_uses_only_canonical_public_stdin_and_no_resume(self):
        from artifact_workflow import Config
        from pilot_interface import inspection_request, request_bytes

        request = inspection_request(Config(recovery_available=True))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scratch = root / "empty"
            scratch.mkdir()
            schema = root / "schema.json"
            schema.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "schema must match"):
                subscription.prepare_request(request, executable="codex", empty_cwd=str(scratch), output_schema=str(schema))
            schema.write_text(json.dumps(request["response_schema"]), encoding="utf-8")
            prepared = subscription.prepare_request(request, executable="codex", empty_cwd=str(scratch), output_schema=str(schema))
            self.assertEqual(prepared.stdin, request_bytes(request))
            self.assertFalse(prepared.launch_ready)
            for flag in ("--ephemeral", "--ignore-user-config", "--strict-config", "--ignore-rules"):
                self.assertIn(flag, prepared.command)
            self.assertNotIn("resume", prepared.command)
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", prepared.command)
            self.assertEqual(prepared.command[-1], "-")
            with self.assertRaises(ValueError):
                subscription.prepare_request(request, executable="codex", empty_cwd=str(scratch), output_schema=str(schema), max_input_bytes=1)
            (scratch / "private.txt").write_text("synthetic forbidden evaluator state", encoding="utf-8")
            with self.assertRaises(ValueError):
                subscription.prepare_request(request, executable="codex", empty_cwd=str(scratch), output_schema=str(schema))

    def test_complete_cannot_dispatch_even_with_valid_credentials_or_bad_input(self):
        client = subscription.CodexSubscriptionClient(executable="codex")
        with patch.object(subprocess, "run", side_effect=AssertionError("No dispatch allowed")):
            with self.assertRaises(subscription.SubscriptionNotReady):
                client.complete({"private": "Never forwarded"})
        self.assertFalse(client.last_metadata["dispatched"])
        self.assertEqual(client.last_metadata["provider_request_count"], 0)
        self.assertNotIn("private", json.dumps(client.last_metadata))

    def test_contract_does_not_equate_subscription_with_free_or_api_prices(self):
        contract = subscription.contract()
        self.assertFalse(contract["launch_ready"])
        self.assertFalse(contract["api_key_fallback"])
        self.assertFalse(contract["subscription_credits_are_free"])
        self.assertIsNone(contract["subscription_charge_bound"])
        self.assertIsNone(contract["provider_retries"])
        self.assertEqual(contract["development_request_ceiling"], 96)
        self.assertEqual(contract["model"], "gpt-5.6-luna")

    def test_login_probe_returns_only_classification_not_auth_output(self):
        replies = iter([
            SimpleNamespace(stdout=subscription.REVIEWED_CLI_VERSION, stderr="", returncode=0),
            SimpleNamespace(stdout="", stderr="Logged in using ChatGPT", returncode=0),
        ])
        calls = []
        def runner(args, **kwargs):
            calls.append(args)
            return next(replies)
        report = subscription.inspect_installation("not-a-real-executable", check_auth=True, runner=runner)
        self.assertEqual(report["authentication"], "chatgpt")
        self.assertFalse(report["launch_ready"])
        self.assertEqual(calls, [["not-a-real-executable", "--version"], ["not-a-real-executable", "login", "status"]])

    def test_api_key_probe_never_echoes_key_or_switches_to_api(self):
        secret = "SYNTHETIC-SECRET-DO-NOT-LOG"
        replies = iter([
            SimpleNamespace(stdout=subscription.REVIEWED_CLI_VERSION, stderr="", returncode=0),
            SimpleNamespace(stdout="Logged in using an API key: " + secret, stderr="", returncode=0),
        ])
        report = subscription.inspect_installation("none", check_auth=True, runner=lambda *a, **k: next(replies))
        self.assertEqual(report["authentication"], "api_key_not_authorized_for_this_adapter")
        self.assertNotIn(secret, json.dumps(report))

    def test_sandbox_home_failure_is_unverified_not_failed_login(self):
        replies = iter([
            SimpleNamespace(stdout=subscription.REVIEWED_CLI_VERSION, stderr="", returncode=0),
            SimpleNamespace(stdout="", stderr="Could not find home directory", returncode=1),
        ])
        report = subscription.inspect_installation("none", check_auth=True, runner=lambda *a, **k: next(replies))
        self.assertEqual(report["authentication"], "unverified")


class SubscriptionEventTests(unittest.TestCase):
    def test_usage_preserves_overlap_and_unknown_subscription_charge(self):
        response, metadata = subscription.parse_events(encoded(events()))
        self.assertEqual(response, {"inspect": True})
        self.assertEqual(metadata["usage"]["output_tokens"], 10)
        self.assertEqual(metadata["usage"]["reasoning_output_tokens"], 6)
        self.assertEqual(metadata["usage"]["input_tokens"], 80)
        self.assertIsNone(metadata["charged_dollars"])
        self.assertIsNone(metadata["provider_request_count"])

    def test_every_tool_and_unknown_item_is_quarantined(self):
        for kind in ("command_execution", "file_change", "mcp_tool_call", "web_search", "plan", "unknown_future_tool"):
            with self.subTest(kind=kind):
                stream = events()
                stream.insert(2, {"type": "item.started", "item": {"type": kind}})
                with self.assertRaises(subscription.InvalidCodexOutput):
                    subscription.parse_events(encoded(stream))

    def test_failures_and_multi_turn_runs_cannot_masquerade_as_one_request(self):
        for extra in ({"type": "turn.started"}, {"type": "error"}, {"type": "turn.failed"}, {"type": "thread.started", "thread_id": "second"}):
            with self.subTest(extra=extra):
                with self.assertRaises(subscription.InvalidCodexOutput):
                    subscription.parse_events(encoded(events() + [extra]))

    def test_rejects_bad_usage_missing_reply_and_duplicate_json_keys(self):
        for usage in (
            {"input_tokens": 3, "cached_input_tokens": 4, "output_tokens": 1},
            {"input_tokens": True, "cached_input_tokens": 0, "output_tokens": 1},
            {"input_tokens": 3, "cached_input_tokens": 0, "output_tokens": -1},
        ):
            with self.subTest(usage=usage):
                with self.assertRaises(subscription.InvalidCodexOutput):
                    subscription.parse_events(encoded(events(usage=usage)))
        with self.assertRaises(subscription.InvalidCodexOutput):
            subscription.parse_events(encoded(events()[:2]))
        stream = events()
        stream[2]["item"]["text"] = '{"inspect":true,"inspect":false}'
        with self.assertRaises(subscription.InvalidCodexOutput):
            subscription.parse_events(encoded(stream))
        stream[2]["item"]["text"] = '{"inspect":NaN}'
        with self.assertRaises(subscription.InvalidCodexOutput):
            subscription.parse_events(encoded(stream))


if __name__ == "__main__":
    unittest.main()
