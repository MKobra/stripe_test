from django.contrib import admin
from stripeApp.models import Item
from stripeApp.models.orders import Order, OrderItem, Tax, Discount


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price")
    search_fields = ("name",)
    list_filter = ("price",)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ("id", "created_at", "total_price")

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_id")

@admin.register(Discount)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("name", "coupon_id")