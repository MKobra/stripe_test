from .models import Item, Order, OrderItem
from django.shortcuts import render

def shop_page(request):
    items = Item.objects.all()

    context = {
        'items': items,
    }
    return render(request, 'shop.html', context)


