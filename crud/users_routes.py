from flask import Blueprint, jsonify, request
from models import Users, db

users_bp = Blueprint('users_routes', __name__)


@users_bp.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'user_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = Users.query.filter_by(is_deleted=False)

    if search:
        query = query.filter(Users.first_name.contains(search) | Users.last_name.contains(search))

    if order == 'asc':
        query = query.order_by(getattr(Users, sort_by).asc())
    else:
        query = query.order_by(getattr(Users, sort_by).desc())

    users = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page
    })


@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = Users.query.filter_by(user_id=user_id, is_deleted=False).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify(user.to_dict())


@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = Users.query.filter_by(user_id=user_id, is_deleted=False).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    if 'password' in data:
        user.set_password(data['password'])

    db.session.commit()
    return jsonify({'message': 'User updated successfully'})


@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Users.query.filter_by(user_id=user_id, is_deleted=False).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})


@users_bp.route('/users/restore', methods=['POST'])
def restore_users():
    data = request.get_json()
    user_ids = data.get('user_ids')
    if not user_ids:
        return jsonify({'message': 'No user IDs provided'}), 400

    users_to_restore = Users.query.filter(Users.user_id.in_(user_ids), Users.is_deleted == True).all()
    for user in users_to_restore:
        user.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(users_to_restore)} users'})
