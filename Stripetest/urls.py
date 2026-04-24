from django.shortcuts import render
from django.urls import path
from stripeApp.views.intent_views import shop_page, CreateOrderView, item_detail
from stripeApp.views.session_views import buy_by_id
from django.contrib import admin

from stripeApp.webhook import stripe_webhook_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', shop_page, name='shop'),
    path('api/create-order/', CreateOrderView.as_view(), name='api_create_order'),
    path('api/webhook/', stripe_webhook_view, name='stripe_webhook'),
    path('success/', lambda request: render(request, 'success.html'), name='success'),
    path('item/<int:id>/', item_detail, name='item_detail'),
    path('buy/<int:id>/', buy_by_id, name='buy_by_id'),
]