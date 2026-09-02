"""Tests for Clauz X Compliance Calendar, Due Date Parser, and WhatsApp Reminders."""
from datetime import date
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from backend import config
from backend.app import app
from backend.calendar_service import compute_obligations_calendar, save_or_update_business
from backend.due_date_parser import calculate_next_due_date
from backend.models import BusinessProfile
from backend.reminder_scheduler import compose_reminder_message, run_reminder_cycle
from backend.storage import load, save
from backend.whatsapp_sender import (
    map_provider_error,
    normalize_whatsapp_number,
    send_whatsapp_message,
)


class DueDateParserTests(unittest.TestCase):
    def test_monthly_nth_following_month(self):
        # as_of = 2026-09-13. Rule = "20th of following month". Next due is 2026-09-20 (7 days away)
        due_date, needs_manual = calculate_next_due_date("20th of following month", "monthly", as_of="2026-09-13")
        self.assertEqual(due_date, "2026-09-20")
        self.assertFalse(needs_manual)

    def test_monthly_passed_rolls_to_next_month(self):
        # as_of = 2026-09-21. Rule = "20th of following month". Next due is 2026-10-20
        due_date, needs_manual = calculate_next_due_date("20th of following month", "monthly", as_of="2026-09-21")
        self.assertEqual(due_date, "2026-10-20")
        self.assertFalse(needs_manual)

    def test_monthly_various_phrasings(self):
        due1, _ = calculate_next_due_date("15th of next month", "monthly", as_of="2026-09-01")
        self.assertEqual(due1, "2026-09-15")

        due2, _ = calculate_next_due_date("7th of the following month", "monthly", as_of="2026-09-01")
        self.assertEqual(due2, "2026-09-07")

        due3, _ = calculate_next_due_date("By the 20th of every month", "monthly", as_of="2026-09-01")
        self.assertEqual(due3, "2026-09-20")

    def test_quarterly_following_month(self):
        # as_of = 2026-09-10. Q3 ends Sep 30, due Oct 30
        due_date, needs_manual = calculate_next_due_date("30th of following month", "quarterly", as_of="2026-09-10")
        self.assertEqual(due_date, "2026-10-30")
        self.assertFalse(needs_manual)

    def test_unparseable_rules_do_not_guess(self):
        # Criterion 2 part A: Never guess dates for unparseable rules
        unparseable_rules = [
            "Filing frequency and due date depend on the taxpayer's GST return scheme.",
            "Confirm the current statutory due date and establishment coverage before filing.",
            "Due dates are calculated from the company’s AGM and applicable statutory requirements.",
            "Within 30 days of incorporation",
            "Half-yearly by end of period",
        ]
        for rule_text in unparseable_rules:
            due_date, needs_manual = calculate_next_due_date(rule_text, "periodic", as_of="2026-09-13")
            self.assertIsNone(due_date, f"Expected None for unparseable rule: '{rule_text}', got: {due_date}")
            self.assertTrue(needs_manual, f"Expected needs_manual=True for: '{rule_text}'")

    def test_one_time_and_half_yearly_flag_manual_entry(self):
        due1, manual1 = calculate_next_due_date("20th of following month", "one_time", as_of="2026-09-13")
        self.assertIsNone(due1)
        self.assertTrue(manual1)

        due2, manual2 = calculate_next_due_date("20th of following month", "half_yearly", as_of="2026-09-13")
        self.assertIsNone(due2)
        self.assertTrue(manual2)


class WhatsAppSenderTests(unittest.TestCase):
    def setUp(self):
        self.patcher = patch.object(config, "WASENDER_API_KEY", None)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_missing_credentials_simulates_and_does_not_raise(self):
        # Criterion 3: Missing credentials logs simulated and does not raise
        result = send_whatsapp_message(
            to="+919876543210",
            message="Test message",
            account_sid=None,
            auth_token=None,
            from_number=None,
        )
        self.assertEqual(result.status, "simulated")
        self.assertTrue(result.sid.startswith("sim_"))
        self.assertIsNone(result.error_code)

    def test_invalid_phone_number_fails_gracefully(self):
        result = send_whatsapp_message(
            to="123",  # too short / invalid
            message="Test message",
            account_sid="test_sid",
            auth_token="test_token",
            from_number="+14155238886",
        )
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.error_code, "INVALID_NUMBER")

    def test_error_code_mappings(self):
        self.assertEqual(map_provider_error(21211), "INVALID_NUMBER")
        self.assertEqual(map_provider_error(63012), "INVALID_NUMBER")
        self.assertEqual(map_provider_error(63016), "TEMPLATE_REQUIRED")
        self.assertEqual(map_provider_error(63032), "TEMPLATE_REQUIRED")
        self.assertEqual(map_provider_error(63007), "RECIPIENT_NOT_OPTED_IN")
        self.assertEqual(map_provider_error(63015), "RECIPIENT_NOT_OPTED_IN")
        self.assertEqual(map_provider_error(50000), "WHATSAPP_SEND_FAILED")
        self.assertEqual(map_provider_error(None, "Template required outside 24-hour window"), "TEMPLATE_REQUIRED")

    def test_number_normalization(self):
        self.assertEqual(normalize_whatsapp_number("+91 98765 43210"), "whatsapp:+919876543210")
        self.assertEqual(normalize_whatsapp_number("9876543210"), "whatsapp:+919876543210")
        self.assertEqual(normalize_whatsapp_number("whatsapp:+14155552671"), "whatsapp:+14155552671")
        self.assertIsNone(normalize_whatsapp_number(None))
        self.assertIsNone(normalize_whatsapp_number(""))


class ReminderSchedulerAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.patcher = patch.object(config, "WASENDER_API_KEY", None)
        self.patcher.start()
        self.root = Path(self.tmp_dir.name)
        self.businesses_path = self.root / "businesses.json"
        self.reminders_path = self.root / "reminder_logs.json"
        self.rules_path = self.root / "rules.json"

        # Setup standard rules
        self.test_rules = [
            {
                "rule_id": "rule_gstr3b_monthly",
                "obligation_name": "GSTR-3B Monthly Return",
                "gst_registered": True,
                "recurrence": "monthly",
                "due_day_rule": "20th of following month",
                "penalty_formula": "₹50/day u/s 47 + 18% p.a. interest",
                "source_citation": "Section 39(1) of CGST Act, 2017",
            },
            {
                "rule_id": "rule_unparseable_scheme",
                "obligation_name": "Custom Scheme Filing",
                "gst_registered": True,
                "recurrence": "periodic",
                "due_day_rule": "Filing frequency and due date depend on taxpayer scheme.",
                "penalty_formula": None,
                "source_citation": "Scheme notification",
            },
        ]
        save(self.rules_path, self.test_rules)

        # Setup test business with whatsapp number
        self.test_business = {
            "business_id": "biz_test_001",
            "profile": {
                "business_name": "Acme MSME Tech Pvt Ltd",
                "gst_registered": True,
                "whatsapp_number": "+919876543210",
            },
        }
        save_or_update_business(
            self.test_business,
            as_of="2026-09-13",
            businesses_path=self.businesses_path,
            rules_path=self.rules_path,
        )

    def tearDown(self):
        self.patcher.stop()
        self.tmp_dir.cleanup()

    def test_acceptance_criterion_1_and_idempotency(self):
        """
        Acceptance Criterion 1:
        A monthly obligation due in exactly 7 days from as_of_date triggers exactly
        one reminder; running the cycle again on the same as_of_date sends zero
        additional reminders for that obligation+window.
        """
        # On 2026-09-13, GSTR-3B (due 2026-09-20) is exactly 7 days away
        first_run = run_reminder_cycle(
            as_of_date="2026-09-13",
            businesses_path=self.businesses_path,
            reminders_path=self.reminders_path,
            rules_path=self.rules_path,
        )

        self.assertEqual(first_run["candidates_found"], 1)
        self.assertEqual(first_run["reminders_simulated"] + first_run["reminders_sent"], 1)
        self.assertEqual(first_run["reminders_skipped_duplicate"], 0)

        logs_after_first = load(self.reminders_path, [])
        self.assertEqual(len(logs_after_first), 1)
        self.assertEqual(logs_after_first[0]["window"], 7)
        self.assertEqual(logs_after_first[0]["date"], "2026-09-13")
        self.assertEqual(logs_after_first[0]["obligation_id"], "rule_gstr3b_monthly")

        # Second run on the SAME as_of_date must skip duplicate and send ZERO additional reminders
        second_run = run_reminder_cycle(
            as_of_date="2026-09-13",
            businesses_path=self.businesses_path,
            reminders_path=self.reminders_path,
            rules_path=self.rules_path,
        )

        self.assertEqual(second_run["candidates_found"], 1)
        self.assertEqual(second_run["reminders_simulated"], 0)
        self.assertEqual(second_run["reminders_sent"], 0)
        self.assertEqual(second_run["reminders_skipped_duplicate"], 1)

        logs_after_second = load(self.reminders_path, [])
        self.assertEqual(len(logs_after_second), 1, "Must not create duplicate log entries on repeated run")

    def test_acceptance_criterion_2_unparseable_rules_never_appear_and_never_crash(self):
        """
        Acceptance Criterion 2:
        An obligation with an unparseable due_day_rule never appears in the
        reminder scheduler's candidate list and never crashes the cycle.
        """
        # Business with only unparseable obligations
        unparseable_biz = {
            "business_id": "biz_unparseable",
            "profile": {
                "business_name": "Unparseable Ltd",
                "gst_registered": True,
                "whatsapp_number": "+919876543211",
            },
        }
        # Only rule is unparseable
        rules_only_unparseable = [
            {
                "rule_id": "rule_unparseable_only",
                "obligation_name": "Manual Evaluation Needed",
                "gst_registered": True,
                "recurrence": "periodic",
                "due_day_rule": "Confirm current statutory due date before filing.",
            }
        ]
        unparseable_rules_path = self.root / "unparseable_rules.json"
        save(unparseable_rules_path, rules_only_unparseable)
        save_or_update_business(
            unparseable_biz,
            businesses_path=self.businesses_path,
            rules_path=unparseable_rules_path,
        )

        result = run_reminder_cycle(
            as_of_date="2026-09-13",
            businesses_path=self.businesses_path,
            reminders_path=self.reminders_path,
            rules_path=unparseable_rules_path,
        )

        # Must evaluate smoothly without exceptions and find 0 candidates
        self.assertEqual(result["candidates_found"], 0)
        self.assertEqual(result["reminders_sent"], 0)
        self.assertEqual(result["reminders_simulated"], 0)

    def test_acceptance_criterion_3_logs_simulated_when_no_credentials(self):
        """
        Acceptance Criterion 3:
        Sending with no provider credentials configured logs a "simulated"
        entry and does not raise.
        """
        result = run_reminder_cycle(
            as_of_date="2026-09-13",
            businesses_path=self.businesses_path,
            reminders_path=self.reminders_path,
            rules_path=self.rules_path,
        )
        self.assertEqual(result["reminders_simulated"], 1)
        logs = load(self.reminders_path, [])
        self.assertTrue(any(l.get("status") == "simulated" for l in logs))

    def test_acceptance_criterion_4_outside_windows_never_trigger(self):
        """
        Acceptance Criterion 4:
        Obligations due in 8 days or 2 days (outside the 7/3/1 windows) never
        trigger a reminder.
        """
        # GSTR-3B is due on 2026-09-20.
        # as_of = 2026-09-12 (8 days left) -> outside window
        res_8days = run_reminder_cycle(
            as_of_date="2026-09-12",
            businesses_path=self.businesses_path,
            reminders_path=self.reminders_path,
            rules_path=self.rules_path,
        )
        self.assertEqual(res_8days["candidates_found"], 0)
        self.assertEqual(res_8days["reminders_sent"] + res_8days["reminders_simulated"], 0)

        # as_of = 2026-09-18 (2 days left) -> outside window
        res_2days = run_reminder_cycle(
            as_of_date="2026-09-18",
            businesses_path=self.businesses_path,
            reminders_path=self.reminders_path,
            rules_path=self.rules_path,
        )
        self.assertEqual(res_2days["candidates_found"], 0)
        self.assertEqual(res_2days["reminders_sent"] + res_2days["reminders_simulated"], 0)

    def test_windows_3_and_1_trigger_correctly(self):
        # as_of = 2026-09-17 (3 days left to 2026-09-20) -> Window 3
        res_3days = run_reminder_cycle(
            as_of_date="2026-09-17",
            businesses_path=self.businesses_path,
            reminders_path=self.reminders_path,
            rules_path=self.rules_path,
        )
        self.assertEqual(res_3days["candidates_found"], 1)
        self.assertEqual(res_3days["reminders_simulated"], 1)

        # as_of = 2026-09-19 (1 day left to 2026-09-20) -> Window 1
        res_1day = run_reminder_cycle(
            as_of_date="2026-09-19",
            businesses_path=self.businesses_path,
            reminders_path=self.reminders_path,
            rules_path=self.rules_path,
        )
        self.assertEqual(res_1day["candidates_found"], 1)
        self.assertEqual(res_1day["reminders_simulated"], 1)


class ComplianceApiEndpointTests(unittest.TestCase):
    def setUp(self):
        self.patcher = patch.object(config, "WASENDER_API_KEY", None)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.client = app.test_client()

    def test_create_business_and_get_calendar(self):
        payload = {
            "business_id": "biz_api_test_01",
            "business_name": "API Test Enterprises",
            "gst_registered": True,
            "headcount": 25,
            "turnover": 5000000,
            "whatsapp_number": "+919988776655",
        }
        res = self.client.post("/api/compliance/businesses", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["business_id"], "biz_api_test_01")
        self.assertIn("obligations", data)

        # Query calendar with as_of date
        cal_res = self.client.get("/api/compliance/businesses/biz_api_test_01/calendar?as_of=2026-09-13")
        self.assertEqual(cal_res.status_code, 200)
        cal_data = cal_res.get_json()
        self.assertIn("obligations", cal_data)

    def test_run_reminders_and_view_logs(self):
        run_res = self.client.post("/api/compliance/reminders/run", json={"as_of_date": "2026-09-13"})
        self.assertEqual(run_res.status_code, 200)
        run_data = run_res.get_json()
        self.assertIn("as_of_date", run_data)
        self.assertIn("candidates_found", run_data)

        # View reminder logs
        log_res = self.client.get("/api/compliance/reminders/log")
        self.assertEqual(log_res.status_code, 200)
        log_data = log_res.get_json()
        self.assertIn("total", log_data)
        self.assertIn("logs", log_data)


if __name__ == "__main__":
    unittest.main()
