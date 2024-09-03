from flask import Blueprint, jsonify, request
from models import Cart, CartItems, Users, db

cart_bp = Blueprint('cart_routes', __name__)


@cart_bp.route('/carts', methods=['GET'])
def get_carts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'cart_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = Cart.query.filter_by(is_deleted=False)

    if search:
        query = query.filter(Cart.created_date.contains(search))

    if order == 'asc':
        query = query.order_by(getattr(Cart, sort_by).asc())
    else:
        query = query.order_by(getattr(Cart, sort_by).desc())

    carts = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'carts': [cart.serialize() for cart in carts.items],
        'total': carts.total,
        'pages': carts.pages,
        'current_page': carts.page
    })


@cart_bp.route('/carts/<int:cart_id>', methods=['GET'])
def get_cart(cart_id):
    cart = Cart.query.filter_by(cart_id=cart_id, is_deleted=False).first()
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404

    return jsonify(cart.serialize())


@cart_bp.route('/carts', methods=['POST'])
def create_cart():
    data = request.get_json()
    if not data or not data.get('user_id'):
        return jsonify({'message': 'User ID is required'}), 400

    user_id = data['user_id']
    user = Users.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    new_cart = Cart(user_id=user_id)
    db.session.add(new_cart)
    db.session.commit()

    return jsonify({'message': 'Cart created successfully', 'cart_id': new_cart.cart_id}), 201


@cart_bp.route('/carts/<int:cart_id>', methods=['PUT'])
def update_cart(cart_id):
    cart = Cart.query.filter_by(cart_id=cart_id, is_deleted=False).first()
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404

    data = request.get_json()
    cart.user_id = data.get('user_id', cart.user_id)

    db.session.commit()
    return jsonify({'message': 'Cart updated successfully'})


@cart_bp.route('/carts/<int:cart_id>', methods=['DELETE'])
def delete_cart(cart_id):
    cart = Cart.query.filter_by(cart_id=cart_id, is_deleted=False).first()
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404

    cart.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Cart deleted successfully'})


@cart_bp.route('/carts/restore', methods=['POST'])
def restore_carts():
    data = request.get_json()
    cart_ids = data.get('cart_ids')
    if not cart_ids:
        return jsonify({'message': 'No cart IDs provided'}), 400

    carts_to_restore = Cart.query.filter(Cart.cart_id.in_(cart_ids), Cart.is_deleted == True).all()
    for cart in carts_to_restore:
        cart.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(carts_to_restore)} carts'})
