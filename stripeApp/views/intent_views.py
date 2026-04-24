from Stripetest import settings
from stripeApp.models import Item, Order, OrderItem
from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
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


stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateOrderView(APIView):
    def post(self, request):
        cart_data = request.data.get('cart', [])
        selected_currency = request.data.get('selected_currency', 'usd').lower()
        if not cart_data:
            return Response({'error': 'Корзина пуста'}, status=400)
        try:
            order = Order.objects.create(status='Pending')
            total_price = 0
            for item in cart_data:
                item_id = item.get('item_id')
                product = Item.objects.get(id=item_id)

                OrderItem.objects.create(
                    order=order,
                    item=product,
                    quantity=item.get('quantity')
                )
                total_price += product.price * item.get('quantity')
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=int(total_price * 100),
                currency=selected_currency,
                metadata={'order_id': order.id}
            )
            order.intent_id = intent.id
            order.save()
            return Response({'client_secret': intent.client_secret})

        except Item.DoesNotExist:
            return Response({'error': 'товар не найден в базе'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    print(payload.decode('utf-8'))
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        order_id = intent.metadata['order_id']
        stripe_currency = intent.get('currency')
        if order_id:
            order = Order.objects.get(id=order_id)
            order.status = 'Paid'
            if stripe_currency:
                order.currency = stripe_currency.lower()
            order.save()

    return HttpResponse(status=200)
