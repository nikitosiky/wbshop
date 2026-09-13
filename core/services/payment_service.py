from django.db import transaction
from rest_framework.exceptions import ValidationError


class PaymentService:
    @staticmethod
    @transaction.atomic
    def top_up_balance(user, amount):
        if amount <= 0:
            raise ValidationError("Сумма пополнения должна быть больше 0")

        user.balance += amount
        user.save(update_fields=["balance"])
        return user
