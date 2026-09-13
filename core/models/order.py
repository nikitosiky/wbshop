from django.db import models

from core.models.product import Product
from core.models.user import User


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "В обработке"
        COMPLETED = "completed", "Завершён"
        CANCELLED = "cancelled", "Отменён"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь",
    )
    total_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Итоговая сумма"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = "orders"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.id} - {self.user.username} ({self.total_price}₽)"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена на момент покупки"
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        db_table = "order_items"
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} x{self.quantity} = {self.total_price}₽"

    @property
    def total_price(self):
        return self.price * self.quantity
