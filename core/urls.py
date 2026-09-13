from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core import views

urlpatterns = [
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/topup/", views.TopUpView.as_view(), name="topup"),
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path(
        "products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"
    ),
    path("products/create/", views.ProductCreateView.as_view(), name="product_create"),
    path(
        "products/<int:pk>/update/",
        views.ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "products/<int:pk>/delete/",
        views.ProductDeleteView.as_view(),
        name="product_delete",
    ),
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/items/", views.AddToCartView.as_view(), name="cart_add"),
    path(
        "cart/items/<int:pk>/", views.UpdateCartItemView.as_view(), name="cart_update"
    ),
    path(
        "cart/items/<int:pk>/delete/",
        views.RemoveFromCartView.as_view(),
        name="cart_remove",
    ),
    path("orders/", views.CreateOrderView.as_view(), name="order_create"),
    path("orders/list/", views.OrderListView.as_view(), name="order_list"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
]
