from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from core.models.product import Product

User = get_user_model()


class AuthViewsTest(APITestCase):
    def test_register_success(self):
        data = {
            "username": "newuser",
            "email": "new@mail.com",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
        }
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_password_mismatch(self):
        data = {
            "username": "newuser",
            "email": "new@mail.com",
            "password": "SecurePass123",
            "password_confirm": "DifferentPass123",
        }
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(username="testuser", password="Test0000")
        data = {"username": "testuser", "password": "Test0000"}
        response = self.client.post("/api/auth/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


class ProductViewsTest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="Admin0000", is_staff=True
        )
        self.user = User.objects.create_user(username="user", password="User0000")
        self.product = Product.objects.create(
            name="iPhone", price=Decimal("999.00"), stock_quantity=10
        )

    def test_list_products_anonymous(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_product_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "Samsung", "price": "799.00", "stock_quantity": 5}
        response = self.client.post("/api/products/create/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Samsung", "price": "799.00", "stock_quantity": 5}
        response = self.client.post("/api/products/create/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CartViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="Test0000", balance=Decimal("1000.00")
        )
        self.product = Product.objects.create(
            name="iPhone", price=Decimal("100.00"), stock_quantity=10
        )
        self.client.force_authenticate(user=self.user)

    def test_add_to_cart(self):
        data = {"product_id": self.product.id, "quantity": 2}
        response = self.client.post("/api/cart/items/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quantity"], 2)

    def test_add_to_cart_insufficient_stock(self):
        data = {"product_id": self.product.id, "quantity": 20}
        response = self.client.post("/api/cart/items/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_cart(self):
        self.client.post(
            "/api/cart/items/", {"product_id": self.product.id, "quantity": 2}
        )
        response = self.client.get("/api/cart/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cart_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/cart/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="Test0000", balance=Decimal("1000.00")
        )
        self.product = Product.objects.create(
            name="iPhone", price=Decimal("100.00"), stock_quantity=10
        )
        self.client.force_authenticate(user=self.user)

    def test_create_order_success(self):
        self.client.post(
            "/api/cart/items/", {"product_id": self.product.id, "quantity": 2}
        )
        response = self.client.post("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_price"], "200.00")

    def test_create_order_empty_cart(self):
        response = self.client.post("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_list(self):
        response = self.client.get("/api/orders/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
