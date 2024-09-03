from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets

from sqlalchemy.dialects.postgresql import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class Categories(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    products = db.relationship("Products", back_populates="category")
    is_deleted = db.Column(db.Boolean, default=False)

    def __str__(self):
        return self.category_name

    def serialize(self):
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'is_deleted': self.is_deleted,
        }


class Suppliers(db.Model):
    supplier_id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(100), nullable=True)
    contact_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    products = db.relationship("Products", back_populates="supplier")
    is_deleted = db.Column(db.Boolean, default=False)

    def __str__(self):
        return self.supplier_name


class Warehouse(db.Model):
    warehouse_id = db.Column(db.Integer, primary_key=True)
    warehouse_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.String(100), nullable=True)
    warehouse_stock = db.relationship("WarehouseStock", back_populates="warehouse")
    is_deleted = db.Column(db.Boolean, default=False)

    def __str__(self):
        return self.warehouse_name

    def serialize(self):
        return {
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse_name,
            'address': self.address,
            'capacity': self.capacity,
            'is_deleted': self.is_deleted,
        }


class Products(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=True)
    price = db.Column(db.DECIMAL(10, 2), nullable=True)
    stock_quantity = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.category_id"))
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.supplier_id"))
    category = db.relationship("Categories", back_populates="products")
    supplier = db.relationship("Suppliers", back_populates="products")
    cart_items = db.relationship("CartItems", back_populates="product")
    order_details = db.relationship("OrderDetails", back_populates="product")
    warehouse_stock = db.relationship("WarehouseStock", back_populates="product")
    is_deleted = db.Column(db.Boolean, default=False)

    def __str__(self):
        return self.product_name

    def serialize(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'price': self.price,
            'stock_quantity': self.stock_quantity,
            'description': self.description,
            'category_id': self.category_id,
            'is_deleted': self.is_deleted,
        }


class WarehouseStock(db.Model):
    warehouse_stock_id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"))
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.warehouse_id"))
    warehouse = db.relationship("Warehouse", back_populates="warehouse_stock")
    product = db.relationship("Products", back_populates="warehouse_stock")
    is_deleted = db.Column(db.Boolean, default=False)

    def __str__(self):
        return str(self.quantity)

    def serialize(self):
        return {
            'warehouse_stock_id': self.warehouse_stock_id,
            'quantity': self.quantity,
            'product_id': self.product_id,
            'warehouse_id': self.warehouse_id,
            'is_deleted': self.is_deleted,

        }


class Roles(db.Model):
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)
    users = db.relationship("Users", back_populates="role")
    is_deleted = db.Column(db.Boolean, default=False)

    def __str__(self):
        return self.role_name

    def serialize(self):
        return {
            'warehouse_stock_id': self.warehouse_stock_id,
            'quantity': self.quantity,
            'product_id': self.product_id,
            'warehouse_id': self.warehouse_id,
            'is_deleted': self.is_deleted,
        }


class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    salt = db.Column(db.String(255), nullable=True)
    token = db.Column(db.String(255), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"))
    role = db.relationship("Roles", back_populates="users")
    cart = db.relationship("Cart", back_populates="user")
    shipping_addresses = db.relationship("ShippingAddresses", back_populates="user")
    orders = db.relationship("Orders", back_populates="user")
    is_deleted = db.Column(db.Boolean, default=False)

    def __str__(self):
        return self.email

    def serialize(self):
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'role_id': self.role_id,
            'is_deleted': self.is_deleted,
        }

    def set_password(self, password):
        self.salt = secrets.token_hex(8)  # Генерируем случайную соль
        self.password_hash = generate_password_hash(password + self.salt)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password + self.salt)

    def generate_token(self):
        self.token = secrets.token_urlsafe(32)  # Генерируем случайный токен

    # def get_user(self, user_id):
    #     try:
    #         self.__cur.execute("SELECT * FROM users WHERE user_id = %s LIMIT 1", (user_id,))
    #         res = self.__cur.fetchone()
    #         if not res:
    #             print("Пользователь не найден")
    #             return False
    #         return res
    #     except psycopg2.Error as e:
    #         print("Ошибка получения данных из БД: " + str(e))
    #         return False


class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    user = db.relationship("Users", back_populates="cart")
    cart_items = db.relationship("CartItems", back_populates="cart")
    is_deleted = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            'cart_id': self.cart_id,
            'created_date': self.created_date,
            'user_id': self.user_id,
            'is_deleted': self.is_deleted,
        }


class CartItems(db.Model):
    cart_item_id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.cart_id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"))
    cart = db.relationship("Cart", back_populates="cart_items")
    product = db.relationship("Products", back_populates="cart_items")
    is_deleted = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            'cart_item_id': self.cart_item_id,
            'quantity': self.quantity,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'is_deleted': self.is_deleted,
        }


class ShippingAddresses(db.Model):
    address_id = db.Column(db.Integer, primary_key=True)
    delivery_address = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    user = db.relationship("Users", back_populates="shipping_addresses")
    orders = db.relationship("Orders", back_populates="shipping_address")
    is_deleted = db.Column(db.Boolean, default=False)

    def __str__(self):
        return self.delivery_address

    def serialize(self):
        return {
            'address_id': self.address_id,
            'delivery_address': self.delivery_address,
            'country': self.country,
            'city': self.city,
            'postal_code': self.postal_code,
            'user_id': self.user_id,
            'is_deleted': self.is_deleted,
        }


class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    address_id = db.Column(db.Integer, db.ForeignKey("shipping_addresses.address_id"))
    customer_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    shipping_address = db.relationship("ShippingAddresses", back_populates="orders")
    user = db.relationship("Users", back_populates="orders")
    payments = db.relationship("Payments", back_populates="order")
    order_details = db.relationship("OrderDetails", back_populates="order")
    is_deleted = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            'order_id': self.order_id,
            'order_date': self.order_date,
            'customer_id': self.customer_id,
            'is_deleted': self.is_deleted,
        }


class Payments(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.DECIMAL(10, 2), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"))
    order = db.relationship("Orders", back_populates="payments")
    is_deleted = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            'payment_id': self.payment_id,
            'payment_date': self.payment_date,
            'amount': self.amount,
            'order_id': self.order_id,
            'is_deleted': self.is_deleted,
        }


class OrderDetails(db.Model):
    order_detail_id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"))
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"))
    product = db.relationship("Products", back_populates="order_details")
    order = db.relationship("Orders", back_populates="order_details")
    is_deleted = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            'order_detail_id': self.order_detail_id,
            'quantity': self.quantity,
            'price': self.price,
            'product_id': self.product_id,
            'order_id': self.order_id,
            'is_deleted': self.is_deleted,
        }
