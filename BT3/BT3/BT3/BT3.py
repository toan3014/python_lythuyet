from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask import url_for

app = Flask(__name__)

# Cấu hình kết nối cơ sở dữ liệu MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456789@localhost/library_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secretkey'  # Cần thiết cho việc bảo mật phiên làm việc
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Định nghĩa mô hình Sách
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(50), unique=True, nullable=False)
    available = db.Column(db.Boolean, default=False)  # Trạng thái có sẵn hay không

# Định nghĩa mô hình Người dùng (Thư viện)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(200), nullable=False)  # Lưu mật khẩu đã mã hóa

# Định nghĩa mô hình Mượn sách
class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    user = db.relationship('User', backref='borrows', lazy=True)
    book = db.relationship('Book', backref='borrows', lazy=True)

with app.app_context():
    db.create_all()

# Hàm load người dùng từ ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Trang chủ - Hiển thị danh sách sách
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    search_query = request.form.get('search')  # Lấy từ form tìm kiếm
    if search_query:
        # Tìm sách theo tên, tác giả hoặc ISBN
        books = Book.query.filter(
            Book.title.like(f'%{search_query}%') |
            Book.author.like(f'%{search_query}%') |
            Book.isbn.like(f'%{search_query}%')
        ).all()
    else:
        books = Book.query.all()  # Nếu không có tìm kiếm, hiển thị tất cả sách

    return render_template('book_list.html', books=books)

# Đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):  # Kiểm tra mật khẩu đã mã hóa
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Đăng nhập không thành công, vui lòng kiểm tra lại thông tin!', 'danger')

    return render_template('login.html')

# Đăng ký tài khoản
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        address = request.form['address']  # Lấy địa chỉ từ form

        if password != confirm_password:
            flash('Mật khẩu không khớp, vui lòng thử lại!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email đã được đăng ký, vui lòng chọn email khác!', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(name=name, email=email, password=hashed_password, address=address)  # Lưu địa chỉ

        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký thành công! Bạn có thể đăng nhập ngay.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Đăng xuất
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_user', methods=['GET', 'POST'])
@login_required  # Chỉ người dùng đăng nhập mới có thể thêm thành viên
def add_user():
    if request.method == 'POST':
        # Xử lý thêm thành viên
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        address = request.form['address']

        # Kiểm tra các điều kiện
        if password != confirm_password:
            flash('Mật khẩu không khớp, vui lòng thử lại!', 'danger')
            return redirect(url_for('add_user'))

        if User.query.filter_by(email=email).first():
            flash('Email đã được đăng ký, vui lòng chọn email khác!', 'danger')
            return redirect(url_for('add_user'))

        # Lưu thành viên mới vào cơ sở dữ liệu
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(name=name, email=email, password=hashed_password, address=address)
        db.session.add(new_user)
        db.session.commit()

        flash('Thêm thành viên thành công!', 'success')
        return redirect(url_for('index'))  # Redirect về trang chủ

    return render_template('add_user.html')  # Render trang thêm thành viên

# Thêm sách mới
@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        
        new_book = Book(title=title, author=author, isbn=isbn)
        db.session.add(new_book)
        db.session.commit()
        
        flash("Thêm sách thành công!", 'success')
        return redirect(url_for('index'))
    
    return render_template('add_book.html')

# Mượn sách
@app.route('/borrow/<int:book_id>', methods=['GET', 'POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if not book.available:
        flash("Sách này đã được mượn!", 'warning')
        return redirect(url_for('index'))  # Nếu sách đã mượn, không thể mượn lại
    
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = User.query.get(user_id)
        
        if user:
            new_borrow = Borrow(book_id=book.id, user_id=user.id)
            book.available = False  # Đánh dấu sách là đã mượn
            db.session.add(new_borrow)
            db.session.commit()
            flash("Mượn sách thành công!", 'success')
            return redirect(url_for('index'))
    
    users = User.query.all()  # Lấy danh sách người dùng
    return render_template('borrow_book.html', book=book, users=users)

@app.route('/book_detail/<int:book_id>', methods=['GET', 'POST'])
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    borrow = Borrow.query.filter_by(book_id=book.id, return_date=None).first()  # Tìm mượn chưa trả

    if request.method == 'POST' and borrow:
        # Trả sách
        borrow.return_date = datetime.utcnow()  # Đánh dấu ngày trả sách
        book.available = True  # Đánh dấu sách có sẵn lại
        db.session.commit()
        flash("Trả sách thành công!", 'success')
        return redirect(url_for('index'))

    return render_template('book_detail.html', book=book, borrow=borrow)


@app.route('/return/<int:borrow_id>', methods=['GET', 'POST'])
@login_required
def return_book(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    if borrow.return_date:
        flash("Sách này đã được trả lại trước đó.", 'warning')
        return redirect(url_for('index'))

    book = Book.query.get(borrow.book_id)
    book.available = True  # Đánh dấu sách là có sẵn để mượn lại

    if request.method == 'POST':
        borrow.return_date = datetime.utcnow()
        db.session.commit()
        flash('Trả sách thành công!', 'success')
        return redirect(url_for('index'))

    return render_template('return_book.html', borrow=borrow)

if __name__ == '__main__':
    app.run(debug=True)
