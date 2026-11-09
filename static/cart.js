// ============================================================
//  AfinAR — Cart (localStorage)
// ============================================================

const CART_KEY = 'afinar_cart';

function getCart() {
    try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
    catch { return []; }
}

function saveCart(cart) {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
}

function addToCart(id, name, price, qty = 1) {
    const cart = getCart();
    const idx = cart.findIndex(i => i.id === id);
    if (idx >= 0) {
        cart[idx].qty += qty;
    } else {
        cart.push({ id, name, price, qty });
    }
    saveCart(cart);
    updateBadge();
    renderDrawer();
    openDrawer();
    showToast(`"${name}" agregado al carrito`);
}

function removeFromCart(id) {
    saveCart(getCart().filter(i => i.id !== id));
    updateBadge();
    renderDrawer();
}

function setQty(id, qty) {
    qty = parseInt(qty);
    if (isNaN(qty) || qty < 1) { removeFromCart(id); return; }
    const cart = getCart();
    const idx = cart.findIndex(i => i.id === id);
    if (idx >= 0) { cart[idx].qty = qty; saveCart(cart); }
    updateBadge();
    renderDrawer();
}

function getTotal() {
    return getCart().reduce((s, i) => s + i.price * i.qty, 0);
}

function updateBadge() {
    const count = getCart().reduce((s, i) => s + i.qty, 0);
    const badge = document.getElementById('cart-badge');
    if (!badge) return;
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
}

function fmt(n) {
    return '$' + Math.round(n).toLocaleString('es-AR');
}

function renderDrawer() {
    const cart = getCart();
    const list = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');
    if (!list) return;

    if (cart.length === 0) {
        list.innerHTML = `
            <div class="cart-empty">
                <span style="font-size:3rem">🎸</span>
                <p>Tu carrito está vacío</p>
                <p style="font-size:.8rem;color:#555;margin-top:.25rem">¡Explorá el catálogo!</p>
            </div>`;
        if (totalEl) totalEl.textContent = '$0';
        return;
    }

    list.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-info">
                <p class="cart-item-name">${item.name}</p>
                <p class="cart-item-price">${fmt(item.price)} c/u</p>
            </div>
            <div class="cart-item-controls">
                <button class="qty-btn" onclick="setQty(${item.id}, ${item.qty - 1})">−</button>
                <input type="number" class="qty-input" value="${item.qty}" min="1"
                       onchange="setQty(${item.id}, this.value)">
                <button class="qty-btn" onclick="setQty(${item.id}, ${item.qty + 1})">+</button>
                <button class="qty-remove" onclick="removeFromCart(${item.id})">🗑</button>
            </div>
            <p class="cart-item-sub">${fmt(item.price * item.qty)}</p>
        </div>
    `).join('');

    if (totalEl) totalEl.textContent = fmt(getTotal());
}

function openDrawer() {
    document.getElementById('cart-drawer').classList.add('open');
    document.getElementById('cart-overlay').classList.add('show');
    document.body.style.overflow = 'hidden';
    renderDrawer();
}

function closeDrawer() {
    document.getElementById('cart-drawer').classList.remove('open');
    document.getElementById('cart-overlay').classList.remove('show');
    document.body.style.overflow = '';
}

function openCheckout() {
    if (getCart().length === 0) {
        showToast('Tu carrito está vacío', 'warn');
        return;
    }
    closeDrawer();
    document.getElementById('checkout-modal').classList.add('show');
}

function closeCheckout() {
    document.getElementById('checkout-modal').classList.remove('show');
}

// Toast notification
function showToast(msg, type = 'ok') {
    const t = document.createElement('div');
    t.className = 'toast' + (type === 'warn' ? ' toast-warn' : '');
    t.textContent = msg;
    document.body.appendChild(t);
    requestAnimationFrame(() => t.classList.add('visible'));
    setTimeout(() => { t.classList.remove('visible'); setTimeout(() => t.remove(), 400); }, 2800);
}

// Init on load
document.addEventListener('DOMContentLoaded', () => {
    updateBadge();
    renderDrawer();
});
