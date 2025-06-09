from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash

from model.User import User
from controller.db_config import get_db_connection

user_bp = Blueprint('user', __name__)

# @user_bp.route('/users', methods=['GET'])
# def get_users():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute('SELECT * FROM users')
#     result = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     users = []
#     for row in result:
#         user = User(
#             id=row['id'],
#             name=row['name'],
#             email=row['email'],
#             address=row.get('address', ''),
#             postal_code=row.get('postal_code', ''),
#             wallet=row.get('wallet', 0.0)
#         )
#         users.append({
#             "id": user._id,
#             "name": user._name,
#             "email": user._email,
#             "address": user._address,
#             "postal_code": user._postal_code,
#             "wallet": user._wallet
#         })

#     return jsonify(users), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        user = User(
            id=row['id'],
            name=row['name'],
            email=row['email'],
            address=row.get('address', ''),
            postal_code=row.get('postal_code', ''),
            wallet=row.get('wallet', 0.0)
        )
        return jsonify({
            "id": user._id,
            "name": user._name,
            "email": user._email,
            "address": user._address,
            "postal_code": user._postal_code,
            "wallet": user._wallet
        }), 200

    return jsonify({"message": "User not found"}), 404


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"message": "Name and email are required"}), 400

    user = User(name=name, email=email)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, email) VALUES (%s, %s)', (user.name, user.email))
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"id": user_id, "name": user.name, "email": user.email}), 201


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"message": "Name and email are required"}), 400

    user = User(id=user_id, name=name, email=email)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET name = %s, email = %s WHERE id = %s', (user.name, user.email, user.id))
    conn.commit()
    updated = cursor.rowcount
    cursor.close()
    conn.close()

    if updated:
        return jsonify({"id": user.id, "name": user.name, "email": user.email}), 200

    return jsonify({"message": "User not found"}), 404


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()
    conn.close()

    if deleted:
        return jsonify({"message": "User deleted"}), 200
    return jsonify({"message": "User not found"}), 404

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

@user_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))

@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        address = request.form.get('address', '')
        postal_code = request.form.get('postal_code', '')
        wallet = 0  # atau bisa None

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Cek apakah email sudah terdaftar
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            error = 'Email sudah terdaftar'
            return render_template('signup.html', error=error)
        # Insert user baru
        cursor.execute('''
            INSERT INTO users (first_name, last_name, email, password, address, postal_code, wallet)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (first_name, last_name, email, password, address, postal_code, wallet))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('user.login'))
    return render_template('signup.html')

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('logged_in'):
        return redirect(url_for('user.login'))

    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Ambil data user untuk ditampilkan
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

        # Cek password lama benar
        cursor.execute("SELECT * FROM users WHERE user_id = %s AND password = %s", (user_id, current_password))
        user_check = cursor.fetchone()
        if not user_check:
            error = "Password lama salah."
        else:
            # Update data profil
            cursor.execute("""
                UPDATE users SET first_name=%s, last_name=%s, address=%s, postal_code=%s, email=%s
                WHERE user_id=%s
            """, (first_name, last_name, address, postal_code, email, user_id))

            # Jika user ingin ganti password dan konfirmasi benar
            if confirm_change_password and new_password and new_password == confirm_new_password:
                cursor.execute("UPDATE users SET password=%s WHERE user_id=%s", (new_password, user_id))
                success = "Profil dan password berhasil diupdate."
            elif confirm_change_password:
                error = "Konfirmasi password baru tidak cocok."
            else:
                success = "Profil berhasil diupdate."

            conn.commit()

        # Refresh data user setelah update
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template('profile.html', user=user, success=success, error=error)

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