document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('menu-items')) {
        loadMenu('Все');
        setupCartButtons();
    }

    if (document.querySelector('.cart-product-pack')) {
        updateCart();
    }
});

document.addEventListener('DOMContentLoaded', () => {
  const images = document.querySelectorAll('img');
  images.forEach(img => {
    const tempImg = new Image();
    tempImg.src = img.src;

    img.onerror = function() {
      this.style.display = 'none';
    };
  });
});

async function loadMenu(category) {
    try {
        const response = await fetch(`/menu?category=${encodeURIComponent(category)}`);
        const items = await response.json();
        renderMenu(items);
    } catch (error) {
        console.error('Ошибка загрузки меню:', error);
    }
}

function renderMenu(items) {
    const container = document.getElementById('menu-items');
    if (!container) return;

    container.innerHTML = items.map(item => `
        <div class="menu-pack">
            <img src="${item.image}" alt="${item.name}">
            <div class="menu-name">${item.name}</div>
            <div class="menu-buy">
                <div class="menu-price">${item.price} руб.</div>
                <button class="add-to-cart" data-id="${item.id}" data-name="${item.name}"
                        data-price="${item.price}" data-image="${item.image}">
                    <img src="static/images/menu-cart.svg" alt="Добавить">
                </button>
            </div>
        </div>
    `).join('');

    setupCartButtons();
}

function setupCartButtons() {
    document.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const item = {
                id: btn.dataset.id,
                name: btn.dataset.name,
                price: parseFloat(btn.dataset.price),
                image: btn.dataset.image
            };
            addToCart(item);
        });
    });
}

function getCart() {
    return JSON.parse(localStorage.getItem('cart')) || [];
}

function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function addToCart(item) {
    const cart = getCart();
    const existing = cart.find(i => i.id === item.id);

    if (existing) {
        existing.quantity = (existing.quantity || 1) + 1;
    } else {
        item.quantity = 1;
        cart.push(item);
    }

    saveCart(cart);
    updateCart();
    alert(`${item.name} добавлен в корзину!`);
}

function updateCart() {
    const cart = getCart();
    const container = document.querySelector('.cart-product-pack');
    const priceContainer = document.querySelector('.cart-price');

    if (!container || !priceContainer) return;

    container.innerHTML = cart.map((item, index) => `
        <div class="cart-product-item">
            <div class='cart-product-card'>
                <img src="${item.image}" alt="${item.name}">
                <div class='cart-product'>${item.name}</div>
                <div class='cart-product-count--'>
                    <div class='price'>${item.price.toFixed(2)}<br>руб.</div>
                    <a class='count-minos' href='#' data-index="${index}">-</a>
                    <div class='count'>${item.quantity}</div>
                    <a class='count-plus' href='#' data-index="${index}">+</a>
                </div>
            </div>
        </div>
    `).join('');

    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    priceContainer.innerHTML = `
        <div class='cart-price-result'>Итого:</div>
        <div class='cart-price-count'>${total.toFixed(2)} руб.</div>
        <a class='cart-price-button' href="{{ url_for('order') }}">оформить заказ</a>
    `;

    document.querySelectorAll('.count-plus').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const index = parseInt(btn.dataset.index);
            const cart = getCart();
            cart[index].quantity += 1;
            saveCart(cart);
            updateCart();
        });
    });

    document.querySelectorAll('.count-minos').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const index = parseInt(btn.dataset.index);
            const cart = getCart();
            if (cart[index].quantity > 1) {
                cart[index].quantity -= 1;
            } else {
                cart.splice(index, 1);
            }
            saveCart(cart);
            updateCart();
        });
    });
}