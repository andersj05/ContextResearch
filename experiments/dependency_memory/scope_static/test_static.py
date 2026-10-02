"""Independent program execution, closure cases and irreversible memory checks."""
from copy import deepcopy
from itertools import product
import json
import random
import unittest

from experiments.dependency_memory.scope_inference import codec, study
from experiments.dependency_memory.scope_static import infer, packing, run, targets
from experiments.dependency_memory.workflow_replay import evidence


def execute(source, entry, record, *arguments):
    namespace = {}
    exec(compile(source, "constructed_static_control_test", "exec"), namespace)
    try:
        return ["value", namespace[entry](deepcopy(record), *arguments)]
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        return ["error", type(error).__name__, str(error)]


def reconstructed(record, contract):
    public = packing.schema(contract)
    return packing.decode(packing.encode(record, contract, public), public)


class StaticScopeTests(unittest.TestCase):
    def test_aliases_and_helper_contexts_against_independent_generated_programs(self):
        rng = random.Random(2026100103)
        for _ in range(12):
            a, b, c = ["k" + str(rng.randrange(100000)) for _ in range(3)]
            source = (f"def field(box, key):\n    return box.get(key)\n"
                      f"def decide(record):\n    alias=record.get('{a}', {{}})\n"
                      f"    return (field(alias, '{b}'), '{c}' in alias, bool(alias))\n")
            contract = infer.infer(source, "decide", "record")["contract"]
            for present_b, present_c, other, value in product((False, True), (False, True), (False, True), (None, 0, [], {}, "x")):
                box = {}
                if present_b:
                    box[b] = value
                if present_c:
                    box[c] = {"large_unused_value": "z"}
                if other:
                    box["unrelated"] = 7
                record = {a: box, "outside": "unread"}
                self.assertEqual(execute(source, "decide", record), execute(source, "decide", reconstructed(record, contract)))
            self.assertNotIn("outside", codec.project({a: {}, "outside": 3}, contract))

    def test_branch_join_and_malformed_alias_types_preserve_outcomes(self):
        source = ("def decide(record):\n    if record.get('mode'):\n        alias=record.get('a')\n"
                  "    else:\n        alias=record.get('b')\n    return alias.get('value')\n")
        contract = infer.infer(source, "decide", "record")["contract"]
        shapes = (None, False, [], "text", {}, {"value": 0}, {"value": {"x": 1}}, {"unrelated": 1})
        for mode, a, b in product((None, False, True, {}, {"x": 1}), shapes, shapes):
            record = {"mode": mode, "a": a, "b": b, "unused": 19}
            self.assertEqual(execute(source, "decide", record), execute(source, "decide", reconstructed(record, contract)))

    def test_presence_truth_overlap_does_not_turn_empty_dict_into_true(self):
        source = "def decide(record):\n    data=record.get('data', {})\n    return ('items' in data, bool(data.get('items')))\n"
        contract = infer.infer(source, "decide", "record")["contract"]
        for row in ({}, {"data": {}}, *({"data": {"items": v}} for v in (None, False, [], {}, 0, "", {"unused": 1}, "x"))):
            self.assertEqual(execute(source, "decide", row), execute(source, "decide", reconstructed(row, contract)))
        self.assertEqual(execute(source, "decide", reconstructed({"data": {"items": {}}}, contract)), ["value", (True, False)])

    def test_unused_subscript_preserves_missing_key_exception(self):
        source = "def decide(record):\n    ignored=record['needed']\n    return True\n"
        contract = infer.infer(source, "decide", "record")["contract"]
        for row in ({}, {"needed": None}, {"needed": {}}, {"needed": False}, [], None):
            self.assertEqual(execute(source, "decide", row), execute(source, "decide", reconstructed(row, contract)))

    def test_late_key_retains_unannounced_values_without_root_noise(self):
        program = targets.programs()[-1]
        contract = infer.infer(program["source"], program["entry"], program["parameter"])["contract"]
        for key in ("never_in_catalog", "other", "absent"):
            record = {"values": {"never_in_catalog": 41, "other": {"exact": "value"}}, "noise": "unread"}
            projected = reconstructed(record, contract)
            self.assertEqual(targets.outcome(program, record, key), targets.outcome(program, projected, key))
            self.assertNotIn("noise", projected)

    def test_unrepresentable_keys_and_reserved_marker_keep_the_whole_base(self):
        for key in ("contains.dot", codec.MARKER):
            source = f"def decide(record):\n    return record.get('{key}')\n"
            result = infer.infer(source, "decide", "record")
            record = {key: {"x": 1}, "other": 8}
            self.assertEqual(execute(source, "decide", record), execute(source, "decide", reconstructed(record, result["contract"])))
            self.assertTrue(result["whole_input_fallback"])

    def test_unsupported_iteration_mutation_and_recursion_keep_whole_input(self):
        sources = ("def decide(record):\n    for x in record.values():\n        pass\n    return True\n",
                   "def decide(record):\n    record['changed']=1\n    return True\n",
                   "def decide(record):\n    return decide(record)\n",
                   "def decide(record):\n    return getattr(record, 'shape')\n")
        for source in sources:
            result = infer.infer(source, "decide", "record")
            self.assertTrue(result["whole_input_fallback"])
            self.assertTrue(result["issues"])

    def test_source_is_never_executed_and_record_data_is_not_an_argument(self):
        source = "raise RuntimeError('must not run')\ndef decide(record):\n    return record.get('x')\n"
        result = infer.infer(source, "decide", "record")
        self.assertEqual(codec.project({"x": 7, "unused": 8}, result["contract"]), {"x": 7})
        with self.assertRaises(ValueError):
            infer.infer(source, "decide", "record", public_arguments={"record": 7})

    def test_public_codec_roundtrip_and_fixed_schema_without_instance_values(self):
        contract = study.HAND
        public = packing.schema(contract)
        before = codec.wire(public)
        for row in study.control_catalog():
            self.assertEqual(reconstructed(row, contract), codec.project(row, contract))
        self.assertEqual(before, codec.wire(public))
        self.assertEqual(public, packing.schema({k:list(reversed(v)) for k,v in contract.items()}))

    def test_empty_memory_identity_and_duplicate_readout_have_no_source_fallback(self):
        program = targets.programs()[0]
        records, _ = evidence.load_snapshot()
        contract = infer.infer(program["source"], program["entry"], program["parameter"])["contract"]
        public = packing.schema(contract)
        row = records[0]
        self.assertEqual(run.child_rows("", (0, 1)), [])
        self.assertEqual(run.readout("", row["case_id"], row["request_sha256"], program, public), ["unknown", None, None])
        retained = {"case_id": row["case_id"], "worker": row["worker"], "request_sha256": row["request_sha256"],
                    "data": packing.encode(row, contract, public)}
        memory = codec.wire([retained]).decode()
        self.assertEqual(run.readout(memory, row["case_id"], row["request_sha256"], program, public), targets.outcome(program, row))
        self.assertEqual(run.readout(memory, row["case_id"], "0"*64, program, public), ["unknown", None, None])
        self.assertEqual(run.readout(codec.wire([retained,retained]).decode(), row["case_id"], row["request_sha256"], program, public), ["unknown", None, None])

    def test_saved_catalog_audit_uniform_codec_and_preserved_model_gap(self):
        fresh = run.analysis()
        saved = json.loads(run.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(run.stable(fresh), run.stable(saved))
        self.assertEqual(fresh["catalog_disagreements"], 0)
        self.assertEqual(fresh["new_model_calls"], 0)
        self.assertEqual(fresh["prospective_natural_episodes_added"], 0)
        self.assertEqual(fresh["permanent_missing_model_answers"], 1)
        self.assertEqual(len(fresh["historical_model_contracts_replayed"]), 7)
        self.assertTrue(all(p["catalog"]["expected_output_sha256"] == p["catalog"]["observed_output_sha256"] for p in fresh["programs"]))
        controls = fresh["dispatch_controls"]
        self.assertEqual((controls["static"]["correct"],controls["authored"]["correct"],controls["cached"]["correct"]), (24,24,24))
