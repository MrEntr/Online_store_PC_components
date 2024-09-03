import pandas as pd
from flask import send_file
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, expose, actions
from models import db, Categories, Suppliers, Warehouse, Products, WarehouseStock, Roles, Users, Cart, CartItems, \
    ShippingAddresses, Orders, Payments, OrderDetails
import tempfile
import os

admin = Admin(template_mode="bootstrap3")


class ReportableModelView(ModelView):

    @actions.action('generate_report', 'Создать отчет', 'Вы уверены, что хотите создать отчет?')
    def action_generate_report(self, ids):
        # Получаем данные для отчета
        data = self._generate_report_data(ids)

        # Создаем временный файл
        tmp_dir = tempfile.mkdtemp()
        report_path = os.path.join(tmp_dir, 'report.csv')

        # Создаем DataFrame и сохраняем его как CSV
        df = pd.DataFrame(data)
        df.to_csv(report_path, index=False, encoding='utf-8-sig')

        return send_file(report_path, as_attachment=True, download_name='report.csv')

    def _generate_report_data(self, ids):
        raise NotImplementedError("Subclasses should implement this method.")


class CategoriesViews(ReportableModelView):
    column_list = ("category_id", "category_name", "is_deleted")
    column_labels = {
        'category_id': 'ID Категории',
        'category_name': 'Название Категории',
        'is_deleted': 'Удален'
    }
    form_columns = ["category_name"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        categories = Categories.query.filter(Categories.category_id.in_(ids)).all()
        return [{'category_id': category.category_id, 'category_name': category.category_name} for category in
                categories]


class SuppliersView(ReportableModelView):
    column_list = ("supplier_id", "supplier_name", "contact_name", "address", "phone", "is_deleted")
    column_labels = {
        'supplier_id': 'ID Поставщика',
        'supplier_name': 'Имя Поставщика',
        'contact_name': 'Контактное Лицо',
        'address': 'Адрес',
        'phone': 'Телефон',
        'is_deleted': 'Удален'
    }
    form_columns = ["supplier_name", "contact_name", "address", "phone"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        suppliers = Suppliers.query.filter(Suppliers.supplier_id.in_(ids)).all()
        return [{'supplier_id': supplier.supplier_id, 'supplier_name': supplier.supplier_name,
                 'contact_name': supplier.contact_name, 'address': supplier.address, 'phone': supplier.phone}
                for supplier in suppliers]


class WarehouseView(ReportableModelView):
    column_list = ("warehouse_id", "warehouse_name", "address", "capacity", "warehouse_stock", "is_deleted")
    column_labels = {
        'warehouse_id': 'ID Склада',
        'warehouse_name': 'Название Склада',
        'address': 'Адрес',
        'capacity': 'Вместимость',
        'warehouse_stock': 'Запасы на Складе',
        'is_deleted': 'Удален'
    }
    form_columns = ["warehouse_name", "address", "capacity", "warehouse_stock"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        warehouses = Warehouse.query.filter(Warehouse.warehouse_id.in_(ids)).all()
        return [{'warehouse_id': warehouse.warehouse_id, 'warehouse_name': warehouse.warehouse_name,
                 'address': warehouse.address, 'capacity': warehouse.capacity,
                 'warehouse_stock': warehouse.warehouse_stock}
                for warehouse in warehouses]


class ProductsView(ReportableModelView):
    column_list = ("product_id", "product_name", "price", "stock_quantity", "description", "category", "supplier", "is_deleted")
    column_labels = {
        'product_id': 'ID Товара',
        'product_name': 'Название Товара',
        'price': 'Цена',
        'stock_quantity': 'Количество на Складе',
        'description': 'Описание',
        'category': 'Категория',
        'supplier': 'Поставщик',
        'is_deleted': 'Удален'
    }
    form_columns = ["product_name", "price", "stock_quantity", "description", "category", "supplier"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        products = Products.query.filter(Products.product_id.in_(ids)).all()
        return [{'product_id': product.product_id, 'product_name': product.product_name, 'price': product.price,
                 'stock_quantity': product.stock_quantity, 'description': product.description,
                 'category': product.category.category_name, 'supplier': product.supplier.supplier_name}
                for product in products]


class WarehouseStockView(ReportableModelView):
    column_list = ("warehouse_stock_id", "quantity", "product", "warehouse", "is_deleted")
    column_labels = {
        'warehouse_stock_id': 'ID Запаса на Складе',
        'quantity': 'Количество',
        'product': 'Товар',
        'warehouse': 'Склад',
        'is_deleted': 'Удален'
    }
    form_columns = ["quantity", "product", "warehouse"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        stocks = WarehouseStock.query.filter(WarehouseStock.warehouse_stock_id.in_(ids)).all()
        return [{'warehouse_stock_id': stock.warehouse_stock_id, 'quantity': stock.quantity,
                 'product': stock.product.product_name, 'warehouse': stock.warehouse.warehouse_name}
                for stock in stocks]


class RolesView(ReportableModelView):
    column_list = ("role_id", "role_name", "is_deleted")
    column_labels = {
        'role_id': 'ID Роли',
        'role_name': 'Название Роли',
        'is_deleted': 'Удален'
    }
    form_columns = ["role_name"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        roles = Roles.query.filter(Roles.role_id.in_(ids)).all()
        return [{'role_id': role.role_id, 'role_name': role.role_name} for role in roles]


class UsersView(ReportableModelView):
    column_list = ("user_id", "first_name", "last_name", "email", "role", "is_deleted")
    column_labels = {
        'user_id': 'ID Пользователя',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'email': 'Email',
        'role': 'Роль',
        'is_deleted': 'Удален'
    }
    form_columns = ["first_name", "last_name", "email", "role", "is_deleted"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        users = Users.query.filter(Users.user_id.in_(ids)).all()
        return [{'user_id': user.user_id, 'first_name': user.first_name, 'last_name': user.last_name,
                 'email': user.email, 'role': user.role.role_name, 'is_deleted': user.is_deleted}
                for user in users]


class CartView(ReportableModelView):
    column_list = ("cart_id", "created_date", "user", "is_deleted")
    column_labels = {
        'cart_id': 'ID Корзины',
        'created_date': 'Дата Создания',
        'user': 'Пользователь',
        'is_deleted': 'Удален'
    }
    form_columns = ["created_date", "user"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        carts = Cart.query.filter(Cart.cart_id.in_(ids)).all()
        return [{'cart_id': cart.cart_id, 'created_date': cart.created_date, 'user': cart.user.email}
                for cart in carts]


class CartItemsView(ReportableModelView):
    column_list = ("cart_item_id", "quantity", "cart", "product", "is_deleted")
    column_labels = {
        'cart_item_id': 'ID Элемента Корзины',
        'quantity': 'Количество',
        'cart': 'Корзина',
        'product': 'Товар',
        'is_deleted': 'Удален'
    }
    form_columns = ["quantity", "cart", "product"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        cart_items = CartItems.query.filter(CartItems.cart_item_id.in_(ids)).all()
        return [{'cart_item_id': item.cart_item_id, 'quantity': item.quantity,
                 'cart': item.cart.cart_id, 'product': item.product.product_name}
                for item in cart_items]


class ShippingAddressesView(ReportableModelView):
    column_list = ("address_id", "delivery_address", "country", "city", "postal_code", "user", "is_deleted")
    column_labels = {
        'address_id': 'ID Адреса',
        'delivery_address': 'Адрес Доставки',
        'country': 'Страна',
        'city': 'Город',
        'postal_code': 'Почтовый Код',
        'user': 'Пользователь',
        'is_deleted': 'Удален'
    }
    form_columns = ["delivery_address", "country", "city", "postal_code", "user"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        addresses = ShippingAddresses.query.filter(ShippingAddresses.address_id.in_(ids)).all()
        return [{'address_id': address.address_id, 'delivery_address': address.delivery_address,
                 'country': address.country, 'city': address.city, 'postal_code': address.postal_code,
                 'user': address.user.email} for address in addresses]


class OrdersView(ReportableModelView):
    column_list = ("order_id", "order_date", "shipping_address", "user", "is_deleted")
    column_labels = {
        'order_id': 'ID Заказа',
        'order_date': 'Дата Заказа',
        'shipping_address': 'Адрес Доставки',
        'user': 'Пользователь',
        'is_deleted': 'Удален'
    }
    form_columns = ["order_date", "shipping_address", "user"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        orders = Orders.query.filter(Orders.order_id.in_(ids)).all()
        return [{'order_id': order.order_id, 'order_date': order.order_date,
                 'shipping_address': order.shipping_address.delivery_address, 'user': order.user.email}
                for order in orders]


class PaymentsView(ReportableModelView):
    column_list = ("payment_id", "payment_date", "amount", "order", "is_deleted")
    column_labels = {
        'payment_id': 'ID Платежа',
        'payment_date': 'Дата Платежа',
        'amount': 'Сумма',
        'order': 'Заказ',
        'is_deleted': 'Удален'
    }
    form_columns = ["payment_date", "amount", "order"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        payments = Payments.query.filter(Payments.payment_id.in_(ids)).all()
        return [{'payment_id': payment.payment_id, 'payment_date': payment.payment_date,
                 'amount': payment.amount, 'order': payment.order.order_id} for payment in payments]


class OrderDetailsView(ReportableModelView):
    column_list = ("order_detail_id", "quantity", "price", "product", "order", "is_deleted")
    column_labels = {
        'order_detail_id': 'ID Детали Заказа',
        'quantity': 'Количество',
        'price': 'Цена',
        'product': 'Товар',
        'order': 'Заказ',
        'is_deleted': 'Удален'
    }
    form_columns = ["quantity", "price", "product", "order"]
    can_set_page_size = True
    page_size = 10

    def _generate_report_data(self, ids):
        order_details = OrderDetails.query.filter(OrderDetails.order_detail_id.in_(ids)).all()
        return [{'order_detail_id': detail.order_detail_id, 'quantity': detail.quantity,
                 'price': detail.price, 'product': detail.product.product_name, 'order': detail.order.order_id}
                for detail in order_details]


admin.add_view(CategoriesViews(Categories, db.session, name="Категории"))
admin.add_view(SuppliersView(Suppliers, db.session, name="Поставщики"))
admin.add_view(WarehouseView(Warehouse, db.session, name="Склад"))
admin.add_view(ProductsView(Products, db.session, name="Товары"))
admin.add_view(WarehouseStockView(WarehouseStock, db.session, name="Запасы на складе"))
admin.add_view(RolesView(Roles, db.session, name="Роли"))
admin.add_view(UsersView(Users, db.session, name="Пользователи"))
admin.add_view(CartView(Cart, db.session, name="Корзина"))
admin.add_view(CartItemsView(CartItems, db.session, name="Элементы корзины"))
admin.add_view(ShippingAddressesView(ShippingAddresses, db.session, name="Адреса доставки"))
admin.add_view(OrdersView(Orders, db.session, name="Заказы"))
admin.add_view(PaymentsView(Payments, db.session, name="Оплата"))
admin.add_view(OrderDetailsView(OrderDetails, db.session, name="Детали заказа"))
