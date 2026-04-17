document.addEventListener("DOMContentLoaded", function () {
  const reviewForm = document.getElementById("reviewForm");

  if (!reviewForm) return;

  reviewForm.addEventListener("submit", async function (e) {
    e.preventDefault(); // ❗ chặn reload trang

    const formData = new FormData(reviewForm);

    const data = {
      product: formData.get("product"),
      name: formData.get("review_name"),
      email: formData.get("review_email"),
      rating: formData.get("rating"),
      comment: formData.get("comment"),
    };

    // 👉 validate đơn giản
    if (!data.email.includes("@")) {
      alert("Email không hợp lệ!");
      return;
    }

    try {
      const response = await fetch("/add_review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      alert(result.message || "Gửi đánh giá thành công!");
      reviewForm.reset(); // reset form
    } catch (error) {
      console.error(error);
      alert("Có lỗi xảy ra khi gửi đánh giá!");
    }
  });
});
