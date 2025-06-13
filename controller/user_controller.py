from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from model.User import User
from controller.db_config import get_db_connection

user_bp = Blueprint('user', __name__)

# Endpoint untuk membuat user baru
@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')

    if not first_name or not last_name or not email:
        return jsonify({"message": "First name, last name, and email are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (first_name, last_name, email) VALUES (%s, %s, %s)', 
                   (first_name, last_name, email))
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"id": user_id, "first_name": first_name, "last_name": last_name, "email": email}), 201

# Endpoint untuk mengambil data user berdasarkan ID
@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return jsonify({
            "id": row['user_id'],
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            "email": row['email'],
            "address": row['address'] or 'N/A',
            "postal_code": row['postal_code'] or 'N/A',
            "wallet": row['wallet'] or 0.0
        }), 200

    return jsonify({"message": "User not found"}), 404

# Endpoint untuk memperbarui user berdasarkan ID
@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')

    if not first_name and not last_name and not email:
        return jsonify({"message": "At least one of first_name, last_name, or email is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    update_fields = []
    update_values = []

    if first_name:
        update_fields.append("first_name = %s")
        update_values.append(first_name)
    
    if last_name:
        update_fields.append("last_name = %s")
        update_values.append(last_name)
    
    if email:
        update_fields.append("email = %s")
        update_values.append(email)

    update_values.append(user_id)  # User ID untuk WHERE
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = %s"

    cursor.execute(query, update_values)
    conn.commit()
    updated = cursor.rowcount
    cursor.close()
    conn.close()

    if updated:
        return jsonify({
            "user_id": user_id,
            "first_name": first_name if first_name else 'No change',
            "last_name": last_name if last_name else 'No change',
            "email": email if email else 'No change'
        }), 200

    return jsonify({"message": "User not found"}), 404

# Endpoint untuk menghapus user berdasarkan ID
@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM cart WHERE user_id = %s', (user_id,))
    cart_items = cursor.fetchall()
    if cart_items:
        cursor.close()
        conn.close()
        return jsonify({"message": "Cannot delete user with active cart items."}), 400

    cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()
    conn.close()

    if deleted:
        return jsonify({"message": "User deleted"}), 200
    return jsonify({"message": "User not found"}), 404

# Login route
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['logged_in'] = True
            session['user_id'] = user['user_id']
            session['user_name'] = user['first_name']
            flash('Login berhasil! Selamat datang, {}.'.format(user['first_name']), 'success')
            return redirect(url_for('index'))
        else:
            error = 'Gagal login, email atau password salah'
            return render_template('login.html', error=error)
    return render_template('login.html')

# Logout route
@user_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))

# Signup route
@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        address = request.form.get('address', '')
        postal_code = request.form.get('postal_code', '')
        wallet = 0  # or None

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            error = 'Email sudah terdaftar'
            return render_template('signup.html', error=error)

        cursor.execute('''
            INSERT INTO users (first_name, last_name, email, password, address, postal_code, wallet)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (first_name, last_name, email, password, address, postal_code, wallet))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('user.login'))
    return render_template('signup.html')

# Profile route
@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('logged_in'):
        return redirect(url_for('user.login'))

    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    success = None
    error = None

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        postal_code = request.form['postal_code']
        email = request.form['email']
        current_password = request.form['current_password']
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        confirm_change_password = request.form.get('confirm_change_password')

        cursor.execute("""
            UPDATE users 
            SET first_name=%s, last_name=%s, address=%s, postal_code=%s, email=%s
            WHERE user_id=%s
        """, (first_name, last_name, address, postal_code, email, user_id))

        if confirm_change_password and new_password and new_password == confirm_new_password:
            cursor.execute("SELECT * FROM users WHERE user_id = %s AND password = %s", (user_id, current_password))
            user_check = cursor.fetchone()
            if user_check:
                cursor.execute("UPDATE users SET password=%s WHERE user_id=%s", (new_password, user_id))
                success = "Profil dan password berhasil diupdate."
            else:
                error = "Password lama salah."

        elif confirm_change_password:
            error = "Konfirmasi password baru tidak cocok."

        else:
            success = "Profil berhasil diupdate."

        conn.commit()

        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template('profile.html', user=user, success=success, error=error)

# Wallet API route
@user_bp.route('/api/wallet', methods=['GET'])
def get_wallet():
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT wallet FROM users WHERE user_id = %s', (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return jsonify({"success": True, "wallet": row['wallet']}), 200
    return jsonify({"success": False, "wallet": 0}), 404
