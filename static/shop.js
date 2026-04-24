let cart = [];

const EXCHANGE_RATES = {
    'usd': 1.0,
    'eur': 0.93
};

function getSelectedCurrency() {
    const el = document.querySelector('input[name="currency-selector"]:checked');
    return el ? el.value : 'usd';
}

function addToCart(id, name, price, currency) {
    price = Number(price);
    currency = currency.toLowerCase();

    if (isNaN(price)) {
        console.error("Invalid price:", price);
        return;
    }

    const item = cart.find(i => i.item_id === id);

    if (item) {
        item.quantity += 1;
    } else {
        cart.push({
            item_id: id,
            name: name,
            base_price: price,
            base_currency: currency,
            quantity: 1
        });
    }
    renderCart();
}

function removeFromCart(id) {
    const index = cart.findIndex(i => i.item_id === id);
    if (index !== -1) {
        if (cart[index].quantity > 1) {
            cart[index].quantity -= 1;
        } else {
            cart.splice(index, 1);
        }
    }
    renderCart();
}


document.addEventListener('change', (e) => {
    if (e.target.classList.contains('currency-radio')) {
        renderCart();
    }
});

function renderCart() {
    const container = document.getElementById('cart-items');
    const summary = document.getElementById('summary-section');
    const totalEl = document.getElementById('total-price');
    const targetCurrency = getSelectedCurrency();

    container.innerHTML = "";
    let total = 0;

    cart.forEach(item => {
        let priceInUsd = item.base_price;
        if (item.base_currency !== 'usd') {
            priceInUsd = item.base_price / EXCHANGE_RATES[item.base_currency];
        }
        let convertedPrice = priceInUsd * EXCHANGE_RATES[targetCurrency];

        let itemTotal = convertedPrice * item.quantity;
        total += itemTotal;

        const div = document.createElement('div');
        div.className = "card mb-2";
        div.innerHTML = `
            <div class="card-body d-flex justify-content-between align-items-center">
                <div>
                    <strong>${item.name}</strong>
                    <span class="badge bg-dark ms-2">x${item.quantity}</span>
                    <small class="text-muted d-block">Оригинал: ${item.base_price} ${item.base_currency.toUpperCase()}</small>
                </div>
                <div>
                    <span class="fw-bold text-primary me-3">
                        ${itemTotal.toFixed(2)} ${targetCurrency.toUpperCase()}
                    </span>
                    <button class="btn btn-sm btn-danger" onclick="removeFromCart(${item.item_id})">-</button>
                </div>
            </div>
        `;
        container.appendChild(div);
    });

    totalEl.innerText = total.toFixed(2);
    document.getElementById('display-currency').innerText = targetCurrency.toUpperCase();
    summary.style.display = cart.length > 0 ? "block" : "none";
}

async function checkout() {
    if (!cart.length) return;

    const targetCurrency = getSelectedCurrency();

    const orderData = cart.map(item => ({
        item_id: item.item_id,
        quantity: item.quantity
    }));

    try {
        const selectedCurrency = document.querySelector('input[name="currency-selector"]:checked').value;

        const response = await fetch('/api/create-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                cart: orderData,
                selected_currency: selectedCurrency
            })
        });

        const data = await response.json();
        if (!data.client_secret) return;

        const stripe = Stripe(window.STRIPE_PUBLIC_KEY);
        const elements = stripe.elements({ clientSecret: data.client_secret });
        const paymentElement = elements.create("payment");

        document.getElementById('payment-box').style.display = "block";
        paymentElement.mount("#payment-element");

        document.getElementById('submit-pay').onclick = async () => {
            const result = await stripe.confirmPayment({
                elements,
                confirmParams: {
                    return_url: window.location.origin + "/success/"
                }
            });
            if (result.error) alert(result.error.message);
        };
    } catch (err) {
        console.error("Checkout error:", err);
    }
}