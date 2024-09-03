from flask import Blueprint, jsonify, request
from models import Products, Categories, Suppliers, db

products_bp = Blueprint('products_routes', __name__)


@products_bp.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'product_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = Products.query.filter_by(is_deleted=False)

    if search:
        query = query.filter(Products.product_name.contains(search) | Products.description.contains(search))

    if order == 'asc':
        query = query.order_by(getattr(Products, sort_by).asc())
    else:
        query = query.order_by(getattr(Products, sort_by).desc())

    products = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'products': [product.serialize() for product in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page
    })


@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Products.query.filter_by(product_id=product_id, is_deleted=False).first()
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    return jsonify(product.serialize())


@products_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data or not data.get('product_name') or not data.get('description') or not data.get('category_id') or not data.get('supplier_id'):
        return jsonify({'message': 'Product name, description, category_id, and supplier_id are required'}), 400

    new_product = Products(
        product_name=data['product_name'],
        price=data.get('price'),
        stock_quantity=data.get('stock_quantity'),
        description=data['description'],
        category_id=data['category_id'],
        supplier_id=data['supplier_id']
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product created successfully', 'product_id': new_product.product_id}), 201


@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Products.query.filter_by(product_id=product_id, is_deleted=False).first()
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    data = request.get_json()
    product.product_name = data.get('product_name', product.product_name)
    product.price = data.get('price', product.price)
    product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
    product.description = data.get('description', product.description)
    product.category_id = data.get('category_id', product.category_id)
    product.supplier_id = data.get('supplier_id', product.supplier_id)

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})


@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Products.query.filter_by(product_id=product_id, is_deleted=False).first()
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    product.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})


@products_bp.route('/products/restore', methods=['POST'])
def restore_products():
    data = request.get_json()
    product_ids = data.get('product_ids')
    if not product_ids:
        return jsonify({'message': 'No product IDs provided'}), 400

    products_to_restore = Products.query.filter(Products.product_id.in_(product_ids), Products.is_deleted == True).all()
    for product in products_to_restore:
        product.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(products_to_restore)} products'})
