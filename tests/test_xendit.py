import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, json
from controller.xendit_controller import xendit_bp  # pastikan path ini sesuai

class TestXenditWebhookUnit(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(xendit_bp)
        self.client = self.app.test_client()

    @patch('controller.xendit_controller.get_db_connection')  # ✅ path udah bener
    def test_webhook_paid_success(self, mock_get_db):
        # Mock DB
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        payload = {
            "status": "PAID",
            "external_id": "INV12345",
            "paid_amount": 299000
        }

        response = self.client.post(
            '/xendit/webhook',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'success': True})
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_webhook_invalid_json(self):
        response = self.client.post(
            '/xendit/webhook',
            data="bukan json",  # bukan JSON valid
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn('success', response.json)
        self.assertFalse(response.json['success'])

    def test_webhook_non_paid_status(self):
        payload = {
            "status": "PENDING",
            "external_id": "INV12345",
            "paid_amount": 1000
        }
        response = self.client.post(
            '/xendit/webhook',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['success'], False)
