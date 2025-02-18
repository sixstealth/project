from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from flask_migrate import Migrate










app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['UPLOAD_FOLDER'] = 'static/uploads'


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def __repr__(self):
    return {self.title}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'
migrate = Migrate(app, db)

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending')  

    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    item = db.relationship('Item', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f"<Order {self.id}>"




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150), unique = True, nullable = False)
    password = db.Column(db.String(150), nullable = False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Wrong Credentials')

    return render_template('login.html')

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):

    product = Item.query.get_or_404(item_id)
    

    db.session.delete(product)
    db.session.commit()
    
  
    return redirect(url_for('addform'))


@app.route('/mark_as_completed/<int:order_id>', methods=['POST'])
@login_required
def mark_as_completed(order_id):
    order = Order.query.get_or_404(order_id)


    if current_user.is_authenticated:
        order.status = 'Completed'
        db.session.commit()
        flash('Order marked as completed.')
        return redirect(url_for('orders'))

    flash('You do not have permission to perform this action.')
    return redirect(url_for('orders'))

@app.route('/orders')
@login_required
def orders():
 
    orders = Order.query.filter_by(status='Pending').all() 
    return render_template('orders.html', orders=orders)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):

    quantity = int(request.form.get('quantity', 1))  
    item = Item.query.get_or_404(item_id)

    cart_item = Cart(user_id=current_user.id, item_id=item.id, quantity=quantity)

    db.session.add(cart_item)
    db.session.commit()

    flash(f"{item.title} added to your cart.")
    return redirect(url_for('menu'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, item_id=item_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Item removed from cart.")
    return redirect(url_for('cart'))


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    price = db.Column(db.Float)
    is_active = db.Column(db.Boolean)
    text = db.Column(db.String(500))
    image_filename = db.Column(db.String(100))  

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    item = db.relationship('Item', backref=db.backref('cart_items', lazy=True))

    def __repr__(self):
        return f"<Cart {self.id}>"








@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash("Your cart is empty!")
        return redirect(url_for('menu'))

    if request.method == 'POST':
        customer_name = request.form.get('customer_name') 
        customer_address = request.form.get('customer_address')  
        payment_method = request.form.get('payment_method')  


        if not customer_name or not customer_address or not payment_method:
            flash("Please fill in all the fields!")
            return render_template('checkout.html', cart_items=cart_items)


        for cart_item in cart_items:
            new_order = Order(
                user_id=current_user.id,
                item_id=cart_item.item_id,
                quantity=cart_item.quantity,
                status="Pending"
            )
            db.session.add(new_order)

        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        flash("Order placed successfully!")
        return redirect(url_for('cart'))  

    return render_template('checkout.html', cart_items=cart_items)




@app.route('/addform', methods=['POST', 'GET'])
@login_required
def addform():
    data = Item.query.all()
    if request.method == 'POST':
        print("POST request recieved")  
        
        title = request.form.get('title')
        price = request.form.get('price')
        image = request.files.get('image') 

        print(f"Recieved title: {title}, price: {price}")  

        if not title or not price:
            flash('Fill in all fields!')
            print("Form is not filled!")
            return render_template('addform.html')

        if image and allowed_file(image.filename):  
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
        else:
            image_path = None  

        try:
            item = Item(title=title, price=float(price), text="", image_filename=filename if image_path else None)
            db.session.add(item)
            db.session.commit()
            flash('Product successfully added!')
            print("Product added to base!")
            return redirect('addform')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}')
            print(f"Error during addition: {str(e)}")

    return render_template('addform.html', data=data)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()  

    if request.method == 'POST':
 
        customer_name = request.form.get('customer_name')  
        customer_address = request.form.get('customer_address')  
        payment_method = request.form.get('payment_method')  


        if not customer_name or not customer_address or not payment_method:
            flash("Please fill in all the fields!")
            return render_template('cart.html', cart_items=cart_items)

        
        for cart_item in cart_items:
            new_order = Order(
                user_id=current_user.id,
                item_id=cart_item.item_id,
                quantity=cart_item.quantity,
                status="Pending"
            )
            db.session.add(new_order)



        flash("Your order has been placed successfully!")
        return redirect(url_for('orders'))  

    return render_template('cart.html', cart_items=cart_items)




@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/menu')
def menu():
    items = Item.query.order_by(Item.price).all()  
    return render_template("menu.html", items=items)

#123

@app.route('/admin')
@login_required
def admin():
    print(current_user.is_authenticated)
    return render_template("admin.html")

@app.route('/home')
@app.route('/main')
@app.route('/index')
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug=True) 