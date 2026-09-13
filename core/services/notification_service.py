import logging

logger = logging.getLogger(__name__)


class NotificationService:

    @staticmethod
    def send_order_notification(order):
        items_count = order.items.count()
        logger.info(
            f"Заказ #{order.id} создан. "
            f"Пользователь: {order.user.username}, "
            f"Сумма: {order.total_price}₽, "
            f"Товаров: {items_count}"
        )

    @staticmethod
    def send_order_cancelled_notification(order):
        logger.info(
            f"Заказ #{order.id} отменён. "
            f"Пользователь: {order.user.username}, "
            f"Сумма: {order.total_price}₽"
        )
