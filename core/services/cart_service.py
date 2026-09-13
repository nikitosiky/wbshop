from django.db import transaction
from rest_framework.exceptions import ValidationError

from core.models.cart import Cart, CartItem
from core.models.product import Product


class CartService:
    @staticmethod
    def get_cart(user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def get_item(user):
        cart = CartService.get_item(user=user)
        return cart.items.select_related("product").all

    @staticmethod
    @transaction.atomic
    def add_item(user, product_id, quantity=1):
        cart = CartService.get_cart(user)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError(f"Товар с id={product_id} не найден")

        if quantity < 1:
            raise ValidationError("Количество должно быть больше 0")

        if product.stock_quantity < quantity:
            raise ValidationError(
                f'Недостаточно товара "{product.name}". '
                f"В наличии: {product.stock_quantity}"
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )

        if not created:
            new_quantity = cart_item.quantity + quantity
            if product.stock_quantity < new_quantity:
                raise ValidationError(
                    f'Недостаточно товара "{product.name}". '
                    f"В наличии: {product.stock_quantity}, "
                    f"в корзине уже: {cart_item.quantity}"
                )
            cart_item.quantity = new_quantity
            cart_item.save()

        return cart_item

    @staticmethod
    @transaction.atomic
    def update_quantity(user, item_id, new_quantity):
        try:
            cart_item = CartItem.objects.select_related("product").get(
                id=item_id, cart__user=user
            )
        except CartItem.DoesNotExist:
            raise ValidationError("Позиция корзины не найдена")

        if new_quantity < 1:
            raise ValidationError("Количество должно быть больше 0")

        if cart_item.product.stock_quantity < new_quantity:
            raise ValidationError(
                f'Недостаточно товара "{cart_item.product.name}". '
                f"В наличии: {cart_item.product.stock_quantity}"
            )

        cart_item.quantity = new_quantity
        cart_item.save()
        return cart_item

    @staticmethod
    @transaction.atomic
    def remove_item(user, item_id):
        deleted_count, _ = CartItem.objects.filter(id=item_id, cart__user=user).delete()

        if deleted_count == 0:
            raise ValidationError("Позиция корзины не найдена")

    @staticmethod
    @transaction.atomic
    def clear_cart(user):
        cart = CartService.get_cart(user)
        cart.items.all().delete()
