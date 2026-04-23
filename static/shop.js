
let cart = [];

function addToCart(id, name, price) {

    price = Number(price);

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
            price: price,
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

function renderCart() {
    const container = document.getElementById('cart-items');
    const summary = document.getElementById('summary-section');
    const totalEl = document.getElementById('total-price');

    container.innerHTML = "";

    let total = 0;

    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        const div = document.createElement('div');
        div.className = "card mb-2";

        div.innerHTML = `
            <div class="card-body d-flex justify-content-between align-items-center">
                <div>
                    <strong>${item.name}</strong>
                    <span class="badge bg-dark ms-2">x${item.quantity}</span>
                </div>

                <div>
                    <span class="fw-bold text-primary me-3">
                        ${itemTotal.toFixed(2)} $
                    </span>

                    <button class="btn btn-sm btn-danger"
                            onclick="removeFromCart(${item.item_id})">
                        -
                    </button>
                </div>
            </div>
        `;

        container.appendChild(div);
    });

    totalEl.innerText = total.toFixed(2);

    summary.style.display = cart.length > 0 ? "block" : "none";
}

async function checkout() {

    if (!cart.length) return;

    const orderData = cart.map(item => ({
        item_id: item.item_id,
        quantity: item.quantity
    }));

    try {
        const response = await fetch('/api/create-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ cart: orderData })
        });

        const data = await response.json();

        if (!data.client_secret) {
            console.error("No client_secret:", data);
            return;
        }

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
                    return_url: window.location.origin + "/success/"
                }
            });

            if (result.error) {
                alert(result.error.message);
            }
        };

    } catch (err) {
        console.error("Checkout error:", err);
    }
}


async function buyNow(itemId) {

    const response = await fetch('/api/create-order/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            cart: [{ item_id: itemId, quantity: 1 }]
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
                return_url: window.location.origin + "/success/"
            }
        });

        if (result.error) {
            alert(result.error.message);
        }
    };
}