import stripe
from django.shortcuts import redirect, get_object_or_404
from Stripetest import settings
from stripeApp.models import Item, Tax, Discount, Order, OrderItem

def buy_by_id(request, id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    item = get_object_or_404(Item, id=id)

    tax = Tax.objects.first()
    discount = Discount.objects.first()

    order = Order.objects.create(
        status='pending',
        tax=tax,
        discount=discount
    )
    OrderItem.objects.create(
        order=order,
        item=item,
        quantity=1,
        currency=item.currency
    )

    tax_rates = [tax.tax_id] if tax else []
    discounts = [{'coupon': discount.coupon_id}] if discount else []

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
            'tax_rates': tax_rates,
        }],
        discounts=discounts,
        mode='payment',
        metadata={'order_id': order.id},
        success_url=request.build_absolute_uri(f'/success/{order.id}/'),
        cancel_url=request.build_absolute_uri('/')
    )

    order.session_id = session.id
    order.save()

    return redirect(session.url, status=303)