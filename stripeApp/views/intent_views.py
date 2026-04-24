from Stripetest import settings
from stripeApp.models import Item, Order, OrderItem
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
import stripe


def item_detail(request, id):
    item = Item.objects.get(id=id)
    return render(request, 'item_detail.html', {
        'item': item,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    })


def shop_page(request):
    items = Item.objects.all()

    context = {
        'items': items,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'shop.html', context)


def success_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    context = {
        'order': order,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'success.html', context)


stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateOrderView(APIView):
    EXCHANGE_RATES = {
        'usd': 1,
        'eur': 0.93,
    }

    def to_usd(self, price, currency):
        currency = currency.lower()
        return price / self.EXCHANGE_RATES[currency]

    def from_usd(self, price, currency):
        currency = currency.lower()
        return price * self.EXCHANGE_RATES[currency]

    def post(self, request):
        cart_data = request.data.get('cart', [])
        selected_currency = request.data.get('selected_currency', 'usd').lower()

        if not cart_data:
            return Response({'error': 'Корзина пуста'}, status=400)

        try:
            order = Order.objects.create(status='Pending')

            total_usd = 0

            for item in cart_data:
                product = Item.objects.get(id=item['item_id'])
                quantity = item.get('quantity', 1)

                OrderItem.objects.create(
                    order=order,
                    item=product,
                    quantity=quantity
                )

                price_usd = self.to_usd(product.price, product.currency)
                total_usd += price_usd * quantity

            final_amount = self.from_usd(total_usd, selected_currency)

            stripe.api_key = settings.STRIPE_SECRET_KEY

            intent = stripe.PaymentIntent.create(
                amount=int(final_amount * 100),
                currency=selected_currency,
                metadata={'order_id': order.id}
            )

            order.intent_id = intent.id
            order.save()

            return Response({
                'client_secret': intent.client_secret,
                'order_id': order.id
            })

        except Item.DoesNotExist:
            return Response({'error': 'товар не найден в базе'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

