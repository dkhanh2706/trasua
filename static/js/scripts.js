document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector(".auth-form");
  if (form) {
    form.addEventListener("submit", function (event) {
      const inputs = Array.from(form.querySelectorAll("input[required]"));
      const invalidField = inputs.find((input) => !input.value.trim());
      if (invalidField) {
        invalidField.focus();
      }
    });
  }

  const reveals = document.querySelectorAll(".reveal");
  const revealOnScroll = function () {
    const windowHeight = window.innerHeight;
    reveals.forEach(function (section) {
      const elementTop = section.getBoundingClientRect().top;
      if (elementTop < windowHeight - 80) {
        section.classList.add("active");
      }
    });
  };

  if (reveals.length) {
    revealOnScroll();
    window.addEventListener("scroll", revealOnScroll);
  }
});

// Page Functions
let currentProduct = null;
let cart = [];
let qty = 1;

function openModal(productId) {
  const card = document.querySelector(`.product-card[data-id="${productId}"]`);
  if (!card) return;

  currentProduct = {
    id: card.dataset.id,
    name: card.dataset.name,
    basePrice: parseInt(card.dataset.price),
  };

  qty = 1;

  document.getElementById("modalProductName").textContent = currentProduct.name;
  document.getElementById("modalBasePrice").textContent =
    currentProduct.basePrice;

  // Reset form
  document.querySelector('input[name="size"][value="S"]').checked = true;
  document.getElementById("iceSlider").value = 100;
  document.getElementById("sugarSlider").value = 100;
  document
    .querySelectorAll('input[name="topping"]')
    .forEach((cb) => (cb.checked = false));
  document
    .querySelectorAll('input[name="sauce"]')
    .forEach((cb) => (cb.checked = false));

  // Reset quantity if element exists
  const qtyEl = document.getElementById("qtyValue");
  if (qtyEl) qtyEl.textContent = "1";

  updateIce(100);
  updateSugar(100);
  calculateTotal();

  document.getElementById("orderModal").classList.add("active");
}

function closeModal(event) {
  if (!event || event.target === document.getElementById("orderModal")) {
    document.getElementById("orderModal").classList.remove("active");
  }
}

function updateIce(value) {
  document.getElementById("iceValue").textContent = value;
}

function updateSugar(value) {
  document.getElementById("sugarValue").textContent = value;
}

function changeQty(delta) {
  const qtyEl = document.getElementById("qtyValue");
  if (!qtyEl) return;

  qty += delta;
  if (qty < 1) qty = 1;
  if (qty > 10) qty = 10;
  qtyEl.textContent = qty;
  calculateTotal();
}

function calculateTotal() {
  if (!currentProduct) return 0;

  let total = currentProduct.basePrice;

  const size = document.querySelector('input[name="size"]:checked');
  if (size) total += parseInt(size.dataset.price);

  document.querySelectorAll('input[name="topping"]:checked').forEach((cb) => {
    total += parseInt(cb.dataset.price);
  });

  document.querySelectorAll('input[name="sauce"]:checked').forEach((cb) => {
    total += parseInt(cb.dataset.price);
  });

  // Apply quantity
  total = total * qty;

  document.getElementById("totalPrice").textContent = total;
  return total;
}

// Add event listeners for real-time price update
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('input[name="size"]').forEach((radio) => {
    radio.addEventListener("change", calculateTotal);
  });

  document.querySelectorAll('input[name="topping"]').forEach((cb) => {
    cb.addEventListener("change", calculateTotal);
  });

  document.querySelectorAll('input[name="sauce"]').forEach((cb) => {
    cb.addEventListener("change", calculateTotal);
  });
});

function addToCart() {
  if (!currentProduct) return;

  const size = document.querySelector('input[name="size"]:checked').value;
  const ice = document.getElementById("iceSlider").value;
  const sugar = document.getElementById("sugarSlider").value;

  const toppings = [];
  document.querySelectorAll('input[name="topping"]:checked').forEach((cb) => {
    const label = cb.closest(".topping-option").querySelector(".topping-btn");
    toppings.push(
      label.textContent.replace(" (+10k)", "").replace(" (+15k)", "").trim(),
    );
  });

  const sauces = [];
  document.querySelectorAll('input[name="sauce"]:checked').forEach((cb) => {
    const label = cb.closest(".sauce-option").querySelector(".sauce-btn");
    sauces.push(label.textContent.replace(" (+5k)", "").trim());
  });

  const total = calculateTotal();

  const item = {
    id: Date.now(),
    productId: currentProduct.id,
    name: currentProduct.name,
    size: size,
    ice: ice + "%",
    sugar: sugar + "%",
    toppings: toppings,
    sauces: sauces,
    qty: qty,
    price: total,
  };

  cart.push(item);
  renderCart();
  closeModal();
  document.getElementById("cartSidebar").classList.add("active");
}

function renderCart() {
  const container = document.getElementById("cartItems");

  if (cart.length === 0) {
    container.innerHTML = '<p class="cart-empty">Chưa có sản phẩm nào</p>';
  } else {
    container.innerHTML = cart
      .map(
        (item) => `
      <div class="cart-item">
        <div class="cart-item-info">
          <h4>${item.name}${item.qty > 1 ? ` (x${item.qty})` : ""}</h4>
          <p>Size: ${item.size} | Đá: ${item.ice} | Đường: ${item.sugar}${
            item.toppings && item.toppings.length
              ? " | " + item.toppings.join(", ")
              : ""
          }${
            item.sauces && item.sauces.length
              ? " | Sốt: " + item.sauces.join(", ")
              : ""
          }</p>
        </div>
        <div class="cart-item-price">${item.price}k</div>
        <button class="cart-item-remove" onclick="removeFromCart(${item.id})">&times;</button>
      </div>
    `,
      )
      .join("");
  }

  const total = cart.reduce((sum, item) => sum + item.price, 0);
  document.getElementById("cartTotal").textContent = total + "k";
  document.getElementById("cartCount").textContent = cart.length;
}

function removeFromCart(itemId) {
  cart = cart.filter((item) => item.id !== itemId);
  renderCart();
}

function toggleCart() {
  document.getElementById("cartSidebar").classList.toggle("active");
}

// 3D Carousel Sphere Effect
document.addEventListener("DOMContentLoaded", function () {
  const container = document.querySelector(".carousel-container");
  const track = document.getElementById("bestsellerCarousel");
  if (!container || !track) return;

  const cards = Array.from(track.children);
  const totalCards = cards.length;
  if (totalCards === 0) return;

  const radius = 260;
  const autoRotate = true;
  let autoRotateTimer;
  let isDragging = false;
  let currentAngle = 0;
  let velocity = 0;
  let lastX = 0;

  function positionCards() {
    const angleStep = (2 * Math.PI) / totalCards;
    cards.forEach((card, index) => {
      const angle = currentAngle + index * angleStep;
      const x = Math.sin(angle) * radius;
      const z = Math.cos(angle) * radius - radius;
      const y = Math.sin(angle * 2) * 25;

      card.style.transform = `translate(${x}px, ${y}px) translateZ(${z}px)`;
      card.style.opacity = (z + radius * 1.5) / (radius * 2);
      card.style.zIndex = Math.floor(z + radius);
    });
  }

  function animate() {
    currentAngle += velocity;
    positionCards();
    requestAnimationFrame(animate);
  }

  function startAutoRotate() {
    if (autoRotate) {
      velocity = 0.004;
    }
  }

  function stopAutoRotate() {
    velocity = 0;
  }

  container.addEventListener("mousedown", (e) => {
    isDragging = true;
    lastX = e.clientX;
    stopAutoRotate();
    clearTimeout(autoRotateTimer);
    container.style.cursor = "grabbing";
    e.preventDefault();
  });

  window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    const deltaX = e.clientX - lastX;
    velocity = deltaX * 0.0005;
    currentAngle += deltaX * 0.003;
    lastX = e.clientX;
  });

  window.addEventListener("mouseup", () => {
    if (isDragging) {
      isDragging = false;
      container.style.cursor = "grab";
      autoRotateTimer = setTimeout(startAutoRotate, 2000);
    }
  });

  container.addEventListener("touchstart", (e) => {
    isDragging = true;
    lastX = e.touches[0].clientX;
    stopAutoRotate();
    clearTimeout(autoRotateTimer);
  }, { passive: true });

  container.addEventListener("touchmove", (e) => {
    if (!isDragging) return;
    const touchX = e.touches[0].clientX;
    const deltaX = touchX - lastX;
    velocity = deltaX * 0.0005;
    currentAngle += deltaX * 0.003;
    lastX = touchX;
  }, { passive: true });

  container.addEventListener("touchend", () => {
    isDragging = false;
    autoRotateTimer = setTimeout(startAutoRotate, 2000);
  });

  positionCards();
  animate();
  autoRotateTimer = setTimeout(startAutoRotate, 1500);
});
