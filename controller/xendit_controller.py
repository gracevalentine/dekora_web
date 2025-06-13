from flask import Blueprint, request, jsonify
import json
from controller.db_config import get_db_connection  # 👈 Pindahkan import ke atas

xendit_bp = Blueprint('xendit', __name__)

@xendit_bp.route('/xendit/webhook', methods=['POST'])
def xendit_webhook():
    try:
        data = request.json
        print("Webhook Data:", json.dumps(data, indent=2))  # Debug print

        if data and data.get('status') == 'PAID':
            external_id = data.get('external_id')
            paid_amount = data.get('paid_amount', 0)

            conn = get_db_connection()
            cursor = conn.cursor()

            # Update order status
            cursor.execute(
                "UPDATE orders SET status = %s, paid_amount = %s WHERE external_id = %s",
                ('PAID', paid_amount, external_id)
            )
            conn.commit()
            print(f"Rows affected: {cursor.rowcount}")
            cursor.close()
            conn.close()

            if cursor.rowcount == 0:
                print(f"TIDAK ADA order dengan external_id {external_id} yang ditemukan!")
            else:
                print(f"Order {external_id} updated to PAID")

            return jsonify({'success': True}), 200

        return jsonify({'success': False, 'error': 'Invalid or missing data'}), 400

    except Exception as e:
        print(f"Webhook Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
