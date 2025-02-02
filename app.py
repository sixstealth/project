from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# login_manager = LoginManager()
# login_manager.init_app(app)
# # class User(db>model, UserMixin):
# #     id = db.Column(db.String(150), unique = True, nullable = False)
# #     password = db.Column(db.String(150), nullable = False)

# @login_manager.user.loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# login_manager = LoginManager()
# login_manager.init_app(app)
# class User(db>model, UserMixin):
#     id = db.Column(db.String(150), unique = True, nullable = False)
#     password = db.Column(db.String(150), nullable = False)

# @login_manager.user.loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    price = db.Column(db.Float, nullable = False)
    isActive = db.Column(db.Boolean, default = True)
    text = db.Column(db.Text, nullable = False)



@app.route('/')
def index():
    return render_template("index.html")

@app.route('/addform')
def addform():
    return render_template("addform.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

with app.app_context():
    db.create_all()



if __name__ == "__main__":
    app.run(debug=True) 