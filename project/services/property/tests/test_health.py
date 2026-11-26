import unittest

from fastapi.testclient import TestClient

from project.services.property.app import app


class HealthTest(unittest.TestCase):
    def test_health_reports_running_service(self) -> None:
        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
