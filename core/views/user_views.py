from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers.user_serializers import (
    TopUpSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
from core.services.payment_service import PaymentService


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class TopUpView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TopUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = PaymentService.top_up_balance(
            user=request.user, amount=serializer.validated_data["amount"]
        )

        return Response(UserProfileSerializer(user).data, status=status.HTTP_200_OK)
