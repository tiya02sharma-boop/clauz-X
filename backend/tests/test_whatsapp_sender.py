import json
import unittest
from unittest.mock import patch

from backend.whatsapp_sender import get_wasender_status, send_whatsapp_message


class _FakeResponse:
    def __init__(self, body: dict):
        self._body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


class WaSenderResponseTests(unittest.TestCase):
    @patch("backend.whatsapp_sender.urllib.request.urlopen")
    def test_session_status_reports_connected_without_exposing_credentials(self, urlopen):
        urlopen.return_value = _FakeResponse({"status": "connected"})

        status = get_wasender_status(api_key="test-key")

        self.assertEqual(status, {"configured": True, "status": "connected"})

    @patch("backend.whatsapp_sender.urllib.request.urlopen")
    def test_provider_error_in_successful_http_response_is_not_marked_sent(self, urlopen):
        urlopen.return_value = _FakeResponse({"success": False, "message": "Invalid recipient"})

        result = send_whatsapp_message(
            to="+919876543210",
            message="Reminder",
            api_key="test-key",
        )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.error_code, "INVALID_NUMBER")

    @patch("backend.whatsapp_sender.urllib.request.urlopen")
    def test_provider_success_is_marked_sent(self, urlopen):
        urlopen.return_value = _FakeResponse({"success": True, "data": {"msgId": "msg_123"}})

        result = send_whatsapp_message(
            to="+919876543210",
            message="Reminder",
            api_key="test-key",
        )

        self.assertEqual(result.status, "sent")
        self.assertEqual(result.sid, "msg_123")
