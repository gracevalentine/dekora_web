import unittest
from flask import Flask, json
from controller.xendit_controller import xendit_bp
from controller.db_config import get_db_connection

class TestXenditWebhookIntegration(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(xendit_bp)
        self.client = self.app.test_client()

        # Setup test data
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (external_id, status, paid_amount) VALUES (%s, %s, %s)",
            ("TEST123", "PENDING", 0)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def tearDown(self):
        # Clean test data
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE external_id = %s", ("TEST123",))
        conn.commit()
        cursor.close()
        conn.close()

    def test_webhook_paid_updates_db(self):
        payload = {
            "status": "PAID",
            "external_id": "TEST123",
            "paid_amount": 50000
        }

        response = self.client.post(
            '/xendit/webhook',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['success'], True)

        # Verify DB updated
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, paid_amount FROM orders WHERE external_id = %s", ("TEST123",))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        self.assertEqual(result[0], "PAID")
        self.assertEqual(result[1], 50000)
