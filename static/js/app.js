let cart = JSON.parse(localStorage.getItem("dkhanh_cart")) || [];

function saveCart() {
  localStorage.setItem("dkhanh_cart", JSON.stringify(cart));
  updateCartCount();
}

function updateCartCount() {
  const countEl = document.getElementById("cartCount");
  if (countEl) {
    countEl.textContent = cart.length;
  }
}

function renderCartSidebar() {
  const container = document.getElementById("cartItems");
  const totalEl = document.getElementById("cartTotal");
  
  if (!container) return;

  if (cart.length === 0) {
    container.innerHTML = '<p class="cart-empty">Chưa có sản phẩm nào</p>';
    if (totalEl) totalEl.textContent = "0k";
    return;
  }

  let html = "";
  let total = 0;

  cart.forEach((item, index) => {
    total += item.price;
    
    let details = [];
    if (item.size) details.push(item.size);
    if (item.ice && item.ice !== "100") details.push(`Đá:${item.ice}%`);
    if (item.sugar && item.sugar !== "100") details.push(`Đường:${item.sugar}%`);

    html += `
      <div class="cart-item">
        <div class="cart-item-info">
          <h4>${item.name}</h4>
          <p>${details.join(" | ")} ${item.qty ? "x" + item.qty : ""}</p>
        </div>
        <div class="cart-item-price">${item.price}k</div>
      </div>
    `;
  });

  container.innerHTML = html;
  if (totalEl) totalEl.textContent = `${total}k`;
}

let currentProduct = null;
let currentModalBasePrice = 0;

function openModal(productId) {
  const card = document.querySelector(`[data-id="${productId}"]`);
  if (!card) return;

  currentProduct = {
    id: card.dataset.id,
    name: card.dataset.name,
    basePrice: parseInt(card.dataset.price) || parseInt(card.dataset.basePrice) || 0,
  };

  currentModalBasePrice = currentProduct.basePrice;

  document.getElementById("modalProductName").textContent = currentProduct.name;
  document.getElementById("modalBasePrice").textContent = currentProduct.basePrice;
  document.getElementById("totalPrice").textContent = currentProduct.basePrice;

  document.getElementById("orderModal").classList.add("active");

  document.querySelectorAll('input[name="size"]').forEach((radio) => {
    radio.checked = radio.value === "S";
    radio.addEventListener("change", calculateTotal);
  });

  document.getElementById("iceSlider").value = 100;
  document.getElementById("sugarSlider").value = 100;
  document.getElementById("iceValue").textContent = "100";
  document.getElementById("sugarValue").textContent = "100";

  document.querySelectorAll('input[name="topping"]').forEach((cb) => {
    cb.checked = false;
    cb.addEventListener("change", calculateTotal);
  });

  calculateTotal();
}

function closeModal(event) {
  if (event && event.target !== event.currentTarget) return;
  document.getElementById("orderModal").classList.remove("active");
}

function updateIce(value) {
  document.getElementById("iceValue").textContent = value;
}

function updateSugar(value) {
  document.getElementById("sugarValue").textContent = value;
}

function calculateTotal() {
  let total = currentModalBasePrice;

  document.querySelectorAll('input[name="size"]:checked').forEach((radio) => {
    total += parseInt(radio.dataset.price) || 0;
  });

  document.querySelectorAll('input[name="topping"]:checked').forEach((cb) => {
    total += parseInt(cb.dataset.price) || 0;
  });

  document.getElementById("totalPrice").textContent = total;
  return total;
}

function addToCart() {
  if (!currentProduct) return;

  const size = document.querySelector('input[name="size"]:checked')?.value || "S";
  const ice = document.getElementById("iceSlider").value;
  const sugar = document.getElementById("sugarSlider").value;
  
  const toppings = [];
  document.querySelectorAll('input[name="topping"]:checked').forEach((cb) => {
    toppings.push(cb.value);
  });

  const price = calculateTotal();

  const item = {
    id: currentProduct.id,
    name: currentProduct.name,
    size: size,
    ice: ice,
    sugar: sugar,
    toppings: toppings,
    qty: 1,
    price: price,
  };

  cart.push(item);
  saveCart();
  renderCartSidebar();

  closeModal();
  alert(`Đã thêm ${currentProduct.name} vào giỏ hàng!`);
}

function toggleCart() {
  const sidebar = document.getElementById("cartSidebar");
  if (sidebar) {
    sidebar.classList.toggle("active");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  renderCartSidebar();
  updateCartCount();

  const checkoutBtn = document.getElementById("checkoutBtn");

  if (!checkoutBtn) return;

  checkoutBtn.addEventListener("click", async function () {
    window.location.href = "/cart";
  });
});