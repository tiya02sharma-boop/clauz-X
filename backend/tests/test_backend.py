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

    def test_composite_msme_classification_micro(self):
        # Both within Micro thresholds -> Micro
        p1 = BusinessProfile(investment_plant_machinery=25_000_000, turnover=100_000_000)
        self.assertEqual(p1.msme_classification, "Micro")
        p2 = BusinessProfile(investment_plant_machinery=10_000_000, turnover=40_000_000)
        self.assertEqual(p2.msme_classification, "Micro")

    def test_composite_msme_classification_either_exceeds_not_micro(self):
        # Investment exceeds 2.5 Cr -> cannot be Micro (composite AND, not OR)
        p_inv_exceeds = BusinessProfile(investment_plant_machinery=25_000_001, turnover=50_000_000)
        self.assertNotEqual(p_inv_exceeds.msme_classification, "Micro")
        self.assertEqual(p_inv_exceeds.msme_classification, "Small")

        # Turnover exceeds 10 Cr -> cannot be Micro (composite AND, not OR)
        p_to_exceeds = BusinessProfile(investment_plant_machinery=10_000_000, turnover=100_000_001)
        self.assertNotEqual(p_to_exceeds.msme_classification, "Micro")
        self.assertEqual(p_to_exceeds.msme_classification, "Small")

        # Both exceed Micro thresholds -> cannot be Micro
        p_both_exceed = BusinessProfile(investment_plant_machinery=30_000_000, turnover=150_000_000)
        self.assertNotEqual(p_both_exceed.msme_classification, "Micro")
        self.assertEqual(p_both_exceed.msme_classification, "Small")

    def test_composite_msme_classification_tiers_and_above(self):
        # Small enterprise: inv <= 25 Cr AND turnover <= 100 Cr
        small = BusinessProfile(investment_plant_machinery=250_000_000, turnover=1_000_000_000)
        self.assertEqual(small.msme_classification, "Small")

        # Exceeds Small investment threshold -> Medium
        medium_by_inv = BusinessProfile(investment_plant_machinery=250_000_001, turnover=500_000_000)
        self.assertEqual(medium_by_inv.msme_classification, "Medium")

        # Medium enterprise: inv <= 125 Cr AND turnover <= 500 Cr
        medium = BusinessProfile(investment_plant_machinery=1_250_000_000, turnover=5_000_000_000)
        self.assertEqual(medium.msme_classification, "Medium")

        # Above Medium thresholds -> Not MSME
        not_msme_inv = BusinessProfile(investment_plant_machinery=1_250_000_001, turnover=100_000_000)
        self.assertEqual(not_msme_inv.msme_classification, "Not MSME")

        not_msme_to = BusinessProfile(investment_plant_machinery=50_000_000, turnover=5_000_000_001)
        self.assertEqual(not_msme_to.msme_classification, "Not MSME")

    def test_factory_vs_shops_establishments_routing(self):
        factory_rule = {
            "rule_id": "rule_factories_act_registration",
            "obligation_name": "Factories Act Registration",
            "requires_is_factory": True
        }
        shops_rule = {
            "rule_id": "rule_shops_establishments_registration",
            "obligation_name": "Shops & Establishments Registration",
            "requires_is_factory": False
        }

        # is_factory = True matches Factories Act and does NOT match Shops & Establishments
        factory_biz = BusinessProfile(is_factory=True, turnover=10_000_000, investment_plant_machinery=5_000_000)
        eval_factory_on_factory = evaluate_rule(factory_rule, factory_biz)
        eval_shops_on_factory = evaluate_rule(shops_rule, factory_biz)

        self.assertTrue(eval_factory_on_factory["applicable"])
        self.assertIn("Applies because your business operates as a factory under the Factories Act, not a commercial establishment.", eval_factory_on_factory["reason"])
        self.assertFalse(eval_shops_on_factory["applicable"])
        self.assertIn("Does not apply because your business operates as a factory, not a commercial establishment.", eval_shops_on_factory["reason"])

        # is_factory = False matches Shops & Establishments and does NOT match Factories Act
        commercial_biz = BusinessProfile(is_factory=False, turnover=10_000_000, investment_plant_machinery=5_000_000)
        eval_factory_on_comm = evaluate_rule(factory_rule, commercial_biz)
        eval_shops_on_comm = evaluate_rule(shops_rule, commercial_biz)

        self.assertFalse(eval_factory_on_comm["applicable"])
        self.assertIn("Does not apply because your business does not operate as a factory under the Factories Act.", eval_factory_on_comm["reason"])
        self.assertTrue(eval_shops_on_comm["applicable"])
        self.assertIn("Applies because your business operates as a commercial establishment under the Shops and Establishments Act, not a factory.", eval_shops_on_comm["reason"])

    def test_existing_obligations_no_regression(self):
        # A rule with no investment or factory constraint continues to match regardless of is_factory / investment
        generic_rule = {"rule_id": "r_gen", "obligation_name": "General Tax", "turnover_min": 1000}
        
        biz_factory = {"turnover": 5000, "is_factory": True, "investment_plant_machinery": 2000000}
        biz_non_factory = {"turnover": 5000, "is_factory": False, "investment_plant_machinery": 500000}
        biz_no_new_fields = {"turnover": 5000}

        self.assertTrue(evaluate_rule(generic_rule, biz_factory)["applicable"])
        self.assertTrue(evaluate_rule(generic_rule, biz_non_factory)["applicable"])
        self.assertTrue(evaluate_rule(generic_rule, biz_no_new_fields)["applicable"])

    def test_investment_min_max_rule_matching(self):
        rule = {"rule_id": "r_inv", "investment_min": 1_000_000, "investment_max": 5_000_000}
        
        # Matches within bounds
        self.assertTrue(evaluate_rule(rule, {"investment_plant_machinery": 2_500_000})["applicable"])
        # Fails below min
        self.assertFalse(evaluate_rule(rule, {"investment_plant_machinery": 500_000})["applicable"])
        # Fails above max
        self.assertFalse(evaluate_rule(rule, {"investment_plant_machinery": 6_000_000})["applicable"])


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

    def test_changed_website_notice_creates_candidate_without_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); original = {k: getattr(config, k) for k in ("STATE_PATH", "QUEUE_PATH", "AUDIT_PATH", "SNAPSHOTS_DIR", "DOCUMENTS_DIR")}
            try:
                config.STATE_PATH, config.QUEUE_PATH, config.AUDIT_PATH = root/'state.json', root/'queue.json', root/'audit.json'
                config.SNAPSHOTS_DIR, config.DOCUMENTS_DIR = root/'snapshots', root/'documents'; config.SNAPSHOTS_DIR.mkdir()
                source = {"source_id":"s", "url":"https://example.test/notices", "active":True}
                candidate = {"obligation_name":"GST return", "source_citation":"Notice 1", "extraction_method":"gemini", "simulated":False, "fields_needing_human_verification":[]}
                with patch('backend.monitor.fetch_source', side_effect=[{'raw_content':'old'}, {'raw_content':'new'}]), \
                     patch('backend.monitor.detect_new_regulatory_entries', return_value=[{"title":"Notice 1", "summary":"GST return due date changes", "source_url":"/notice-1"}]), \
                     patch('backend.monitor.call_gemini_extraction', return_value=candidate):
                    run_monitor_cycle(sources=[source]); result = run_monitor_cycle(sources=[source])
                self.assertEqual(result['review_candidates_created'], 1)
                self.assertEqual(load(config.QUEUE_PATH, [])[0]['document']['source_url'], 'https://example.test/notice-1')
            finally:
                for key, value in original.items(): setattr(config, key, value)

if __name__ == "__main__": unittest.main()
