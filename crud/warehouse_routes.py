from flask import Blueprint, jsonify, request
from models import Warehouse, WarehouseStock, db

warehouse_bp = Blueprint('warehouse_routes', __name__)


@warehouse_bp.route('/warehouses', methods=['GET'])
def get_warehouses():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'warehouse_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = Warehouse.query.filter_by(is_deleted=False)

    if search:
        query = query.filter(Warehouse.warehouse_name.contains(search) | Warehouse.address.contains(search))

    if order == 'asc':
        query = query.order_by(getattr(Warehouse, sort_by).asc())
    else:
        query = query.order_by(getattr(Warehouse, sort_by).desc())

    warehouses = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'warehouses': [warehouse.serialize() for warehouse in warehouses.items],
        'total': warehouses.total,
        'pages': warehouses.pages,
        'current_page': warehouses.page
    })


@warehouse_bp.route('/warehouses/<int:warehouse_id>', methods=['GET'])
def get_warehouse(warehouse_id):
    warehouse = Warehouse.query.filter_by(warehouse_id=warehouse_id, is_deleted=False).first()
    if not warehouse:
        return jsonify({'message': 'Warehouse not found'}), 404

    return jsonify(warehouse.serialize())


@warehouse_bp.route('/warehouses', methods=['POST'])
def create_warehouse():
    data = request.get_json()
    if not data or not data.get('warehouse_name') or not data.get('address'):
        return jsonify({'message': 'Warehouse name and address are required'}), 400

    new_warehouse = Warehouse(
        warehouse_name=data['warehouse_name'],
        address=data['address'],
        capacity=data.get('capacity'),
    )
    db.session.add(new_warehouse)
    db.session.commit()

    return jsonify({'message': 'Warehouse created successfully', 'warehouse_id': new_warehouse.warehouse_id}), 201


@warehouse_bp.route('/warehouses/<int:warehouse_id>', methods=['PUT'])
def update_warehouse(warehouse_id):
    warehouse = Warehouse.query.filter_by(warehouse_id=warehouse_id, is_deleted=False).first()
    if not warehouse:
        return jsonify({'message': 'Warehouse not found'}), 404

    data = request.get_json()
    warehouse.warehouse_name = data.get('warehouse_name', warehouse.warehouse_name)
    warehouse.address = data.get('address', warehouse.address)
    warehouse.capacity = data.get('capacity', warehouse.capacity)

    db.session.commit()
    return jsonify({'message': 'Warehouse updated successfully'})


@warehouse_bp.route('/warehouses/<int:warehouse_id>', methods=['DELETE'])
def delete_warehouse(warehouse_id):
    warehouse = Warehouse.query.filter_by(warehouse_id=warehouse_id, is_deleted=False).first()
    if not warehouse:
        return jsonify({'message': 'Warehouse not found'}), 404

    warehouse.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Warehouse deleted successfully'})


@warehouse_bp.route('/warehouses/restore', methods=['POST'])
def restore_warehouses():
    data = request.get_json()
    warehouse_ids = data.get('warehouse_ids')
    if not warehouse_ids:
        return jsonify({'message': 'No warehouse IDs provided'}), 400

    warehouses_to_restore = Warehouse.query.filter(Warehouse.warehouse_id.in_(warehouse_ids), Warehouse.is_deleted == True).all()
    for warehouse in warehouses_to_restore:
        warehouse.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(warehouses_to_restore)} warehouses'})
