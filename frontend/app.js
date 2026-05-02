const state = {
  products: [],
  cart: {},
};

const productGrid = document.querySelector("#productGrid");
const themeFilter = document.querySelector("#themeFilter");
const searchInput = document.querySelector("#searchInput");
const cartItems = document.querySelector("#cartList");
const cartTotal = document.querySelector("#cartTotal");
const orderForm = document.querySelector("#orderForm");
const orderMessage = document.querySelector("#orderMessage");
const newsletterForm = document.querySelector("#newsletterForm");
const newsletterMessage = document.querySelector("#newsletterMessage");

async function fetchProducts() {
  const params = new URLSearchParams();
  if (themeFilter.value) params.set("theme", themeFilter.value);
  if (searchInput.value) params.set("q", searchInput.value);

  const response = await fetch(`/api/products?${params.toString()}`);
  const data = await response.json();
  state.products = data.products;
  renderThemeOptions(data.themes);
  renderProducts();
  renderCart();
}

function renderThemeOptions(themes) {
  const current = themeFilter.value;
  themeFilter.innerHTML = '<option value="">全部主题</option>';
  themes.forEach((theme) => {
    const option = document.createElement("option");
    option.value = theme;
    option.textContent = theme;
    if (theme === current) option.selected = true;
    themeFilter.appendChild(option);
  });
}

function renderProducts() {
  productGrid.innerHTML = "";
  if (state.products.length === 0) {
    productGrid.innerHTML = '<p class="empty">没有找到匹配的木质玩具，试试 pinball、marble run 或 arcade。</p>';
    return;
  }

  state.products.forEach((product) => {
    const card = document.createElement("article");
    card.className = "product-card";
    card.innerHTML = `
      <div class="product-image">${product.image}</div>
      <span class="tag">${product.tag}</span>
      <h3>${product.name}</h3>
      <p>${product.description}</p>
      <div class="product-meta">
        <strong>$${product.price}</strong>
        <span>${product.theme}</span>
      </div>
      <button data-product-id="${product.id}">加入购物车</button>
    `;
    card.querySelector("button").addEventListener("click", () => addToCart(product.id));
    productGrid.appendChild(card);
  });
}

function addToCart(productId) {
  state.cart[productId] = (state.cart[productId] || 0) + 1;
  renderCart();
}

function changeQuantity(productId, quantity) {
  if (quantity <= 0) {
    delete state.cart[productId];
  } else {
    state.cart[productId] = quantity;
  }
  renderCart();
}

function renderCart() {
  const productMap = new Map(state.products.map((product) => [product.id, product]));
  const allKnownProducts = [...state.products];
  Object.keys(state.cart).forEach((productId) => {
    if (!productMap.has(productId)) {
      const saved = window.localStorage.getItem(`product:${productId}`);
      if (saved) allKnownProducts.push(JSON.parse(saved));
    }
  });

  cartItems.innerHTML = "";
  let total = 0;
  Object.entries(state.cart).forEach(([productId, quantity]) => {
    const product = allKnownProducts.find((item) => item.id === productId);
    if (!product) return;
    window.localStorage.setItem(`product:${productId}`, JSON.stringify(product));
    total += product.price * quantity;

    const item = document.createElement("div");
    item.className = "cart-item";
    item.innerHTML = `
      <span>${product.name}</span>
      <div>
        <button aria-label="减少数量">-</button>
        <strong>${quantity}</strong>
        <button aria-label="增加数量">+</button>
      </div>
    `;
    const [minusButton, plusButton] = item.querySelectorAll("button");
    minusButton.addEventListener("click", () => changeQuantity(productId, quantity - 1));
    plusButton.addEventListener("click", () => changeQuantity(productId, quantity + 1));
    cartItems.appendChild(item);
  });

  if (Object.keys(state.cart).length === 0) {
    cartItems.innerHTML = '<p class="muted">购物车还是空的，先挑一款适合亲子共建或礼物场景的木质玩具吧。</p>';
  }
  cartTotal.textContent = `$${total}`;
}

orderForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  orderMessage.textContent = "";

  const formData = new FormData(orderForm);
  const items = Object.entries(state.cart).map(([productId, quantity]) => ({
    productId,
    quantity,
  }));

  const response = await fetch("/api/orders", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      name: formData.get("name"),
      phone: formData.get("phone"),
      address: formData.get("address"),
      items,
    }),
  });
  const data = await response.json();
  orderMessage.textContent = response.ok
    ? `${data.message} 订单号：${data.order.id}`
    : data.error;
  orderMessage.className = response.ok ? "message success" : "message error";

  if (response.ok) {
    state.cart = {};
    orderForm.reset();
    renderCart();
  }
});

newsletterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(newsletterForm);
  const response = await fetch("/api/newsletter", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({email: formData.get("email")}),
  });
  const data = await response.json();
  newsletterMessage.textContent = response.ok ? data.message : data.error;
  newsletterMessage.className = response.ok ? "message success" : "message error";
  if (response.ok) newsletterForm.reset();
});

themeFilter.addEventListener("change", fetchProducts);
searchInput.addEventListener("input", () => {
  window.clearTimeout(searchInput.searchTimer);
  searchInput.searchTimer = window.setTimeout(fetchProducts, 250);
});

fetchProducts();
