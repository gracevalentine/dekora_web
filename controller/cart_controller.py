from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from controller.db_config import get_db_connection
# controller/cart_controller.py
import requests, base64, time, uuid


cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
def cart():
    if not session.get('logged_in'):
        return redirect(url_for('user.login'))
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # <-- HARUS dictionary=True
    cursor.execute('''
        SELECT c.cart_id, c.quantity, p.product_id, p.name, p.price, p.image_url
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    ''', (user_id,))
    cart_items = cursor.fetchall()
    total_produk = sum(item['price'] * item['quantity'] for item in cart_items)
    cursor.close()
    conn.close()
    return render_template('Cart.html', cart_items=cart_items, total_produk=total_produk)

@cart_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu.'}), 401

    user_id = session['user_id']
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Cek apakah produk sudah ada di cart
    cursor.execute('SELECT * FROM cart WHERE user_id = %s AND product_id = %s', (user_id, product_id))
    cart_item = cursor.fetchone()
    if cart_item:
        # Update quantity
        cursor.execute('UPDATE cart SET quantity = quantity + %s WHERE cart_id = %s', (quantity, cart_item['cart_id']))
    else:
        # Insert baru
        cursor.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)', (user_id, product_id, quantity))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'message': 'Produk berhasil ditambahkan ke cart.'})

@cart_bp.route('/update_qty', methods=['POST'])
def update_qty():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu.'}), 401
    user_id = session['user_id']
    cart_id = request.form.get('cart_id')
    quantity = int(request.form.get('quantity', 1))
    if quantity < 1:
        return jsonify({'success': False, 'message': 'Jumlah minimal 1.'})
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE cart SET quantity = %s WHERE cart_id = %s AND user_id = %s', (quantity, cart_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@cart_bp.route('/cart/delete', methods=['POST'])
def delete_cart():
    cart_id = request.form.get('cart_id')
    if not cart_id:
        return jsonify(success=False, message="Cart ID tidak ditemukan.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE cart_id = %s", (cart_id,))
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()
    conn.close()
    if deleted:
        return jsonify(success=True, message="Produk berhasil dihapus dari cart.")
    else:
        return jsonify(success=False, message="Produk tidak ditemukan di cart.")



@cart_bp.route('/checkout', methods=['POST'])
def checkout():
    if not session.get('logged_in'):
        return redirect(url_for('user.login'))
    
    user_id = session['user_id']
    delivery_method = request.form.get('delivery_method', 'pickup')
    delivery_fee = 25000 if delivery_method == 'delivery' else 0
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Ambil semua item cart
    cursor.execute('''
        SELECT c.cart_id, c.quantity, p.product_id, p.name, p.price,
               (c.quantity * p.price) as subtotal
        FROM cart c 
        JOIN products p ON c.product_id = p.product_id 
        WHERE c.user_id = %s
    ''', (user_id,))
    cart_items = cursor.fetchall()
    
    if not cart_items:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Cart kosong'}), 400

    total = sum(item['subtotal'] for item in cart_items)
    grand_total = total + delivery_fee

    import requests, base64, time, uuid
    api_key = 'xnd_development_5v7BqnSusQojGoxOXIJY11K75pt0yVkTeXyuvaPD9R95DYdGZmtZWAFZGsxrgPg'  # Ganti dengan key kamu
    headers = {
        'Authorization': 'Basic ' + base64.b64encode((api_key + ':').encode()).decode(),
        'Content-Type': 'application/json'
    }
    external_id = f"order-{user_id}-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    data = {
        "external_id": external_id,
        "amount": grand_total,
        "payer_email": session.get('email', 'user@email.com'),
        "description": "Pembayaran Dekora",
        "success_redirect_url": url_for('cart.cart', _external=True)
    }
    response = requests.post(
        "https://api.xendit.co/v2/invoices",
        headers=headers,
        json=data
    )
    print("Xendit Response:", response.text)
    if response.status_code == 200:
        result = response.json()
        # Buat satu baris order saja
        cursor.execute('''
            INSERT INTO orders 
            (user_id, total_amount, external_id, status) 
            VALUES (%s, %s, %s, %s)
        ''', (
            user_id,
            total,
            external_id,
            'PENDING'
        ))
        # (Opsional) Insert detail produk ke tabel lain, misal order_items/transaction
        # Kosongkan cart
        cursor.execute('DELETE FROM cart WHERE user_id = %s', (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(result['invoice_url'])
    else:
        cursor.close()
        conn.close()
        return jsonify({
            'success': False, 
            'message': 'Gagal membuat invoice',
            'error': response.text
        }), 400
        
@cart_bp.route('/clear_cart', methods=['POST'])
def clear_cart():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu.'}), 401

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart WHERE user_id = %s', (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'message': 'Cart berhasil dikosongkan.'})
