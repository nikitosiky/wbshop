from django.db import transaction
from rest_framework.exceptions import ValidationError

from core.models.order import Order, OrderItem
from core.services.cart_service import CartService
from core.services.notification_service import NotificationService


class OrderService:

    @staticmethod
    @transaction.atomic
    def create_order(user):
        cart = CartService.get_cart(user)
        cart_items = cart.items.select_related("product").all()

        if not cart_items.exists():
            raise ValidationError("Корзина пуста")

        total_price = 0
        items_to_create = []

        for cart_item in cart_items:
            product = cart_item.product

            if product.stock_quantity < cart_item.quantity:
                raise ValidationError(f'Недостаточно товара "{product.name}". ')

            item_total = product.price * cart_item.quantity
            total_price += item_total

            items_to_create.append(
                {
                    "product": product,
                    "price": product.price,
                    "quantity": cart_item.quantity,
                }
            )

        if user.balance < total_price:
            raise ValidationError(f"Недостаточно средств. ")

        user.balance -= total_price
        user.save(update_fields=["balance"])

        for item_data in items_to_create:
            product = item_data["product"]
            product.stock_quantity -= item_data["quantity"]
            product.save(update_fields=["stock_quantity"])

        order = Order.objects.create(
            user=user, total_price=total_price, status=Order.Status.PENDING
        )

        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=item_data["product"],
                    price=item_data["price"],
                    quantity=item_data["quantity"],
                )
                for item_data in items_to_create
            ]
        )
        CartService.clear_cart(user)
        NotificationService.send_order_notification(order)
        return order

    @staticmethod
    def get_user_orders(user):
        return Order.objects.filter(user=user).prefetch_related("items__product")

    @staticmethod
    def get_order(user, order_id):
        try:
            return Order.objects.prefetch_related("items__product").get(
                id=order_id, user=user
            )
        except Order.DoesNotExist:
            raise ValidationError("Заказ не найден")

    @staticmethod
    @transaction.atomic
    def cancel_order(user, order_id):
        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            raise ValidationError("Заказ не найден")

        if order.status == Order.Status.CANCELLED:
            raise ValidationError("Заказ уже отменён")

        if order.status == Order.Status.COMPLETED:
            raise ValidationError("Нельзя отменить завершённый заказ")

        user.balance += order.total_price
        user.save(update_fields=["balance"])

        for item in order.items.select_related("product").all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save(update_fields=["stock_quantity"])

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])
        NotificationService.send_order_cancelled_notification(order)
        return order
