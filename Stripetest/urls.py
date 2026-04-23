from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import path
from stripeApp.views import shop_page, CreateOrderView, stripe_webhook_view, item_detail
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', shop_page, name='shop'),
    path('api/create-order/', CreateOrderView.as_view(), name='api_create_order'),
    path('api/webhook/', stripe_webhook_view, name='stripe_webhook'),
    path('success/', lambda request: render(request, 'success.html'), name='success'),
    path('item/<int:id>/', item_detail, name='item_detail'),
]

User = get_user_model()
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
    else:
        print("ℹАдмин уже существует")
except Exception as e:
    print(f"⚠️ Ошибка при создании админа: {e}")