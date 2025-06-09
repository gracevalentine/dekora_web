import unittest
import requests

BASE_URL = "http://localhost:5000"

class TestCartIntegration(unittest.TestCase):

    def setUp(self):
        self.session = requests.Session()
        login_data = {
            "email": "test@example.com",
            "password": "test"
        }
        self.session.post(f"{BASE_URL}/login", data=login_data)

    def test_add_to_cart_integration(self):
        data = {
            "product_id": 1,
            "quantity": 2
        }
        res = self.session.post(f"{BASE_URL}/add_to_cart", data=data)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Produk berhasil ditambahkan", res.content)

    def test_cart_page_view(self):
        res = self.session.get(f"{BASE_URL}/cart")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Keranjang Belanja", res.content)

if __name__ == '__main__':
    unittest.main()
