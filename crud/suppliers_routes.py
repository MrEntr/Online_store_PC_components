from flask import Blueprint, jsonify, request
from models import Suppliers, Products, db

suppliers_bp = Blueprint('suppliers_routes', __name__)


@suppliers_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'supplier_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = Suppliers.query.filter_by(is_deleted=False)

    if search:
        query = query.filter(Suppliers.supplier_name.contains(search) | Suppliers.contact_name.contains(search))

    if order == 'asc':
        query = query.order_by(getattr(Suppliers, sort_by).asc())
    else:
        query = query.order_by(getattr(Suppliers, sort_by).desc())

    suppliers = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'suppliers': [supplier.serialize() for supplier in suppliers.items],
        'total': suppliers.total,
        'pages': suppliers.pages,
        'current_page': suppliers.page
    })


@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    supplier = Suppliers.query.filter_by(supplier_id=supplier_id, is_deleted=False).first()
    if not supplier:
        return jsonify({'message': 'Supplier not found'}), 404

    return jsonify(supplier.serialize())


@suppliers_bp.route('/suppliers', methods=['POST'])
def create_supplier():
    data = request.get_json()
    if not data or not data.get('contact_name') or not data.get('address') or not data.get('phone'):
        return jsonify({'message': 'Contact name, address, and phone are required'}), 400

    new_supplier = Suppliers(
        supplier_name=data.get('supplier_name'),
        contact_name=data['contact_name'],
        address=data['address'],
        phone=data['phone']
    )
    db.session.add(new_supplier)
    db.session.commit()

    return jsonify({'message': 'Supplier created successfully', 'supplier_id': new_supplier.supplier_id}), 201


@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    supplier = Suppliers.query.filter_by(supplier_id=supplier_id, is_deleted=False).first()
    if not supplier:
        return jsonify({'message': 'Supplier not found'}), 404

    data = request.get_json()
    supplier.supplier_name = data.get('supplier_name', supplier.supplier_name)
    supplier.contact_name = data.get('contact_name', supplier.contact_name)
    supplier.address = data.get('address', supplier.address)
    supplier.phone = data.get('phone', supplier.phone)

    db.session.commit()
    return jsonify({'message': 'Supplier updated successfully'})


@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    supplier = Suppliers.query.filter_by(supplier_id=supplier_id, is_deleted=False).first()
    if not supplier:
        return jsonify({'message': 'Supplier not found'}), 404

    supplier.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Supplier deleted successfully'})


@suppliers_bp.route('/suppliers/restore', methods=['POST'])
def restore_suppliers():
    data = request.get_json()
    supplier_ids = data.get('supplier_ids')
    if not supplier_ids:
        return jsonify({'message': 'No supplier IDs provided'}), 400

    suppliers_to_restore = Suppliers.query.filter(Suppliers.supplier_id.in_(supplier_ids), Suppliers.is_deleted == True).all()
    for supplier in suppliers_to_restore:
        supplier.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(suppliers_to_restore)} suppliers'})

