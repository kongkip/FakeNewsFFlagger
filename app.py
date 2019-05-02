from flask import Flask, render_template,url_for, request, redirect
import pickle
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from tokens import getTokens
import pandas as pd
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user



mail = Mail()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SECRET_KEY'] = "asecretkey"

app.secret_key = "asecretkey"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'evanskiplagat3@gmail.com'
app.config["MAIL_PASSWORD"] = '33387388'

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
admin = Admin(app)

mail.init_app(app)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=True)
	email = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Implementing user login form
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


# Implementing user registration form
class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

# Route for user to predict url probability before login
@app.route("/",methods=["GET","POST"])
def detect():

	model = pickle.load(open("pickles/naive_bayes.pkl","rb"))
	vectorizer = pickle.load(open("pickles/vectorizer.pkl","rb"))

	if request.method == "POST":
		url = request.form["url"]
		urls = [url]
		data = pd.DataFrame(data=[urls],columns=["url"])
		#print(data.url)
		vect = vectorizer.transform(data.url)
		#print(vect)
		prediction_proba = model.predict_proba(vect)[0]
		prediction = np.array(pd.DataFrame(data=prediction_proba, columns = ['prediction']).loc[1])
		return render_template("result.html", prediction=prediction)
	return render_template("index.html")

# Route for user to predict url probability after login
@app.route("/dashboard",methods=["GET","POST"])
def detect_2():
    
    # Loading model from disk
	model = pickle.load(open("pickles/naive_bayes.pkl","rb"))
    # loading vectorizer
	vectorizer = pickle.load(open("pickles/vectorizer.pkl","rb"))


	if request.method == "POST":
        # gettinng data from form
		url = request.form["url"]
		urls = [url]
		data = pd.DataFrame(data=[urls],columns=["url"])
		#print(data.url)
		vect = vectorizer.transform(data.url)
		#print(vect)
		prediction_proba = model.predict_proba(vect)[0]
		prediction = np.array(pd.DataFrame(data=prediction_proba, columns = ['prediction']).loc[1])
		return render_template("result.html", prediction=prediction)
	return render_template("dashboard.html")

# route for contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
 
  if request.method == 'POST':
      msg = Message(request.form['subject'], sender=request.form['email'], recipients=['dankimz@gmail.com'])
      msg.body = """
      From: %s &lt;%s&gt;
      %s
      """ % (request.form['name'],request.form['email'], request.form['message'])
      mail.send(msg)
 
      return render_template("contact.html", form = request.form)
 
  elif request.method == 'GET':
    return render_template('contact.html', form=request.form)

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)

# route for login page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1 style="color:green">Your account has been created Successfully!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

# dashboard for user after login
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

# user logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')





class Urls(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(1000))
	category = db.Column(db.String(10))
		
admin.add_view(ModelView(Urls, db.session ))
admin.add_view(ModelView(User, db.session ))


if __name__ == "__main__":
	app.run(debug=True, port=5000)
