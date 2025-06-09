import unittest
from app import app

class TestCartController(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['user_id'] = 1
            sess['email'] = 'test@example.com'

        from controller.db_config import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Setup dummy user & product
        cursor.execute("INSERT IGNORE INTO users (user_id, email, password) VALUES (1, 'test@example.com', 'test')")
        cursor.execute("INSERT IGNORE INTO products (product_id, name, price, category, image_url) VALUES (1, 'Test Product', 100000, 'Dekorasi', 'default.jpg')")
        # Bersihkan isi cart dulu
        cursor.execute("DELETE FROM cart WHERE user_id = 1")
        # Tambahkan 1 item ke cart untuk testing delete & update
        cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (1, 1, 1)")
        conn.commit()

        # Ambil cart_id yang baru ditambahkan
        cursor.execute("SELECT cart_id FROM cart WHERE user_id = 1 AND product_id = 1")
        result = cursor.fetchone()
        self.cart_id = result[0] if result else 1

        cursor.close()
        conn.close()

    def test_cart_page(self):
        res = self.client.get('/cart')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Keranjang Belanja', res.data)

    def test_add_to_cart(self):
        res = self.client.post('/add_to_cart', data={
            'product_id': 1,
            'quantity': 1
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Produk berhasil ditambahkan', res.data)

    def test_update_qty_valid(self):
        res = self.client.post('/update_qty', data={
            'cart_id': self.cart_id,
            'quantity': 2
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'success', res.data)

    def test_update_qty_invalid(self):
        res = self.client.post('/update_qty', data={
            'cart_id': self.cart_id,
            'quantity': 0
        })
        self.assertIn(b'Jumlah minimal 1', res.data)

    def test_delete_cart_valid(self):
        res = self.client.post('/cart/delete', data={
            'cart_id': self.cart_id
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'berhasil dihapus', res.data)

    def test_delete_cart_invalid(self):
        res = self.client.post('/cart/delete', data={
            'cart_id': 99999
        })
        self.assertIn(b'tidak ditemukan', res.data)

    def test_checkout_empty_cart(self):
        from controller.db_config import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE user_id = 1")
        conn.commit()
        cursor.close()
        conn.close()

        res = self.client.post('/checkout')
        self.assertIn(b'Cart kosong', res.data)


if __name__ == '__main__':
    unittest.main()
