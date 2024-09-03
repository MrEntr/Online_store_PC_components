from flask import Blueprint, jsonify, request
from models import CartItems, Cart, Products, db

cart_items_bp = Blueprint('cart_items_routes', __name__)


@cart_items_bp.route('/cart-items', methods=['GET'])
def get_cart_items():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'cart_item_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = CartItems.query.filter_by(is_deleted=False)

    if search:
        query = query.filter(CartItems.quantity.contains(search))

    if order == 'asc':
        query = query.order_by(getattr(CartItems, sort_by).asc())
    else:
        query = query.order_by(getattr(CartItems, sort_by).desc())

    cart_items = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'cart_items': [cart_item.serialize() for cart_item in cart_items.items],
        'total': cart_items.total,
        'pages': cart_items.pages,
        'current_page': cart_items.page
    })


@cart_items_bp.route('/cart-items/<int:cart_item_id>', methods=['GET'])
def get_cart_item(cart_item_id):
    cart_item = CartItems.query.filter_by(cart_item_id=cart_item_id, is_deleted=False).first()
    if not cart_item:
        return jsonify({'message': 'Cart item not found'}), 404

    return jsonify(cart_item.serialize())


@cart_items_bp.route('/cart-items', methods=['POST'])
def create_cart_item():
    data = request.get_json()
    if not data or not data.get('cart_id') or not data.get('product_id') or not data.get('quantity'):
        return jsonify({'message': 'Cart ID, Product ID, and Quantity are required'}), 400

    cart_id = data['cart_id']
    product_id = data['product_id']
    quantity = data['quantity']

    cart = Cart.query.get(cart_id)
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404

    product = Products.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    new_cart_item = CartItems(cart_id=cart_id, product_id=product_id, quantity=quantity)
    db.session.add(new_cart_item)
    db.session.commit()

    return jsonify({'message': 'Cart item created successfully', 'cart_item_id': new_cart_item.cart_item_id}), 201


@cart_items_bp.route('/cart-items/<int:cart_item_id>', methods=['PUT'])
def update_cart_item(cart_item_id):
    cart_item = CartItems.query.filter_by(cart_item_id=cart_item_id, is_deleted=False).first()
    if not cart_item:
        return jsonify({'message': 'Cart item not found'}), 404

    data = request.get_json()
    cart_item.cart_id = data.get('cart_id', cart_item.cart_id)
    cart_item.product_id = data.get('product_id', cart_item.product_id)
    cart_item.quantity = data.get('quantity', cart_item.quantity)

    db.session.commit()
    return jsonify({'message': 'Cart item updated successfully'})


@cart_items_bp.route('/cart-items/<int:cart_item_id>', methods=['DELETE'])
def delete_cart_item(cart_item_id):
    cart_item = CartItems.query.filter_by(cart_item_id=cart_item_id, is_deleted=False).first()
    if not cart_item:
        return jsonify({'message': 'Cart item not found'}), 404

    cart_item.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Cart item deleted successfully'})


@cart_items_bp.route('/cart-items/restore', methods=['POST'])
def restore_cart_items():
    data = request.get_json()
    cart_item_ids = data.get('cart_item_ids')
    if not cart_item_ids:
        return jsonify({'message': 'No cart item IDs provided'}), 400

    cart_items_to_restore = CartItems.query.filter(CartItems.cart_item_id.in_(cart_item_ids), CartItems.is_deleted == True).all()
    for cart_item in cart_items_to_restore:
        cart_item.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(cart_items_to_restore)} cart items'})
