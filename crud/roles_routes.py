from flask import Blueprint, jsonify, request
from models import Roles, Users, db

roles_bp = Blueprint('roles_routes', __name__)


@roles_bp.route('/roles', methods=['GET'])
def get_roles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'role_id')
    order = request.args.get('order', 'asc')
    search = request.args.get('search')

    query = Roles.query.filter_by(is_deleted=False)

    if search:
        query = query.filter(Roles.role_name.contains(search))

    if order == 'asc':
        query = query.order_by(getattr(Roles, sort_by).asc())
    else:
        query = query.order_by(getattr(Roles, sort_by).desc())

    roles = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'roles': [role.serialize() for role in roles.items],
        'total': roles.total,
        'pages': roles.pages,
        'current_page': roles.page
    })


@roles_bp.route('/roles/<int:role_id>', methods=['GET'])
def get_role(role_id):
    role = Roles.query.filter_by(role_id=role_id, is_deleted=False).first()
    if not role:
        return jsonify({'message': 'Role not found'}), 404

    return jsonify(role.serialize())


@roles_bp.route('/roles', methods=['POST'])
def create_role():
    data = request.get_json()
    if not data or not data.get('role_name'):
        return jsonify({'message': 'Role name is required'}), 400

    new_role = Roles(role_name=data['role_name'])
    db.session.add(new_role)
    db.session.commit()

    return jsonify({'message': 'Role created successfully', 'role_id': new_role.role_id}), 201


@roles_bp.route('/roles/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    role = Roles.query.filter_by(role_id=role_id, is_deleted=False).first()
    if not role:
        return jsonify({'message': 'Role not found'}), 404

    data = request.get_json()
    role.role_name = data.get('role_name', role.role_name)

    db.session.commit()
    return jsonify({'message': 'Role updated successfully'})


@roles_bp.route('/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    role = Roles.query.filter_by(role_id=role_id, is_deleted=False).first()
    if not role:
        return jsonify({'message': 'Role not found'}), 404

    role.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Role deleted successfully'})


@roles_bp.route('/roles/restore', methods=['POST'])
def restore_roles():
    data = request.get_json()
    role_ids = data.get('role_ids')
    if not role_ids:
        return jsonify({'message': 'No role IDs provided'}), 400

    roles_to_restore = Roles.query.filter(Roles.role_id.in_(role_ids), Roles.is_deleted == True).all()
    for role in roles_to_restore:
        role.is_deleted = False

    db.session.commit()
    return jsonify({'message': f'Restored {len(roles_to_restore)} roles'})
