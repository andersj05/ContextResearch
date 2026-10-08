"""Semantic tamper probes over copies of completed live evidence; no model calls."""
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from ..controller import write_new
from ..records import digest, wire
from ..subscription.accounting import Ledger
from ..cohort_v1.analysis import analyze, markdown
from ..cohort_v1.run import read, lines, seal
from .verify import verify


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configured=os.environ.get("ROLLBACK_SUBSCRIPTION_EVIDENCE")
        root=Path(__file__).resolve().parents[4]
        cls.archive=(Path(configured) if configured else root/"experiments/dependency_memory/results/rollback_subscription_2026-10-08/pilot_authored_v1").resolve()
        if not (cls.archive/"evidence_manifest.json").is_file():
            raise unittest.SkipTest("requires separately completed live archive; never dispatches a model")

    def copy(self):
        root=Path(__file__).resolve().parents[4]/"tmp"/"rollback_evidence_checks"
        root.mkdir(parents=True,exist_ok=True)
        temp=tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(temp.cleanup)
        target=Path(temp.name)/"copy"
        shutil.copytree(self.archive,target)
        return target

    @staticmethod
    def rewrite(path,value):
        Path(path).write_text(wire(value)+"\n",encoding="utf-8",newline="\n")

    @staticmethod
    def reseal(folder):
        (folder/"evidence_manifest.json").unlink()
        seal(folder)

    @staticmethod
    def export_and_analyze(folder):
        ledger=Ledger(folder/"ledger.sqlite",max_calls=312)
        try:
            (folder/"usage_events.jsonl").write_text("".join(wire(x)+"\n" for x in ledger.events()),encoding="utf-8",newline="\n")
            EvidenceTests.rewrite(folder/"accounting.json",ledger.summary())
            result=analyze(lines(folder/"tasks.jsonl"),ledger.events())
            EvidenceTests.rewrite(folder/"analysis.json",result)
            (folder/"report.md").write_text(markdown(result),encoding="utf-8",newline="\n")
        finally:ledger.close()

    def test_complete_live_archive_verifies(self):
        result=verify(self.archive)
        self.assertEqual(result["verified_tasks"],24)
        self.assertEqual(result["verified_possible_slots"],312)

    def test_erased_task_rejected_after_resealing(self):
        folder=self.copy()
        rows=lines(folder/"tasks.jsonl")[:-1]
        (folder/"tasks.jsonl").write_text("".join(wire(x)+"\n" for x in rows),encoding="utf-8",newline="\n")
        self.reseal(folder)
        with self.assertRaisesRegex(ValueError,"selected tasks omitted"):
            verify(folder)

    def test_lost_skipped_slot_rejected_after_resealing(self):
        folder=self.copy()
        rows=lines(folder/"slot_dispositions.jsonl")
        self.assertTrue(any(x["dispatch_state"]=="not_dispatched" for x in rows))
        remove=next(i for i,x in enumerate(rows) if x["dispatch_state"]=="not_dispatched")
        rows.pop(remove)
        (folder/"slot_dispositions.jsonl").write_text("".join(wire(x)+"\n" for x in rows),encoding="utf-8",newline="\n")
        self.reseal(folder)
        with self.assertRaisesRegex(ValueError,"slot dispositions"):
            verify(folder)

    def test_shared_thread_rejected_with_consistent_export_and_response(self):
        folder=self.copy()
        connection=sqlite3.connect(folder/"ledger.sqlite")
        from ..records import strict_loads
        records=connection.execute("SELECT call_id,payload FROM events WHERE state='completed' ORDER BY seq LIMIT 2").fetchall()
        self.assertEqual(len(records),2)
        first,second=(strict_loads(x[1]) for x in records)
        second["metadata"]["thread_id"]=first["metadata"]["thread_id"]
        connection.execute("UPDATE events SET payload=? WHERE call_id=? AND state='completed'",(wire(second),records[1][0]));connection.commit();connection.close()
        response_path=folder/"responses"/(records[1][0]+".json")
        response=read(response_path);response["metadata"]=second["metadata"];self.rewrite(response_path,response)
        self.export_and_analyze(folder);self.reseal(folder)
        with self.assertRaisesRegex(ValueError,"shared continuity"):
            verify(folder)

    def test_private_payload_rejected_even_with_rebound_request_hash(self):
        folder=self.copy()
        connection=sqlite3.connect(folder/"ledger.sqlite")
        from ..records import strict_loads
        key,payload=connection.execute("SELECT call_id,payload FROM events WHERE state='planned' ORDER BY seq LIMIT 1").fetchone()
        path=folder/"requests"/(key+".json")
        request=read(path)
        content=strict_loads(request["messages"][1]["content"])
        content["private_tests"]=[{"input":"hidden","output":"answer"}]
        request["messages"][1]["content"]=wire(content)
        self.rewrite(path,request)
        plan=strict_loads(payload);plan["request_hash"]=digest(wire(request))
        connection.execute("UPDATE events SET payload=? WHERE call_id=? AND state='planned'",(wire(plan),key));connection.commit();connection.close()
        self.export_and_analyze(folder);self.reseal(folder)
        with self.assertRaisesRegex(ValueError,"canonical input"):
            verify(folder)

    def test_inconsistent_coding_success_rejected_after_resealing(self):
        folder=self.copy()
        grades=read(folder/"coding_grades.json")
        self.assertTrue(grades)
        grades[0]["grade"]["tests"]=grades[0]["grade"]["tests"][:-1]
        grades[0]["grade"]["score"]=1
        grades[0]["grade"]["disposition"]="correct"
        self.rewrite(folder/"coding_grades.json",grades);self.reseal(folder)
        with self.assertRaisesRegex(ValueError,"coding score"):
            verify(folder)


if __name__=="__main__":unittest.main()
