from flask import Blueprint, jsonify, request
from models import WarehouseStock, Products, Warehouse, db

warehouse_stock_bp = Blueprint('warehouse_stock_routes', __name__)


@warehouse_stock_bp.route('/warehouse-stock', methods=['GET'])
def get_warehouse_stock():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'warehouse_stock_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = WarehouseStock.query.filter_by(is_deleted=False)

    if search:
        query = query.join(Products).filter(
            Products.product_name.contains(search) | Products.description.contains(search)
        )

    if order == 'asc':
        query = query.order_by(getattr(WarehouseStock, sort_by).asc())
    else:
        query = query.order_by(getattr(WarehouseStock, sort_by).desc())

    warehouse_stock = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'warehouse_stock': [ws.serialize() for ws in warehouse_stock.items],
        'total': warehouse_stock.total,
        'pages': warehouse_stock.pages,
        'current_page': warehouse_stock.page
    })


@warehouse_stock_bp.route('/warehouse-stock/<int:warehouse_stock_id>', methods=['GET'])
def get_warehouse_stock_item(warehouse_stock_id):
    ws_item = WarehouseStock.query.filter_by(warehouse_stock_id=warehouse_stock_id, is_deleted=False).first()
    if not ws_item:
        return jsonify({'message': 'Warehouse stock item not found'}), 404

    return jsonify(ws_item.serialize())


@warehouse_stock_bp.route('/warehouse-stock', methods=['POST'])
def create_warehouse_stock():
    data = request.get_json()
    if not data or not data.get('quantity') or not data.get('product_id') or not data.get('warehouse_id'):
        return jsonify({'message': 'Quantity, product_id, and warehouse_id are required'}), 400

    new_ws_item = WarehouseStock(
        quantity=data['quantity'],
        product_id=data['product_id'],
        warehouse_id=data['warehouse_id']
    )
    db.session.add(new_ws_item)
    db.session.commit()

    return jsonify({'message': 'Warehouse stock item created successfully', 'warehouse_stock_id': new_ws_item.warehouse_stock_id}), 201


@warehouse_stock_bp.route('/warehouse-stock/<int:warehouse_stock_id>', methods=['PUT'])
def update_warehouse_stock(warehouse_stock_id):
    ws_item = WarehouseStock.query.filter_by(warehouse_stock_id=warehouse_stock_id, is_deleted=False).first()
    if not ws_item:
        return jsonify({'message': 'Warehouse stock item not found'}), 404

    data = request.get_json()
    ws_item.quantity = data.get('quantity', ws_item.quantity)
    ws_item.product_id = data.get('product_id', ws_item.product_id)
    ws_item.warehouse_id = data.get('warehouse_id', ws_item.warehouse_id)

    db.session.commit()
    return jsonify({'message': 'Warehouse stock item updated successfully'})


@warehouse_stock_bp.route('/warehouse-stock/<int:warehouse_stock_id>', methods=['DELETE'])
def delete_warehouse_stock(warehouse_stock_id):
    ws_item = WarehouseStock.query.filter_by(warehouse_stock_id=warehouse_stock_id, is_deleted=False).first()
    if not ws_item:
        return jsonify({'message': 'Warehouse stock item not found'}), 404

    ws_item.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Warehouse stock item deleted successfully'})


@warehouse_stock_bp.route('/warehouse-stock/restore', methods=['POST'])
def restore_warehouse_stock():
    data = request.get_json()
    warehouse_stock_ids = data.get('warehouse_stock_ids')
    if not warehouse_stock_ids:
        return jsonify({'message': 'No warehouse stock IDs provided'}), 400

    items_to_restore = WarehouseStock.query.filter(
        WarehouseStock.warehouse_stock_id.in_(warehouse_stock_ids),
        WarehouseStock.is_deleted == True
    ).all()

    for ws_item in items_to_restore:
        ws_item.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(items_to_restore)} warehouse stock items'})
