async function buyNow(itemId, currency) {

    const response = await fetch('/api/create-order/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            cart: [{ item_id: itemId, quantity: 1 }],
            selected_currency: currency.toLowerCase()
        })
    });

    const data = await response.json();

    const stripe = Stripe(window.STRIPE_PUBLIC_KEY);

    const elements = stripe.elements({
        clientSecret: data.client_secret
    });

    const paymentElement = elements.create("payment");

    document.getElementById('payment-box').style.display = "block";
    paymentElement.mount("#payment-element");

    document.getElementById('submit-pay').onclick = async () => {

        const result = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: window.location.origin + `/success/${data.order_id}/`
            }
        });

        if (result.error) {
            alert(result.error.message);
        }
    };
}