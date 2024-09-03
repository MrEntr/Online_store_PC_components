from flask import Blueprint, jsonify, request
from models import OrderDetails, Products, Orders, db

order_details_bp = Blueprint('order_details_routes', __name__)


@order_details_bp.route('/order-details', methods=['GET'])
def get_order_details():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'order_detail_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = OrderDetails.query.filter_by(is_deleted=False)

    if search:
        query = query.filter(OrderDetails.quantity.contains(search) |
                             OrderDetails.price.contains(search))

    if order == 'asc':
        query = query.order_by(getattr(OrderDetails, sort_by).asc())
    else:
        query = query.order_by(getattr(OrderDetails, sort_by).desc())

    order_details = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'order_details': [detail.serialize() for detail in order_details.items],
        'total': order_details.total,
        'pages': order_details.pages,
        'current_page': order_details.page
    })


@order_details_bp.route('/order-details/<int:order_detail_id>', methods=['GET'])
def get_order_detail(order_detail_id):
    detail = OrderDetails.query.filter_by(order_detail_id=order_detail_id, is_deleted=False).first()
    if not detail:
        return jsonify({'message': 'Order detail not found'}), 404

    return jsonify(detail.serialize())


@order_details_bp.route('/order-details', methods=['POST'])
def create_order_detail():
    data = request.get_json()
    if not data or not data.get('quantity') or not data.get('price') or not data.get('product_id') or not data.get('order_id'):
        return jsonify({'message': 'Quantity, price, product_id, and order_id are required'}), 400

    product_id = data['product_id']
    product = Products.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    order_id = data['order_id']
    order = Orders.query.get(order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    new_detail = OrderDetails(
        quantity=data['quantity'],
        price=data['price'],
        product_id=product_id,
        order_id=order_id
    )
    db.session.add(new_detail)
    db.session.commit()

    return jsonify({'message': 'Order detail created successfully', 'order_detail_id': new_detail.order_detail_id}), 201


@order_details_bp.route('/order-details/<int:order_detail_id>', methods=['PUT'])
def update_order_detail(order_detail_id):
    detail = OrderDetails.query.filter_by(order_detail_id=order_detail_id, is_deleted=False).first()
    if not detail:
        return jsonify({'message': 'Order detail not found'}), 404

    data = request.get_json()
    detail.quantity = data.get('quantity', detail.quantity)
    detail.price = data.get('price', detail.price)

    db.session.commit()
    return jsonify({'message': 'Order detail updated successfully'})


@order_details_bp.route('/order-details/<int:order_detail_id>', methods=['DELETE'])
def delete_order_detail(order_detail_id):
    detail = OrderDetails.query.filter_by(order_detail_id=order_detail_id, is_deleted=False).first()
    if not detail:
        return jsonify({'message': 'Order detail not found'}), 404

    detail.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Order detail deleted successfully'})


@order_details_bp.route('/order-details/restore', methods=['POST'])
def restore_order_details():
    data = request.get_json()
    detail_ids = data.get('order_detail_ids')
    if not detail_ids:
        return jsonify({'message': 'No order detail IDs provided'}), 400

    details_to_restore = OrderDetails.query.filter(OrderDetails.order_detail_id.in_(detail_ids), OrderDetails.is_deleted == True).all()
    for detail in details_to_restore:
        detail.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(details_to_restore)} order details'})