import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from backend.applicability_engine import check_applicability, evaluate_rule
from backend.models import BusinessProfile
from backend.monitor import run_monitor_cycle
from backend import config
from backend.storage import load

class ApplicabilityTests(unittest.TestCase):
    def test_all_conditions_and_explanation(self):
        rule = {"rule_id":"r1","obligation_name":"ESI","turnover_min":100, "turnover_max":500, "headcount_min":10, "sector":"Manufacturing", "state":"Haryana", "entity_type":None}
        yes = evaluate_rule(rule, {"turnover":200,"headcount":10,"sector":"manufacturing","state":"hARYANA"})
        no = evaluate_rule(rule, {"turnover":99,"headcount":5,"sector":"services","state":"Delhi"})
        self.assertTrue(yes["applicable"]); self.assertIn("headcount", yes["matched_conditions"])
        self.assertFalse(no["applicable"]); self.assertIn("turnover", no["failed_conditions"])

    def test_null_conditions_do_not_restrict(self):
        self.assertTrue(evaluate_rule({"rule_id":"r","obligation_name":"General"}, {})["applicable"])

class ReviewBoundaryTests(unittest.TestCase):
    def test_engine_reads_only_live_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rules.json"; path.write_text(json.dumps([{"rule_id":"r","obligation_name":"X","headcount_min":2}]))
            result = check_applicability({"headcount":2}, path)
            self.assertEqual(len(result["applicable_obligations"]), 1)

class MonitorTests(unittest.TestCase):
    def test_baseline_then_unchanged_skips_ai(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); original = {k: getattr(config, k) for k in ("STATE_PATH", "QUEUE_PATH", "AUDIT_PATH", "SNAPSHOTS_DIR", "DOCUMENTS_DIR")}
            try:
                config.STATE_PATH, config.QUEUE_PATH, config.AUDIT_PATH = root/'state.json', root/'queue.json', root/'audit.json'
                config.SNAPSHOTS_DIR, config.DOCUMENTS_DIR = root/'snapshots', root/'documents'; config.SNAPSHOTS_DIR.mkdir()
                source = {"source_id":"s", "url":"https://example.test", "active":True}
                with patch('backend.monitor.fetch_source', return_value={'raw_content':'Notice A'}), patch('backend.monitor.detect_new_regulatory_entries') as detector:
                    run_monitor_cycle(sources=[source]); result = run_monitor_cycle(sources=[source])
                self.assertEqual(result['ai_calls'], 0); detector.assert_not_called()
            finally:
                for key, value in original.items(): setattr(config, key, value)

if __name__ == "__main__": unittest.main()
