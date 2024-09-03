from flask import Blueprint, jsonify, request
from models import Payments, Orders, db

payments_bp = Blueprint('payments_routes', __name__)


@payments_bp.route('/payments', methods=['GET'])
def get_payments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'payment_id')
    order = request.args.get('order', 'asc')

    query = Payments.query.filter_by(is_deleted=False)

    if order == 'asc':
        query = query.order_by(getattr(Payments, sort_by).asc())
    else:
        query = query.order_by(getattr(Payments, sort_by).desc())

    payments = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'payments': [payment.serialize() for payment in payments.items],
        'total': payments.total,
        'pages': payments.pages,
        'current_page': payments.page
    })


@payments_bp.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = Payments.query.filter_by(payment_id=payment_id, is_deleted=False).first()
    if not payment:
        return jsonify({'message': 'Payment not found'}), 404

    return jsonify(payment.serialize())


@payments_bp.route('/payments', methods=['POST'])
def create_payment():
    data = request.get_json()
    if not data or not data.get('order_id') or not data.get('amount'):
        return jsonify({'message': 'Order ID and amount are required'}), 400

    order_id = data['order_id']
    order = Orders.query.get(order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    new_payment = Payments(
        amount=data['amount'],
        order_id=order_id
    )
    db.session.add(new_payment)
    db.session.commit()

    return jsonify({'message': 'Payment created successfully', 'payment_id': new_payment.payment_id}), 201


@payments_bp.route('/payments/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    payment = Payments.query.filter_by(payment_id=payment_id, is_deleted=False).first()
    if not payment:
        return jsonify({'message': 'Payment not found'}), 404

    data = request.get_json()
    payment.amount = data.get('amount', payment.amount)

    db.session.commit()
    return jsonify({'message': 'Payment updated successfully'})


@payments_bp.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    payment = Payments.query.filter_by(payment_id=payment_id, is_deleted=False).first()
    if not payment:
        return jsonify({'message': 'Payment not found'}), 404

    payment.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Payment deleted successfully'})


@payments_bp.route('/payments/restore', methods=['POST'])
def restore_payments():
    data = request.get_json()
    payment_ids = data.get('payment_ids')
    if not payment_ids:
        return jsonify({'message': 'No payment IDs provided'}), 400

    payments_to_restore = Payments.query.filter(Payments.payment_id.in_(payment_ids), Payments.is_deleted == True).all()
    for payment in payments_to_restore:
        payment.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(payments_to_restore)} payments'})
