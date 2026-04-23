from django.shortcuts import render
from django.urls import path
from stripeApp.views import shop_page, CreateOrderView, stripe_webhook_view
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', shop_page, name='shop'),
    path('api/create-order/', CreateOrderView.as_view(), name='api_create_order'),
    path('api/webhook/', stripe_webhook_view, name='stripe_webhook'),
    path('success/', lambda request: render(request, 'success.html'), name='success'),
]