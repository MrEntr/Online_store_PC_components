from flask import Blueprint, jsonify, request
from models import Orders, ShippingAddresses, Users, OrderDetails, db

orders_bp = Blueprint('orders_routes', __name__)


@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'order_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = Orders.query.filter_by(is_deleted=False)

    if search:
        query = query.filter(Orders.order_id.contains(search))

    if order == 'asc':
        query = query.order_by(getattr(Orders, sort_by).asc())
    else:
        query = query.order_by(getattr(Orders, sort_by).desc())

    orders = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'orders': [order.serialize() for order in orders.items],
        'total': orders.total,
        'pages': orders.pages,
        'current_page': orders.page
    })


@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Orders.query.filter_by(order_id=order_id, is_deleted=False).first()
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    return jsonify(order.serialize())


@orders_bp.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data or not data.get('address_id') or not data.get('customer_id'):
        return jsonify({'message': 'Address ID and customer ID are required'}), 400

    address_id = data['address_id']
    customer_id = data['customer_id']
    shipping_address = ShippingAddresses.query.get(address_id)
    if not shipping_address:
        return jsonify({'message': 'Shipping address not found'}), 404

    user = Users.query.get(customer_id)
    if not user:
        return jsonify({'message': 'Customer not found'}), 404

    new_order = Orders(
        address_id=address_id,
        customer_id=customer_id
    )
    db.session.add(new_order)
    db.session.commit()

    return jsonify({'message': 'Order created successfully', 'order_id': new_order.order_id}), 201


@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Orders.query.filter_by(order_id=order_id, is_deleted=False).first()
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    data = request.get_json()
    order.address_id = data.get('address_id', order.address_id)
    order.customer_id = data.get('customer_id', order.customer_id)

    db.session.commit()
    return jsonify({'message': 'Order updated successfully'})


@orders_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Orders.query.filter_by(order_id=order_id, is_deleted=False).first()
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    order.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Order deleted successfully'})


@orders_bp.route('/orders/restore', methods=['POST'])
def restore_orders():
    data = request.get_json()
    order_ids = data.get('order_ids')
    if not order_ids:
        return jsonify({'message': 'No order IDs provided'}), 400

    orders_to_restore = Orders.query.filter(Orders.order_id.in_(order_ids), Orders.is_deleted == True).all()
    for order in orders_to_restore:
        order.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(orders_to_restore)} orders'})
