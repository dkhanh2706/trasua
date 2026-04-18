document.addEventListener("DOMContentLoaded", function () {
  const checkoutBtn = document.getElementById("checkoutBtn");

  if (!checkoutBtn) return;

  checkoutBtn.addEventListener("click", async function () {
    const email = document.getElementById("customerEmail").value.trim();

    if (!email) {
      alert("Vui lòng nhập email!");
      return;
    }

    if (cart.length === 0) {
      alert("Giỏ hàng trống!");
      return;
    }

    const total = cart.reduce((sum, item) => sum + item.price, 0);

    try {
      const res = await fetch("/checkout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          customer_email: email,
          items: cart,
          total: total,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        alert("Thanh toán thành công! Email đã được gửi.");
        cart = [];
        renderCart();
      } else {
        alert(data.error || "Có lỗi xảy ra!");
      }
    } catch (err) {
      console.error(err);
      alert("Không kết nối được server!");
    }
  });
});
