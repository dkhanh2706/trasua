import json
import os
import io
import base64
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_mail import Mail, Message
from datetime import datetime
from werkzeug.utils import secure_filename
import qrcode

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-value"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "duykhanh1911205@gmail.com"
app.config["MAIL_PASSWORD"] = "pjihyqcnqhktnuev"
app.config["MAIL_DEFAULT_SENDER"] = "duykhanh1911205@gmail.com"

mail = Mail(app)

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

    all_products = [
        {"id": "trasua-tran-chau-den", "name": "Trà sữa trân châu đen", "price": 25, "category": "trasua", "emoji": "🧋"},
        {"id": "trasua-tran-chau-trang", "name": "Trà sữa trân châu trắng", "price": 28, "category": "trasua", "emoji": "🧋"},
        {"id": "trasua-thai-xanh", "name": "Trà sữa thái xanh", "price": 25, "category": "trasua", "emoji": "🍵"},
        {"id": "trasua-kem-cheese", "name": "Trà sữa kem cheese", "price": 30, "category": "trasua", "emoji": "🧀"},
        {"id": "tra-dao-kem-cheese", "name": "Trà đào kem cheese", "price": 32, "category": "trasua", "emoji": "🍑"},
        {"id": "tra-olong-kem-cheese", "name": "Trà ô long kem cheese", "price": 32, "category": "trasua", "emoji": "🍵"},
        {"id": "trasua-matcha", "name": "Trà sữa matcha", "price": 30, "category": "trasua", "emoji": "🍵"},
        {"id": "trasua-socola", "name": "Trà sữa socola", "price": 28, "category": "trasua", "emoji": "🍫"},
        {"id": "trasua-khoai-mon", "name": "Trà sữa khoai môn", "price": 28, "category": "trasua", "emoji": "🥔"},
        {"id": "che-dau-xanh", "name": "Chè đậu xanh", "price": 20, "category": "che", "emoji": "🫘"},
        {"id": "che-dau-den", "name": "Chè đậu đen", "price": 20, "category": "che", "emoji": "🫘"},
        {"id": "che-dau-do", "name": "Chè đậu đỏ", "price": 20, "category": "che", "emoji": "🫘"},
        {"id": "che-bap", "name": "Chè bắp", "price": 22, "category": "che", "emoji": "🌽"},
        {"id": "che-khuc-bach", "name": "Chè khúc bạch", "price": 25, "category": "che", "emoji": "🍮"},
        {"id": "che-thai", "name": "Chè Thái", "price": 28, "category": "che", "emoji": "🥭"},
        {"id": "che-trai-cay", "name": "Chè trái cây", "price": 25, "category": "che", "emoji": "🍓"},
        {"id": "che-nha-dam", "name": "Chè nha đam", "price": 22, "category": "che", "emoji": "🌿"},
        {"id": "che-bo", "name": "Chè bơ", "price": 25, "category": "che", "emoji": "🥑"},
        {"id": "khoai-tay-chien", "name": "Khoai tây chiên", "price": 25, "category": "fried", "emoji": "🍟"},
        {"id": "ga-ran", "name": "Gà rán", "price": 30, "category": "fried", "emoji": "🍗"},
        {"id": "ca-vien-chien", "name": "Cá viên chiên", "price": 20, "category": "fried", "emoji": "🐟"},
        {"id": "xuc-xich-chien", "name": "Xúc xích chiên", "price": 15, "category": "fried", "emoji": "🌭"},
        {"id": "phomai-que", "name": "Phô mai que", "price": 20, "category": "fried", "emoji": "🧀"},
        {"id": "muc-chien-xu", "name": "Mực chiên xù", "price": 35, "category": "fried", "emoji": "🦑"},
        {"id": "tom-chien", "name": "Tôm chiên", "price": 35, "category": "fried", "emoji": "🦐"},
        {"id": "bach-tuoc-chien", "name": "Bạch tuộc chiên", "price": 40, "category": "fried", "emoji": "🐙"},
        {"id": "thanh-cua-chien", "name": "Thanh cua chiên", "price": 25, "category": "fried", "emoji": "🦀"},
    ]

    import random
    bestsellers = random.sample(all_products, 12)

    for i, product in enumerate(bestsellers, start=1):
        product["rank"] = i

    return render_template("home.html", user=user, show_nav=True, bestsellers=bestsellers)

@app.route("/milk-tea")
def milk_tea():
    user = get_current_user()
    if not user:
        flash("Vui lòng đăng nhập để xem trang trà sữa.", "error")
        return redirect(url_for("login"))

    def optimize_pexels(url, width=600):
        url = url.strip()
        if "images.pexels.com" in url:
            if "?" in url:
                return url
            return f"{url}?auto=compress&cs=tinysrgb&w={width}"
        return url

    products = [
        {
            "id": "trasua-tran-chau-den",
            "name": "Trà sữa trân châu đen",
            "desc": "Vị trà thơm nhẹ, sữa mịn và trân châu mềm dai.",
            "price": 25,
            "image": optimize_pexels("https://images.pexels.com/photos/15487855/pexels-photo-15487855.jpeg"),
        },
        {
            "id": "trasua-tran-chau-trang",
            "name": "Trà sữa trân châu trắng",
            "desc": "Trân châu trắng dai mềm, vị ngọt thanh.",
            "price": 28,
            "image": optimize_pexels("https://images.pexels.com/photos/4013151/pexels-photo-4013151.jpeg"),
        },
        {
            "id": "trasua-thai-xanh",
            "name": "Trà sữa thái xanh",
            "desc": "Trà Thái xanh thơm mát, vị đậm đà.",
            "price": 25,
            "image": optimize_pexels("https://images.pexels.com/photos/33766716/pexels-photo-33766716.jpeg"),
        },
        {
            "id": "trasua-kem-cheese",
            "name": "Trà sữa kem cheese",
            "desc": "Lớp kem cheese béo mặn, hòa quyện vị trà sữa.",
            "price": 30,
            "image": optimize_pexels("https://images.pexels.com/photos/33766716/pexels-photo-33766716.jpeg"),
        },
        {
            "id": "tra-dao-kem-cheese",
            "name": "Trà đào kem cheese",
            "desc": "Đào tươi ngọt lịm, kem cheese mịn màng.",
            "price": 32,
            "image": optimize_pexels("https://images.pexels.com/photos/33212324/pexels-photo-33212324.jpeg"),
        },
        {
            "id": "tra-olong-kem-cheese",
            "name": "Trà ô long kem cheese",
            "desc": "Trà ô long thơm nồng, kem cheese đậm vị.",
            "price": 32,
            "image": optimize_pexels("https://images.pexels.com/photos/33766717/pexels-photo-33766717.jpeg"),
        },
        {
            "id": "trasua-matcha",
            "name": "Trà sữa matcha",
            "desc": "Matcha Nhật Bản xanh mịn, vị đắng nhẹ.",
            "price": 30,
            "image": optimize_pexels("https://images.pexels.com/photos/18794176/pexels-photo-18794176.jpeg"),
        },
        {
            "id": "trasua-socola",
            "name": "Trà sữa socola",
            "desc": "Socola ngọt đậm, kết hợp trà sữa mịn.",
            "price": 28,
            "image": optimize_pexels("https://images.pexels.com/photos/4071422/pexels-photo-4071422.jpeg"),
        },
        {
            "id": "trasua-khoai-mon",
            "name": "Trà sữa khoai môn",
            "desc": "Khoai môn bùi béo, vị trà thơm nhẹ.",
            "price": 28,
            "image": optimize_pexels("https://images.pexels.com/photos/5335709/pexels-photo-5335709.jpeg"),
        },
    ]

    return render_template("milk_tea.html", user=user, show_nav=True, products=products)


@app.route("/che")
def che():
    user = get_current_user()
    if not user:
        flash("Vui lòng đăng nhập để xem trang chè.", "error")
        return redirect(url_for("login"))

    def optimize_pexels(url, width=600):
        url = url.strip()
        if "images.pexels.com" in url:
            if "?" in url:
                return url
            return f"{url}?auto=compress&cs=tinysrgb&w={width}"
        return url

    products = [
        {
            "id": "che-dau-xanh",
            "name": "Chè đậu xanh",
            "desc": "Đậu xanh mịn, nấu nhừ, vị thanh mát.",
            "price": 20,
            "image": optimize_pexels("https://images.pexels.com/photos/36211530/pexels-photo-36211530.jpeg"),
        },
        {
            "id": "che-dau-den",
            "name": "Chè đậu đen",
            "desc": "Đậu đen bùi bùi, ngọt dịu.",
            "price": 20,
            "image": optimize_pexels("https://images.pexels.com/photos/5652183/pexels-photo-5652183.jpeg"),
        },
        {
            "id": "che-dau-do",
            "name": "Chè đậu đỏ",
            "desc": "Đậu đỏ thơm bùi, vị ngọt đậm.",
            "price": 20,
            "image": optimize_pexels("https://images.pexels.com/photos/5652183/pexels-photo-5652183.jpeg"),
        },
        {
            "id": "che-bap",
            "name": "Chè bắp",
            "desc": "Bắp mọng nước, ngọt tự nhiên.",
            "price": 22,
            "image": optimize_pexels("https://images.pexels.com/photos/29631481/pexels-photo-29631481.jpeg"),
        },
        {
            "id": "che-khuc-bach",
            "name": "Chè khúc bạch",
            "desc": "Khúc bạch dai dai, mịn màng.",
            "price": 25,
            "image": optimize_pexels("https://images.pexels.com/photos/33212602/pexels-photo-33212602.jpeg"),
        },
        {
            "id": "che-thai",
            "name": "Chè Thái",
            "desc": "Sầu riêng béo ngậy, thơm nồng.",
            "price": 28,
            "image": optimize_pexels("https://images.pexels.com/photos/6063321/pexels-photo-6063321.jpeg"),
        },
        {
            "id": "che-trai-cay",
            "name": "Chè trái cây",
            "desc": "Đủ các loại trái cây tươi ngon.",
            "price": 25,
            "image": optimize_pexels("https://images.pexels.com/photos/1242512/pexels-photo-1242512.jpeg"),
        },
        {
            "id": "che-nha-dam",
            "name": "Chè nha đam",
            "desc": "Nha đam mát lạnh, giòn sần.",
            "price": 22,
            "image": optimize_pexels("https://images.pexels.com/photos/37106997/pexels-photo-37106997.jpeg"),
        },
        {
            "id": "che-bo",
            "name": "Chè bơ",
            "desc": "Bơ béo ngậy, mịn như kem.",
            "price": 25,
            "image": optimize_pexels("https://images.pexels.com/photos/1334130/pexels-photo-1334130.jpeg"),
        },
    ]

    hot_products = [
        {
            "id": "che-dau-xanh",
            "name": "Chè đậu xanh",
            "desc": "Đậu xanh mịn, nấu nhừ, vị thanh mát.",
            "price": 20,
            "image": optimize_pexels("https://images.pexels.com/photos/36211530/pexels-photo-36211530.jpeg"),
        },
        {
            "id": "che-khuc-bach",
            "name": "Chè khúc bạch",
            "desc": "Khúc bạch dai dai, mịn màng.",
            "price": 25,
            "image": optimize_pexels("https://images.pexels.com/photos/33212602/pexels-photo-33212602.jpeg"),
        },
        {
            "id": "che-thai",
            "name": "Chè Thái",
            "desc": "Sầu riêng béo ngậy, thơm nồng.",
            "price": 28,
            "image": optimize_pexels("https://images.pexels.com/photos/6063321/pexels-photo-6063321.jpeg"),
        },
        {
            "id": "che-trai-cay",
            "name": "Chè trái cây",
            "desc": "Đủ các loại trái cây tươi ngon.",
            "price": 25,
            "image": optimize_pexels("https://images.pexels.com/photos/1242512/pexels-photo-1242512.jpeg"),
        },
    ]

    return render_template("che.html", user=user, show_nav=True, products=products, hot_products=hot_products)


@app.route("/fried")
def fried():
    user = get_current_user()
    if not user:
        flash("Vui lòng đăng nhập để xem trang đồ chiên.", "error")
        return redirect(url_for("login"))

    def optimize_pexels(url, width=600):
        url = url.strip()
        if "images.pexels.com" in url:
            if "?" in url:
                return url
            return f"{url}?auto=compress&cs=tinysrgb&w={width}"
        return url

    products = [
        {
            "id": "khoai-tay-chien",
            "name": "Khoai tây chiên",
            "desc": "Giòn rụm, tẩm gia vị vàng ruộm.",
            "price": 25,
            "image": optimize_pexels("https://images.pexels.com/photos/29150162/pexels-photo-29150162.jpeg"),
        },
        {
            "id": "ga-ran",
            "name": "Gà rán",
            "desc": "Gà mềm ngọt, vỏ giòn tan.",
            "price": 30,
            "image": optimize_pexels("https://images.pexels.com/photos/33101857/pexels-photo-33101857.jpeg"),
        },
        {
            "id": "ca-vien-chien",
            "name": "Cá viên chiên",
            "desc": "Cá tươi, dai ngon.",
            "price": 20,
            "image": optimize_pexels("https://images.pexels.com/photos/33297058/pexels-photo-33297058.jpeg"),
        },
        {
            "id": "xuc-xich-chien",
            "name": "Xúc xích chiên",
            "desc": "Xúc xích giòn ngoài, mềm trong.",
            "price": 15,
            "image": optimize_pexels("https://images.pexels.com/photos/32228060/pexels-photo-32228060.jpeg"),
        },
        {
            "id": "phomai-que",
            "name": "Phô mai que",
            "desc": "Phô mai kéo sợi, giòn vàng.",
            "price": 20,
            "image": optimize_pexels("https://images.pexels.com/photos/17121733/pexels-photo-17121733.jpeg"),
        },
        {
            "id": "muc-chien-xu",
            "name": "Mực chiên xù",
            "desc": "Mực tươi, giòn rụm.",
            "price": 35,
            "image": optimize_pexels("https://images.pexels.com/photos/15801007/pexels-photo-15801007.jpeg"),
        },
        {
            "id": "tom-chien",
            "name": "Tôm chiên",
            "desc": "Tôm to, giòn thơm.",
            "price": 35,
            "image": optimize_pexels("https://images.pexels.com/photos/3622477/pexels-photo-3622477.jpeg"),
        },
        {
            "id": "bach-tuoc-chien",
            "name": "Bạch tuộc chiên",
            "desc": "Bạch tuộc dai giòn.",
            "price": 40,
            "image": optimize_pexels("https://images.pexels.com/photos/8352801/pexels-photo-8352801.jpeg"),
        },
        {
            "id": "thanh-cua-chien",
            "name": "Thanh cua chiên",
            "desc": "Thanh cua ngọt thịt.",
            "price": 25,
            "image": optimize_pexels("https://images.pexels.com/photos/35017889/pexels-photo-35017889.jpeg"),
        },
    ]

    hot_combos = [
        {
            "id": "combo-1",
            "name": "Combo 1",
            "desc": "Khoai tây + Cá viên + Xúc xích",
            "price": 55,
            "image": optimize_pexels("https://images.pexels.com/photos/25390054/pexels-photo-25390054.jpeg"),
        },
        {
            "id": "combo-2",
            "name": "Combo 2",
            "desc": "Gà rán + Khoai tây + Nước ngọt",
            "price": 65,
            "image": optimize_pexels("https://images.pexels.com/photos/12362924/pexels-photo-12362924.jpeg"),
        },
        {
            "id": "combo-3",
            "name": "Combo 3 - Full",
            "desc": "Mix tất cả đồ chiên",
            "price": 89,
            "image": optimize_pexels("https://images.pexels.com/photos/29905245/pexels-photo-29905245.jpeg"),
        },
        {
            "id": "combo-tra-sua-che",
            "name": "Combo Trà Sữa + Chè",
            "desc": "Trà sữa trân châu + Chè đậu xanh",
            "price": 45,
            "image": optimize_pexels("https://images.pexels.com/photos/35727299/pexels-photo-35727299.jpeg"),
        },
        {
            "id": "combo-full-house",
            "name": "Combo Full House",
            "desc": "Trà sữa + Chè + Đồ chiên",
            "price": 99,
            "image": optimize_pexels("https://images.pexels.com/photos/35727301/pexels-photo-35727301.jpeg"),
        },
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
        return jsonify({"message": "Vui lòng đăng nhập để đánh giá."}), 401

    try:
        data = request.get_json()

        if not data:
            return jsonify({"message": "Không nhận được dữ liệu."}), 400

        product = data.get("product", "").strip()
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        rating = str(data.get("rating", "")).strip()
        comment = data.get("comment", "").strip()

        if not product or not rating or not name or not email:
            return jsonify({"message": "Vui lòng nhập đầy đủ thông tin."}), 400

        new_review = {
            "id": int(datetime.now().timestamp()),
            "product": product,
            "name": name,
            "email": email,
            "rating": int(rating),
            "comment": comment,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        reviews = session.get("reviews", [])
        reviews.insert(0, new_review)
        session["reviews"] = reviews

        # Gửi email cảm ơn
        msg = Message(
            subject="Cảm ơn bạn đã gửi đánh giá",
            recipients=[email]
        )

        msg.body = f"""
Xin chào {name},

Cảm ơn ní đã gửi đánh giá cho sản phẩm: {product}.

Chúng tôi đã ghi nhận phản hồi của bạn:
- Số sao: {rating}
- Nội dung: {comment}

Phản hồi của fen rất quan trọng và tôi cải thiện dịch vụ tốt hơn.

Trân trọng,
Duy Khánh
"""
        mail.send(msg)

        return jsonify({"message": "Gửi đánh giá và email cảm ơn thành công!"}), 200

    except Exception as e:
        print("Lỗi add_review:", e)
        return jsonify({"message": f"Có lỗi xảy ra: {str(e)}"}), 500

@app.route("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất thành công.", "success")
    return redirect(url_for("login"))

@app.route("/cart")
def cart():
    user = get_current_user()
    if not user:
        flash("Vui lòng đăng nhập để xem giỏ hàng.", "error")
        return redirect(url_for("login"))
    return render_template("cart.html", user=user, show_nav=True)

@app.route("/generate-qr", methods=["POST"])
def generate_qr():
    try:
        data = request.get_json()
        amount = data.get("amount", 0)
        
        bank_id = "BIDV"
        account_no = "0963176945"
        account_name = "Hoàng Duy Khánh"
        template = "compact"
        
        qr_content = f"https://img.vietqr.io/image/{bank_id}-{account_no}-{template}.png?amount={amount}&addInfo=Thanh+toan+don+hang+DKhanh+Tea+House"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            "qr_image": f"data:image/png;base64,{img_base64}",
            "qr_url": qr_content,
            "bank": bank_id,
            "account_no": account_no,
            "account_name": account_name,
            "amount": amount
        })
    except Exception as e:
        print("Lỗi generate_qr:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/checkout", methods=["POST"])
def checkout():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Vui lòng đăng nhập để thanh toán."}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Không nhận được dữ liệu đơn hàng."}), 400

        payment_method = data.get("payment_method", "")
        customer_email = data.get("customer_email", "").strip()
        items = data.get("items", [])
        total = data.get("total", 0)
        
        if not customer_email:
            return jsonify({"error": "Vui lòng nhập email."}), 400
        if not items:
            return jsonify({"error": "Giỏ hàng trống."}), 400
        if not payment_method:
            return jsonify({"error": "Vui lòng chọn phương thức thanh toán."}), 400

        order_lines = []
        for idx, item in enumerate(items, start=1):
            name = item.get("name", "Không rõ")
            size = item.get("size", "")
            ice = item.get("ice", "")
            sugar = item.get("sugar", "")
            toppings = item.get("toppings", [])
            sauces = item.get("sauces", [])
            qty = item.get("qty", 1)
            price = item.get("price", 0)

            toppings_text = ", ".join(toppings) if toppings else "Không"
            sauces_text = ", ".join(sauces) if sauces else "Không"

            order_lines.append(
                f"""{idx}. {name}
- Size: {size}
- Đá: {ice}
- Đường: {sugar}
- Topping: {toppings_text}
- Sốt: {sauces_text}
- Số lượng: {qty}
- Giá: {price}k"""
            )

        order_detail = "\n\n".join(order_lines)

        if payment_method == "bank_transfer":
            admin_msg = Message(
                subject=f"Đơn hàng mới - Chuyển khoản - {total}k",
                recipients=[app.config["MAIL_USERNAME"]]
            )
            admin_msg.body = f"""
Có đơn hàng mới từ website (Thanh toán chuyển khoản).

Khách hàng: {user.get('name', 'Không rõ')}
Email khách: {customer_email}

Chi tiết đơn hàng:
{order_detail}

Tổng tiền: {total}k
Phương thức: Chuyển khoản BIDV - 0963176945
"""
            mail.send(admin_msg)

            customer_msg = Message(
                subject="Xác nhận đơn hàng - DKhanh Tea House",
                recipients=[customer_email]
            )
            customer_msg.body = f"""
Xin chào {user.get('name', 'bạn')},

Cảm ơn bạn đã đặt hàng tại DKhanh Tea House.

Chi tiết đơn hàng:
{order_detail}

Tổng tiền: {total}k

Phương thức thanh toán: Chuyển khoản BIDV
Số tài khoản: 0963176945
Tên: Hoàng DUY KHÁNH
Nội dung: Thanh toan don hang DKhanh Tea House

Vui lòng chuyển khoản. Chúng tôi sẽ xác nhận sau khi nhận được tiền.

Trân trọng,
DKhanh Tea House
"""
            mail.send(customer_msg)
            return jsonify({"message": "Đơn hàng đã được xác nhận! Cảm ơn bạn đã đặt hàng.", "payment_method": "bank_transfer"}), 200
        
        elif payment_method == "email_payment":
            admin_msg = Message(
                subject=f"Đơn hàng mới - Thanh toán qua email - {total}k",
                recipients=[app.config["MAIL_USERNAME"]]
            )
            admin_msg.body = f"""
Có đơn hàng mới từ website (Thanh toán qua email).

Khách hàng: {user.get('name', 'Không rõ')}
Email khách: {customer_email}

Chi tiết đơn hàng:
{order_detail}

Tổng tiền: {total}k
Phương thức: Thanh toán qua email
"""
            mail.send(admin_msg)

            customer_msg = Message(
                subject="Xác nhận đơn hàng - DKhanh Tea House",
                recipients=[customer_email]
            )
            customer_msg.body = f"""
Xin chào {user.get('name', 'bạn')},

Cảm ơn bạn đã đặt hàng tại DKhanh Tea House.

Chi tiết đơn hàng:
{order_detail}

Tổng tiền: {total}k

Phương thức thanh toán: Thanh toán qua email
Chúng tôi sẽ gửi hóa đơn chi tiết qua email sau.

Trân trọng,
DKhanh Tea House
"""
            mail.send(customer_msg)
            return jsonify({"message": "Đơn hàng đã được xác nhận! Chúng tôi sẽ gửi email thanh toán cho bạn.", "payment_method": "email_payment"}), 200

        return jsonify({"error": "Phương thức thanh toán không hợp lệ."}), 400

    except Exception as e:
        print("Lỗi checkout:", e)
        return jsonify({"error": f"Có lỗi xảy ra: {str(e)}"}), 500

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    current_admin = users.get(session.get("admin_email"))
    if current_admin:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Vui lòng nhập email và mật khẩu.", "error")
            return redirect(url_for("admin_login"))

        user = users.get(email)
        if user and user["password"] == password and user.get("is_admin", False):
            session["admin_email"] = email
            flash(f"Đăng nhập admin thành công!", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Email hoặc mật khẩu không đúng hoặc không có quyền admin.", "error")
        return redirect(url_for("admin_login"))

    return render_template("admin_login.html")

def get_current_admin():
    email = session.get("admin_email")
    return users.get(email)

@app.route("/admin")
def admin_dashboard():
    admin_user = get_current_admin()
    if not admin_user:
        flash("Vui lòng đăng nhập admin để truy cập trang quản trị.", "error")
        return redirect(url_for("admin_login"))
    
    if not admin_user.get("is_admin", False):
        flash("Bạn không có quyền truy cập trang quản trị.", "error")
        return redirect(url_for("admin_login"))
    
    user_list = []
    for email, u in users.items():
        user_list.append({
            "email": email,
            "name": u.get("name"),
            "is_admin": u.get("is_admin", False)
        })
    
    return render_template("admin.html", user=admin_user, users=user_list)

@app.route("/admin/change-password", methods=["POST"])
def admin_change_password():
    admin_user = get_current_admin()
    if not admin_user or not admin_user.get("is_admin", False):
        flash("Bạn không có quyền thực hiện thao tác này.", "error")
        return redirect(url_for("admin_login"))
    
    target_email = request.form.get("email", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()
    
    if not target_email or not new_password:
        flash("Vui lòng nhập đầy đủ thông tin.", "error")
        return redirect(url_for("admin_dashboard"))
    
    if target_email not in users:
        flash("Người dùng không tồn tại.", "error")
        return redirect(url_for("admin_dashboard"))
    
    if target_email == admin_user["email"]:
        flash("Bạn không thể đổi mật khẩu cho ch��nh mình tại đây.", "error")
        return redirect(url_for("admin_dashboard"))
    
    if new_password != confirm_password:
        flash("Mật khẩu xác nhận không khớp.", "error")
        return redirect(url_for("admin_dashboard"))
    
    users[target_email]["password"] = new_password
    save_users()
    flash(f"Đã đổi mật khẩu cho {users[target_email]['name']}.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete-user", methods=["POST"])
def admin_delete_user():
    admin_user = get_current_admin()
    if not admin_user or not admin_user.get("is_admin", False):
        flash("Bạn không có quyền thực hiện thao tác này.", "error")
        return redirect(url_for("admin_login"))
    
    target_email = request.form.get("email", "").strip()
    
    if not target_email:
        flash("Email không hợp lệ.", "error")
        return redirect(url_for("admin_dashboard"))
    
    if target_email not in users:
        flash("Người dùng không tồn tại.", "error")
        return redirect(url_for("admin_dashboard"))
    
    if target_email == admin_user["email"]:
        flash("Bạn không thể xóa tài khoản của chính mình.", "error")
        return redirect(url_for("admin_dashboard"))
    
    target_name = users[target_email]["name"]
    del users[target_email]
    save_users()
    flash(f"Đã xóa tài khoản của {target_name}.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_email", None)
    flash("Đăng xuất admin thành công.", "success")
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(debug=True)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)