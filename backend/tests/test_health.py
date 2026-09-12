import unittest

from backend.app import app


class HealthEndpointTests(unittest.TestCase):
    def test_health_endpoint_reports_ready(self):
        response = app.test_client().get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "status": "ok",
            "service": "clauzx-backend",
        })
