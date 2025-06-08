from flask import Blueprint, request, session, redirect, url_for, jsonify
from controller.db_config import get_db_connection

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
def cart():
    if not session.get('logged_in'):
        return redirect(url_for('user.login'))
    return render_template('cart.html')


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