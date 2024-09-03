from flask import Blueprint, jsonify, request
from models import Categories, db
from flask_login import login_required

categories_bp = Blueprint('categories_routes', __name__)


@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'category_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = Categories.query.filter_by(is_deleted=False)

    if search:
        query = query.filter(Categories.category_name.contains(search))

    if order == 'asc':
        query = query.order_by(getattr(Categories, sort_by).asc())
    else:
        query = query.order_by(getattr(Categories, sort_by).desc())

    categories = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'categories': [category.serialize() for category in categories.items],
        'total': categories.total,
        'pages': categories.pages,
        'current_page': categories.page
    })


@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Categories.query.filter_by(category_id=category_id, is_deleted=False).first()
    if not category:
        return jsonify({'message': 'Category not found'}), 404

    return jsonify(category.serialize())


@categories_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data or not data.get('category_name'):
        return jsonify({'message': 'Category name is required'}), 400

    new_category = Categories(category_name=data['category_name'])
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': 'Category created successfully', 'category_id': new_category.category_id}), 201


@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Categories.query.filter_by(category_id=category_id, is_deleted=False).first()
    if not category:
        return jsonify({'message': 'Category not found'}), 404

    data = request.get_json()
    category.category_name = data.get('category_name', category.category_name)

    db.session.commit()
    return jsonify({'message': 'Category updated successfully'})


@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Categories.query.filter_by(category_id=category_id, is_deleted=False).first()
    if not category:
        return jsonify({'message': 'Category not found'}), 404

    category.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'})
