from flask import Blueprint, request, jsonify
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
