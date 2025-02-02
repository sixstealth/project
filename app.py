from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    price = db.Column(db.Float, nullable = False)
    isActive = db.Column(db.Boolean, default = True)
    text = db.Column(db.Text, nullable = False)

@app.route('/')
def index():
    return render_template("index.html")

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