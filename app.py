import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-value"

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


users = load_users()


def get_current_user():
    email = session.get("user_email")
    return users.get(email)

@app.route("/")
def index():
    if get_current_user():
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user():
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Vui lòng nhập email và mật khẩu.", "error")
            return redirect(url_for("login"))

        user = users.get(email)
        if user and user["password"] == password:
            session["user_email"] = email
            flash(f"Đăng nhập thành công, {user['name']}", "success")
            return redirect(url_for("home"))

        flash("Email hoặc mật khẩu không đúng.", "error")
        return redirect(url_for("login"))

    return render_template("login.html", show_nav=False)

@app.route("/register", methods=["GET", "POST"])
def register():
    if get_current_user():
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        admin_code = request.form.get("admin_code", "").strip()

        if not name or not email or not password:
            flash("Vui lòng điền đầy đủ thông tin.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp.", "error")
            return redirect(url_for("register"))

        if email in users:
            flash("Email này đã được đăng ký.", "error")
            return redirect(url_for("register"))

        is_admin = admin_code.lower() == "duykhanh"
        users[email] = {
            "name": name,
            "email": email,
            "password": password,
            "is_admin": is_admin,
        }
        save_users()

        if is_admin:
            flash("Đăng ký admin thành công! Bạn có thể đăng nhập với quyền quản trị.", "success")
        else:
            flash("Đăng ký thành công! Bạn có thể đăng nhập ngay.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", show_nav=False)

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if get_current_user():
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            flash("Vui lòng nhập email.", "error")
            return redirect(url_for("forgot_password"))

        if email not in users:
            flash("Email chưa được đăng ký.", "error")
            return redirect(url_for("forgot_password"))

        flash("Yêu cầu đổi mật khẩu đã được gửi. Vui lòng kiểm tra email (giả lập).", "success")
        return redirect(url_for("login"))

    return render_template("forgot_password.html", show_nav=False)

@app.route("/home")
def home():
    user = get_current_user()
    if not user:
        flash("Vui lòng đăng nhập trước khi truy cập trang chủ.", "error")
        return redirect(url_for("login"))

    return render_template("home.html", user=user, show_nav=True)

@app.route("/milk-tea")
def milk_tea():
    user = get_current_user()
    if not user:
        flash("Vui lòng đăng nhập để xem trang trà sữa.", "error")
        return redirect(url_for("login"))

    products = [
        {"id": "trasua-tran-chau-den", "name": "Trà sữa trân châu đen", "desc": "Vị trà thơm nhẹ, sữa mịn và trân châu mềm dai.", "price": 25, "image": "https://hunufa.vn/wp-content/uploads/2024/10/hinh-ly-tra-sua-dep-4.webp"},
        {"id": "trasua-tran-chau-trang", "name": "Trà sữa trân châu trắng", "desc": "Trân châu trắng dai mềm, vị ngọt thanh.", "price": 28, "image": "https://cdn.hstatic.net/200000921537/file/cach-lam-tra-sua-tran-chau-trang_f7254d6ed471486b8ed72956b25c0476_grande.jpg"},
        {"id": "trasua-thai-xanh", "name": "Trà sữa thái xanh", "desc": "Trà Thái xanh thơm mát, vị đậm đà.", "price": 25, "image": "https://example.com/trasua-thai-xanh.jpg"},
        {"id": "trasua-kem-cheese", "name": "Trà sữa kem cheese", "desc": "Lớp kem cheese béo mặn, hòa quyện vị trà sữa.", "price": 30, "image": "https://example.com/trasua-kem-cheese.jpg"},
        {"id": "tra-dao-kem-cheese", "name": "Trà đào kem cheese", "desc": "Đào tươi ngọt lịm, kem cheese mịn màng.", "price": 32, "image": "https://example.com/tra-dao-kem-cheese.jpg"},
        {"id": "tra-olong-kem-cheese", "name": "Trà ô long kem cheese", "desc": "Trà ô long thơm nồng, kem cheese đậm vị.", "price": 32, "image": "https://example.com/tra-olong-kem-cheese.jpg"},
        {"id": "trasua-matcha", "name": "Trà sữa matcha", "desc": "Matcha Nhật Bản xanh mịn, vị đắng nhẹ.", "price": 30, "image": "https://example.com/trasua-matcha.jpg"},
        {"id": "trasua-socola", "name": "Trà sữa socola", "desc": "Socola ngọt đậm, kết hợp trà sữa mịn.", "price": 28, "image": ""},
        {"id": "trasua-khoai-mon", "name": "Trà sữa khoai môn", "desc": "Khoai môn bùi béo, vị trà thơm nhẹ.", "price": 28, "image": ""},
    ]
    return render_template("milk_tea.html", user=user, show_nav=True, products=products)

@app.route("/che")
def che():
    user = get_current_user()
    if not user:
        flash("Vui lòng đăng nhập để xem trang chè.", "error")
        return redirect(url_for("login"))

    products = [
        {"id": "che-dau-xanh", "name": "Chè đậu xanh", "desc": "Đậu xanh mịn, nấu nhừ, vị thanh mát.", "price": 20, "image": ""},
        {"id": "che-dau-den", "name": "Chè đậu đen", "desc": "Đậu đen bùi bùi, ngọt dịu.", "price": 20, "image": ""},
        {"id": "che-dau-do", "name": "Chè đậu đỏ", "desc": "Đậu đỏ thơm bùi, vị ngọt đậm.", "price": 20, "image": ""},
        {"id": "che-bap", "name": "Chè bắp", "desc": "Bắp mọng nước, ngọt tự nhiên.", "price": 22, "image": ""},
        {"id": "che-khuc-bach", "name": "Chè khúc bạch", "desc": "Khúc bạch dai dai, mịn màng.", "price": 25, "image": ""},
        {"id": "che-thai", "name": "Chè Thái", "desc": "Sầu riêng béo ngậy, thơm nồng.", "price": 28, "image": ""},
        {"id": "che-trai-cay", "name": "Chè trái cây", "desc": "Đủ các loại trái cây tươi ngon.", "price": 25, "image": ""},
        {"id": "che-nha-dam", "name": "Chè nha đam", "desc": "Nha đam mát lạnh, giòn sần.", "price": 22, "image": ""},
        {"id": "che-bo", "name": "Chè bơ", "desc": "Bơ béo ngậy, mịn như kem.", "price": 25, "image": ""},
    ]

    hot_products = [
        {"id": "che-dau-xanh", "name": "Chè đậu xanh", "desc": "Đậu xanh mịn, nấu nhừ, vị thanh mát.", "price": 20, "image": ""},
        {"id": "che-khuc-bach", "name": "Chè khúc bạch", "desc": "Khúc bạch dai dai, mịn màng.", "price": 25, "image": ""},
        {"id": "che-thai", "name": "Chè Thái", "desc": "Sầu riêng béo ngậy, thơm nồng.", "price": 28, "image": ""},
        {"id": "che-trai-cay", "name": "Chè trái cây", "desc": "Đủ các loại trái cây tươi ngon.", "price": 25, "image": ""},
    ]

    return render_template("che.html", user=user, show_nav=True, products=products, hot_products=hot_products)

@app.route("/fried")
def fried():
    user = get_current_user()
    if not user:
        flash("Vui lòng đăng nhập để xem trang đồ chiên.", "error")
        return redirect(url_for("login"))

    products = [
        {"id": "khoai-tay-chien", "name": "Khoai tây chiên", "desc": "Giòn rụm, tẩm gia vị vàng ruộm.", "price": 25, "image": ""},
        {"id": "ga-ran", "name": "Gà rán", "desc": "Gà mềm ngọt, vỏ giòn tan.", "price": 30, "image": ""},
        {"id": "ca-vien-chien", "name": "Cá viên chiên", "desc": "Cá tươi, dai ngon.", "price": 20, "image": ""},
        {"id": "xuc-xich-chien", "name": "Xúc xích chiên", "desc": "Xúc xích giòn ngoài, mềm trong.", "price": 15, "image": ""},
        {"id": "phomai-que", "name": "Phô mai que", "desc": "Phô mai kéo sợi, giòn vàng.", "price": 20, "image": ""},
        {"id": "muc-chien-xu", "name": "Mực chiên xù", "desc": "Mực tươi, giòn rụm.", "price": 35, "image": ""},
        {"id": "tom-chien", "name": "Tôm chiên", "desc": "Tôm to, giòn thơm.", "price": 35, "image": ""},
        {"id": "bach-tuoc-chien", "name": "Bạch tuộc chiên", "desc": "Bạch tuộc dai giòn.", "price": 40, "image": ""},
        {"id": "thanh-cua-chien", "name": "Thanh cua chiên", "desc": "Thanh cua ngọt thịt.", "price": 25, "image": ""},
    ]

    hot_combos = [
        {"id": "combo-1", "name": "Combo 1", "desc": "Khoai tây + Cá viên + Xúc xích", "price": 55, "image": ""},
        {"id": "combo-2", "name": "Combo 2", "desc": "Gà rán + Khoai tây + Nước ngọt", "price": 65, "image": ""},
        {"id": "combo-3", "name": "Combo 3 - Full", "desc": "Mix tất cả đồ chiên", "price": 89, "image": ""},
        {"id": "combo-tra-sua-che", "name": "Combo Trà Sữa + Chè", "desc": "Trà sữa trân châu + Chè đậu xanh", "price": 45, "image": ""},
        {"id": "combo-full-house", "name": "Combo Full House", "desc": "Trà sữa + Chè + Đồ chiên", "price": 99, "image": ""},
    ]

    return render_template("fried.html", user=user, show_nav=True, products=products, hot_combos=hot_combos)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = get_current_user()
    if not user:
        flash("Vui lòng đăng nhập để xem hồ sơ.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not name:
            flash("Vui lòng nhập tên.", "error")
            return redirect(url_for("profile"))

        email = session.get("user_email")
        users[email]["name"] = name

        if new_password:
            if new_password != confirm_password:
                flash("Mật khẩu xác nhận không khớp.", "error")
                return redirect(url_for("profile"))
            users[email]["password"] = new_password

        if "avatar" in request.files:
            file = request.files["avatar"]
            if file and file.filename and allowed_file(file.filename):
                filename = f"avatar_{email.split('@')[0]}.{file.filename.rsplit('.', 1)[1].lower()}"
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                users[email]["avatar"] = f"/static/uploads/{filename}"

        save_users()
        flash("Cập nhật hồ sơ thành công!", "success")
        return redirect(url_for("profile"))

    reviews = session.get("reviews", [
        {"id": 1, "product": "Trà sữa trân châu đen", "rating": 5, "comment": "Rất ngon, trân châu dai!", "date": "2026-04-15"},
        {"id": 2, "product": "Trà sữa thái xanh", "rating": 4, "comment": "Vị trà thơm, sữa mịn.", "date": "2026-04-10"},
        {"id": 3, "product": "Chè đậu xanh", "rating": 5, "comment": "Mát lắm!", "date": "2026-04-05"},
    ])

    return render_template("profile.html", user=user, show_nav=True, reviews=reviews)

@app.route("/add-review", methods=["POST"])
def add_review():
    user = get_current_user()
    if not user:
        flash("Vui lòng đăng nhập để đánh giá.", "error")
        return redirect(url_for("login"))

    product = request.form.get("product", "").strip()
    rating = request.form.get("rating", "").strip()
    comment = request.form.get("comment", "").strip()

    if not product or not rating:
        flash("Vui lòng chọn sản phẩm và đánh giá.", "error")
        return redirect(url_for("profile"))

    from datetime import datetime
    new_review = {
        "id": int(datetime.now().timestamp()),
        "product": product,
        "rating": int(rating),
        "comment": comment,
        "date": datetime.now().strftime("%Y-%m-%d")
    }

    reviews = session.get("reviews", [])
    reviews.insert(0, new_review)
    session["reviews"] = reviews

    flash("Đánh giá của bạn đã được gửi!", "success")
    return redirect(url_for("profile"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất thành công.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
