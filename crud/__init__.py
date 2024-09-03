from flask import Blueprint
from .categories_routes import categories_bp
from .suppliers_routes import suppliers_bp
from .warehouse_routes import warehouse_bp
from .products_routes import products_bp
from .warehouse_stock_routes import warehouse_stock_bp
from .roles_routes import roles_bp
from .users_routes import users_bp
from .cart_routes import cart_bp
from .cart_items_routes import cart_items_bp
from .shipping_addresses_routes import shipping_addresses_bp
from .orders_routes import orders_bp
from .payments_routes import payments_bp
from .order_details_routes import order_details_bp

crud_bp = Blueprint('crud', __name__)


crud_bp.register_blueprint(categories_bp, url_prefix='/api')
crud_bp.register_blueprint(suppliers_bp, url_prefix='/api')
crud_bp.register_blueprint(warehouse_bp, url_prefix='/api')
crud_bp.register_blueprint(products_bp, url_prefix='/api')
crud_bp.register_blueprint(warehouse_stock_bp, url_prefix='/api')
crud_bp.register_blueprint(roles_bp, url_prefix='/api')
crud_bp.register_blueprint(users_bp, url_prefix='/api')
crud_bp.register_blueprint(cart_bp, url_prefix='/api')
crud_bp.register_blueprint(cart_items_bp, url_prefix='/api')
crud_bp.register_blueprint(shipping_addresses_bp, url_prefix='/api')
crud_bp.register_blueprint(orders_bp, url_prefix='/api')
crud_bp.register_blueprint(payments_bp, url_prefix='/api')
crud_bp.register_blueprint(order_details_bp, url_prefix='/api')
