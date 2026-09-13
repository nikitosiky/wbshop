from django.contrib import admin

from core.models.cart import Cart, CartItem
from core.models.order import Order, OrderItem
from core.models.product import Product
from core.models.user import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email", "balance", "is_staff"]
    search_fields = ["username", "email"]
    list_filter = ["is_staff", "is_active"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "price", "stock_quantity", "created_at"]
    search_fields = ["name"]
    list_filter = ["created_at"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_at"]
    search_fields = ["user__username"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["id", "cart", "product", "quantity", "total_price"]
    search_fields = ["cart__user__username", "product__name"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "total_price", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__username"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "product", "price", "quantity", "total_price"]
