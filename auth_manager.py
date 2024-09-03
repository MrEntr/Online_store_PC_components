# from models import Users
# from flask import jsonify
# from flask_login import login_required, current_user
#
#
# class AuthManager:
#     def __init__(self, login_manager):
#         self.login_manager = login_manager
#         self.setup_user_loader()
#
#     def setup_user_loader(self):
#         @self.login_manager.user_loader
#         def load_user(user_id):
#             return Users.query.get(int(user_id))
#
#     @staticmethod
#     def role_required(role):
#         def decorator(func):
#             @login_required
#             def wrapper(*args, **kwargs):
#                 if current_user.role.role_name != role:
#                     return jsonify({'message': 'Access denied: insufficient permissions'}), 403
#                 return func(*args, **kwargs)
#             return wrapper
#         return decorator
