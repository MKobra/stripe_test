from django.db import models

from stripeApp.models import Item

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, verbose_name="Status", default='')
    intent_id = models.CharField(max_length=255, blank=True, null=True, default=None)

    def total_price(self):
        return sum(i.total_price() for i in self.order_items.all())

    def __str__(self):
        return f"Order {self.id}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    currency = models.CharField(max_length=10, blank=True, null=True)

    def total_price(self):
        return float(self.item.price) * self.quantity

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"