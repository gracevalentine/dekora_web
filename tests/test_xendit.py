import unittest
from app import app
from controller.db_config import get_db_connection

class TestXenditWebhook(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        # Tambahkan dummy order
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT IGNORE INTO orders (order_id, user_id, external_id, status, paid_amount) 
            VALUES (1, 1, 'order-1-test', 'PENDING', 0)
        """)
        conn.commit()
        cursor.close()
        conn.close()

    def test_webhook_paid_valid(self):
        payload = {
            "external_id": "order-1-test",
            "status": "PAID",
            "paid_amount": 100000
        }
        res = self.client.post('/xendit/webhook', json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'success', res.data)

    def test_webhook_paid_invalid(self):
        payload = {
            "external_id": "order-x-not-found",
            "status": "PAID",
            "paid_amount": 100000
        }
        res = self.client.post('/xendit/webhook', json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'success', res.data)  # tetap 200 meski tidak ditemukan, sesuai logic-mu

    def test_webhook_malformed_data(self):
        # Kirim payload yang tidak valid
        res = self.client.post('/xendit/webhook', data="Not JSON", content_type='text/plain')
        self.assertEqual(res.status_code, 500)
        self.assertIn(b'success', res.data)

if __name__ == '__main__':
    unittest.main()
