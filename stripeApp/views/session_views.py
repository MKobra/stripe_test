import stripe
from django.shortcuts import redirect, get_object_or_404
from Stripetest import settings
from stripeApp.models import Item


def buy_by_id(request, id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    item = get_object_or_404(Item, id=id)

    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': item.currency.lower(),
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': int(item.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/')
    )
    return redirect(session.url, status=303)