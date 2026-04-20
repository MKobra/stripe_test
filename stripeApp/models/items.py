from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False, verbose_name="Name")
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    price = models.FloatField(max_length=100, blank=False, null=False, verbose_name="Price")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.price}"

class Meta:
    verbose_name = "Item"
    verbose_name_plural = "Items"