// Kumar QuickCart — dynamic front-end interactions

function updateCartBadge(count) {
  const badge = document.querySelector('.cart-badge');
  const cartLink = document.querySelector('.cart-link');
  if (count > 0) {
    if (badge) {
      badge.textContent = count;
    } else if (cartLink) {
      const span = document.createElement('span');
      span.className = 'cart-badge';
      span.textContent = count;
      cartLink.appendChild(span);
    }
  } else if (badge) {
    badge.remove();
  }
}

async function addToCart(productId, qty = 1, btn = null) {
  try {
    if (btn) { btn.disabled = true; btn.textContent = 'Adding...'; }
    const res = await fetch('/api/cart/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId, qty: qty })
    });
    const data = await res.json();
    if (data.success) {
      updateCartBadge(data.cart_count);
      if (btn) { btn.textContent = '✓ Added'; setTimeout(() => { btn.disabled = false; btn.textContent = 'Add to Cart'; }, 1200); }
    }
  } catch (e) {
    console.error('Cart error', e);
    if (btn) { btn.disabled = false; btn.textContent = 'Add to Cart'; }
  }
}

async function setCartQty(productId, qty) {
  const res = await fetch('/api/cart/set', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId, qty: qty })
  });
  const data = await res.json();
  if (data.success) {
    updateCartBadge(data.cart_count);
    const row = document.querySelector(`.cart-row[data-pid="${productId}"]`);
    if (qty <= 0 && row) { row.remove(); }
    const lineEl = document.querySelector(`#line-total-${productId}`);
    document.querySelectorAll(`.qty-input-${productId}`).forEach(el => el.value = qty);
    const subtotalEl = document.getElementById('cart-subtotal');
    const deliveryEl = document.getElementById('cart-delivery');
    const totalEl = document.getElementById('cart-grandtotal');
    if (subtotalEl) subtotalEl.textContent = '₹' + data.subtotal.toFixed(2);
    if (deliveryEl) deliveryEl.textContent = data.delivery_fee > 0 ? '₹' + data.delivery_fee.toFixed(2) : 'FREE';
    if (totalEl) totalEl.textContent = '₹' + data.grand_total.toFixed(2);
    if (!data.cart_count) { location.reload(); }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Payment method selector on checkout page
  const payOptions = document.querySelectorAll('.pay-option');
  payOptions.forEach(opt => {
    opt.addEventListener('click', () => {
      const radio = opt.querySelector('input[type=radio]');
      radio.checked = true;
      payOptions.forEach(o => o.classList.remove('active'));
      opt.classList.add('active');
      document.querySelectorAll('.pay-detail-box').forEach(b => b.classList.remove('show'));
      const detail = document.getElementById('detail-' + radio.value);
      if (detail) detail.classList.add('show');
    });
  });
});
