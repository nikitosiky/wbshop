from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from core.models.product import Product
from core.services.cart_service import CartService
from core.services.order_service import OrderService

User = get_user_model()


class CartServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="Test0", balance=Decimal("1000.00")
        )
        self.product = Product.objects.create(
            name="book", price=Decimal("300"), stock_quantity=12
        )

    def test_add_item_success(self):
        item = CartService.add_item(self.user, self.product.id, 3)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.product, self.product)

    def test_add_item_more(self):
        with self.assertRaises(ValidationError):
            CartService.add_item(self.user, self.product.id, 20)

    def test_update_quantity(self):
        item = CartService.add_item(self.user, self.product.id, 2)
        updated = CartService.update_quantity(self.user, item.id, 5)
        self.assertEqual(updated.quantity, 5)

    def test_update_quantity_exceeds_stock(self):
        item = CartService.add_item(self.user, self.product.id, 2)
        with self.assertRaises(ValidationError):
            CartService.update_quantity(self.user, item.id, 15)

    def test_remove_item(self):
        item = CartService.add_item(self.user, self.product.id, 2)
        CartService.remove_item(self.user, item.id)
        self.assertEqual(self.user.cart.items.count(), 0)

    def test_clear_cart(self):
        CartService.add_item(self.user, self.product.id, 2)
        CartService.clear_cart(self.user)
        self.assertEqual(self.user.cart.items.count(), 0)


class OrderServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassw", balance=Decimal("500.00")
        )
        self.product = Product.objects.create(
            name="book", price=Decimal("100"), stock_quantity=100
        )

    def test_create_order_success(self):
        CartService.add_item(self.user, self.product.id, 2)
        order = OrderService.create_order(self.user)
        self.assertEqual(order.total_price, Decimal("200"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("300"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 98)

    def test_create_empty_order(self):
        with self.assertRaises(ValidationError):
            OrderService.create_order(self.user)

    def test_create_order_without_balance(self):
        self.user.balance = Decimal("99.00")
        CartService.add_item(self.user, self.product.id, 10)
        self.user.save()
        with self.assertRaises(ValidationError):
            OrderService.create_order(self.user)

    def test_create_order_small_stock(self):
        self.product.stock_quantity = 1
        self.product.save()
        with self.assertRaises(ValidationError):
            CartService.add_item(self.user, self.product.id, 10)
