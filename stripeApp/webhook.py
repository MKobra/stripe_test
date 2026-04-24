import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from Stripetest import settings
from stripeApp.models import Order


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded' or event['type'] == 'checkout.session.completed':
        intent = event['data']['object']

        metadata = intent.metadata
        order_id = metadata['order_id'] if 'order_id' in metadata else None

        currency = intent.currency

        if order_id:
            try:
                order = Order.objects.get(id=order_id)

                if order.status != 'Paid':
                    order.status = 'Paid'

                    if currency:
                        order.currency = currency.lower()

                    order.save()

            except Order.DoesNotExist:
                return HttpResponse(status=404)


    return HttpResponse(status=200)