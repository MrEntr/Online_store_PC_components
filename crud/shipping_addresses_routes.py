from flask import Blueprint, jsonify, request
from models import ShippingAddresses, Users, Orders, db

shipping_addresses_bp = Blueprint('shipping_addresses_routes', __name__)


@shipping_addresses_bp.route('/shipping-addresses', methods=['GET'])
def get_shipping_addresses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'address_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = ShippingAddresses.query.filter_by(is_deleted=False)

    if search:
        query = query.filter(ShippingAddresses.delivery_address.contains(search) |
                             ShippingAddresses.country.contains(search) |
                             ShippingAddresses.city.contains(search) |
                             ShippingAddresses.postal_code.contains(search))

    if order == 'asc':
        query = query.order_by(getattr(ShippingAddresses, sort_by).asc())
    else:
        query = query.order_by(getattr(ShippingAddresses, sort_by).desc())

    shipping_addresses = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'shipping_addresses': [addr.serialize() for addr in shipping_addresses.items],
        'total': shipping_addresses.total,
        'pages': shipping_addresses.pages,
        'current_page': shipping_addresses.page
    })


@shipping_addresses_bp.route('/shipping-addresses/<int:address_id>', methods=['GET'])
def get_shipping_address(address_id):
    address = ShippingAddresses.query.filter_by(address_id=address_id, is_deleted=False).first()
    if not address:
        return jsonify({'message': 'Shipping address not found'}), 404

    return jsonify(address.serialize())


@shipping_addresses_bp.route('/shipping-addresses', methods=['POST'])
def create_shipping_address():
    data = request.get_json()
    if not data or not data.get('delivery_address') or not data.get('country') or not data.get('city') or not data.get('postal_code') or not data.get('user_id'):
        return jsonify({'message': 'Delivery address, country, city, postal code, and user ID are required'}), 400

    user_id = data['user_id']
    user = Users.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    new_address = ShippingAddresses(
        delivery_address=data['delivery_address'],
        country=data['country'],
        city=data['city'],
        postal_code=data['postal_code'],
        user_id=user_id
    )
    db.session.add(new_address)
    db.session.commit()

    return jsonify({'message': 'Shipping address created successfully', 'address_id': new_address.address_id}), 201


@shipping_addresses_bp.route('/shipping-addresses/<int:address_id>', methods=['PUT'])
def update_shipping_address(address_id):
    address = ShippingAddresses.query.filter_by(address_id=address_id, is_deleted=False).first()
    if not address:
        return jsonify({'message': 'Shipping address not found'}), 404

    data = request.get_json()
    address.delivery_address = data.get('delivery_address', address.delivery_address)
    address.country = data.get('country', address.country)
    address.city = data.get('city', address.city)
    address.postal_code = data.get('postal_code', address.postal_code)

    db.session.commit()
    return jsonify({'message': 'Shipping address updated successfully'})


@shipping_addresses_bp.route('/shipping-addresses/<int:address_id>', methods=['DELETE'])
def delete_shipping_address(address_id):
    address = ShippingAddresses.query.filter_by(address_id=address_id, is_deleted=False).first()
    if not address:
        return jsonify({'message': 'Shipping address not found'}), 404

    address.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Shipping address deleted successfully'})


@shipping_addresses_bp.route('/shipping-addresses/restore', methods=['POST'])
def restore_shipping_addresses():
    data = request.get_json()
    address_ids = data.get('address_ids')
    if not address_ids:
        return jsonify({'message': 'No shipping address IDs provided'}), 400

    addresses_to_restore = ShippingAddresses.query.filter(ShippingAddresses.address_id.in_(address_ids), ShippingAddresses.is_deleted == True).all()
    for address in addresses_to_restore:
        address.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(addresses_to_restore)} shipping addresses'})
