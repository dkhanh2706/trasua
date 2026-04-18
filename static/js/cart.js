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

function renderCart() {
  const container = document.getElementById("cartItemsContainer");
  const totalEl = document.getElementById("cartTotalAmount");
  
  if (!container) return;

  if (cart.length === 0) {
    container.innerHTML = '<p class="cart-empty-message">Giỏ hàng trống. Hãy thêm món từ <a href="{{ url_for(\'milk_tea\') }}">Trà sữa</a>, <a href="{{ url_for(\'che\') }}">Chè</a>, hoặc <a href="{{ url_for(\'fried\') }}">Đồ chiên</a> nhé!</p>';
    if (totalEl) totalEl.textContent = "0k";
    return;
  }

  let html = "";
  let total = 0;

  cart.forEach((item, index) => {
    total += item.price;
    
    let details = [];
    if (item.size) details.push(`Size: ${item.size}`);
    if (item.ice && item.ice !== "100") details.push(`Đá: ${item.ice}%`);
    if (item.sugar && item.sugar !== "100") details.push(`Đường: ${item.sugar}%`);
    if (item.toppings && item.toppings.length > 0) details.push(`Topping: ${item.toppings.join(", ")}`);
    if (item.sauces && item.sauces.length > 0) details.push(`Sốt: ${item.sauces.join(", ")}`);

    html += `
      <div class="cart-item-card">
        <div class="cart-item-info">
          <h4>${item.name}</h4>
          <p class="cart-item-details">${details.join(" | ")}</p>
          <p class="cart-item-qty">SL: ${item.qty || 1}</p>
        </div>
        <div class="cart-item-price">${item.price}k</div>
        <button class="cart-item-remove" onclick="removeFromCart(${index})">🗑️</button>
      </div>
    `;
  });

  container.innerHTML = html;
  if (totalEl) totalEl.textContent = `${total}k`;
}

function removeFromCart(index) {
  cart.splice(index, 1);
  saveCart();
  renderCart();
  renderCartSidebar();
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

function addToCartShared(item) {
  cart.push(item);
  saveCart();
  renderCartSidebar();
  updateCartCount();
}

function getCartTotal() {
  return cart.reduce((sum, item) => sum + item.price, 0);
}

function clearCart() {
  cart = [];
  saveCart();
}

function openQRModal() {
  const modal = document.getElementById("qrModal");
  if (modal) modal.classList.add("active");
}

function closeQRModal() {
  const modal = document.getElementById("qrModal");
  if (modal) modal.classList.remove("active");
}

function confirmPaid() {
  clearCart();
  closeQRModal();
  renderCart();
  renderCartSidebar();
  updateCartCount();
  alert("Cảm ơn bạn! Chúng tôi sẽ xác nhận đơn hàng.");
}

document.addEventListener("DOMContentLoaded", function () {
  renderCart();
  renderCartSidebar();
  updateCartCount();

  const checkoutBtn = document.getElementById("checkoutBtn");
  if (!checkoutBtn) return;

  checkoutBtn.addEventListener("click", async function () {
    const email = document.getElementById("customerEmail")?.value.trim();
    const paymentMethod = document.querySelector('input[name="payment_method"]:checked')?.value;

    if (!email) {
      alert("Vui lòng nhập email!");
      return;
    }

    if (cart.length === 0) {
      alert("Giỏ hàng trống!");
      return;
    }

    if (!paymentMethod) {
      alert("Vui lòng chọn phương thức thanh toán!");
      return;
    }

    const total = getCartTotal();

    try {
      if (paymentMethod === "bank_transfer") {
        const qrRes = await fetch("/generate-qr", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ amount: total })
        });

        const qrData = await qrRes.json();
        
        if (qrRes.ok) {
          document.getElementById("qrImage").src = qrData.qr_image;
          document.getElementById("qrBank").textContent = qrData.bank;
          document.getElementById("qrAccountNo").textContent = qrData.account_no;
          document.getElementById("qrAccountName").textContent = qrData.account_name;
          document.getElementById("qrAmount").textContent = qrData.amount + "k";
          
          openQRModal();
        } else {
          alert(qrData.error || "Không tạo được QR!");
          return;
        }
      }

      const res = await fetch("/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_email: email,
          items: cart,
          total: total,
          payment_method: paymentMethod
        }),
      });

      const data = await res.json();

      if (res.ok) {
        alert(data.message);
        if (paymentMethod === "email_payment") {
          clearCart();
          renderCart();
          renderCartSidebar();
          updateCartCount();
        }
      } else {
        alert(data.error || "Có lỗi xảy ra!");
      }
    } catch (err) {
      console.error(err);
      alert("Không kết nối được server!");
    }
  });
});