from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from controller.db_config import get_db_connection

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

@cart_bp.route('/delete', methods=['POST'])
def delete_cart():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu.'}), 401
    user_id = session['user_id']
    cart_id = request.form.get('cart_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart WHERE cart_id = %s AND user_id = %s', (cart_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})