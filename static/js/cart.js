document.addEventListener('DOMContentLoaded', () => {
    updateCartDisplay();
    setupCartEventListeners();
});

function getCart() {
    return JSON.parse(localStorage.getItem('cart')) || [];
}

function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCartDisplay() {
    const cart = getCart();
    const container = document.querySelector('.cart-product-pack');
    const priceContainer = document.querySelector('.cart-price');

    if (!container || !priceContainer) return;

    if (cart.length === 0) {
        container.innerHTML = '<div class="empty-cart">Ваша корзина пуста</div>';
        priceContainer.innerHTML = '';
        return;
    }

    container.innerHTML = cart.map((item, index) => `
        <div class="cart-product-item">
            <div class='cart-product-card'>
                <img src="${item.image}" alt="${item.name}">
                <div class='cart-product'>${item.name}</div>
                <div class='cart-product-count--'>
                    <div class='price'>${item.price.toFixed(2)} руб.</div>
                    <button class='count-btn count-minos' data-index="${index}">-</button>
                    <div class='count'>${item.quantity}</div>
                    <button class='count-btn count-plus' data-index="${index}">+</button>
                </div>
            </div>
        </div>
    `).join('');

    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    priceContainer.innerHTML = `
        <div class='cart-price-result'>Итого:</div>
        <div class='cart-price-count'>${total.toFixed(2)} руб.</div>
        <button class='cart-price-button' id="checkout-button">Оформить заказ</button>
    `;
    document.getElementById('checkout-button')?.addEventListener('click', checkout);
}

function setupCartEventListeners() {
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('count-plus')) {
            const index = e.target.dataset.index;
            updateQuantity(index, 1);
        } else if (e.target.classList.contains('count-minos')) {
            const index = e.target.dataset.index;
            updateQuantity(index, -1);
        }
    });
}

function updateQuantity(index, change) {
    const cart = getCart();
    const item = cart[index];

    if (!item) return;

    item.quantity += change;

    if (item.quantity < 1) {
        cart.splice(index, 1);
    }

    saveCart(cart);
    updateCartDisplay();
}

function checkout() {
    const tableNumber = prompt('Пожалуйста, укажите номер вашего столика:');
    if (tableNumber) {
        const cart = getCart();
        fetch('/order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                cart: cart,
                table_number: tableNumber
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.redirect) {
                localStorage.removeItem('cart');
                window.location.href = data.redirect;
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при оформлении заказа');
        });
    }
}