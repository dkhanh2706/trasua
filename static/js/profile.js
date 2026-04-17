document.addEventListener("DOMContentLoaded", function () {
  const reviewForm = document.getElementById("reviewForm");

  if (!reviewForm) return;

  reviewForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const submitBtn = reviewForm.querySelector("button[type='submit']");
    const originalText = submitBtn.innerText;

    const formData = new FormData(reviewForm);

    const data = {
      product: formData.get("product"),
      name: formData.get("review_name"),
      email: formData.get("review_email"),
      rating: formData.get("rating"),
      comment: formData.get("comment"),
    };

    if (
      !data.name ||
      !data.email ||
      !data.product ||
      !data.rating ||
      !data.comment
    ) {
      alert("Vui lòng nhập đầy đủ thông tin.");
      return;
    }

    if (!data.email.includes("@")) {
      alert("Email không hợp lệ.");
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerText = "Đang gửi...";

      const response = await fetch("/add-review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Gửi thất bại");
      }

      alert(result.message || "Gửi đánh giá thành công!");
      reviewForm.reset();
    } catch (error) {
      console.error("Lỗi:", error);
      alert(error.message || "Có lỗi xảy ra khi gửi đánh giá.");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerText = originalText;
    }
  });
});
