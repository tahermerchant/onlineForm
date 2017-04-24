from flask import Flask, render_template, request, session, redirect, url_for, flash
from models import db, User
from forms import SignupForm, LoginForm
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://taher:cspl123@localhost/onlineform'
db.init_app(app)

app.secret_key = "developer-key"

@app.route("/")
@app.route("/index")
def index():
	session.pop('email',None)
	return render_template("index.html")

@app.route("/createadmin", methods=['GET','POST'])
def createadmin():
	if 'email' not in session:
		return redirect(url_for('login'))
	form = SignupForm()
	if request.method == 'POST':
		if form.validate() == False:
			return render_template('createadmin.html', form = form)
		else:
			newUser = User(form.first_name.data,form.last_name.data, form.email.data, form.password.data,form.phone.data,"admin","No")
			db.session.add(newUser)
			db.session.commit()
			flash("A new admin created!")
			return redirect(url_for('superadmin'))
	else:
		return render_template('createadmin.html', form = form)
	
@app.route("/superadmin")
def superadmin():
	if 'email' not in session:
		return redirect(url_for('login'))
	users = User.query.filter_by(role ="admin").all()
	email = session['email']
	authorized = User.query.filter_by(email=email).first()
	if authorized.role == 'super':
		return render_template("superadmin.html",users=users)
	else:
		return redirect(url_for('logout'))

@app.route("/admin")
def admin():
	if 'email' not in session:
		return redirect(url_for('login'))
	users = User.query.filter_by(role ="normal").all()
	email = session['email']
	authorized = User.query.filter_by(email=email).first()
	if authorized.role == 'admin':
		return render_template("admin.html",users=users)
	else:
		return redirect(url_for('logout'))

@app.route("/signup", methods=['GET','POST'])
def signup():
	if 'email' in session:
		return redirect(url_for('home'))

	form = SignupForm()
	if request.method == 'POST':
		if form.validate() == False:
			return render_template('signup.html', form = form)
		else:
			newUser = User(form.first_name.data,form.last_name.data, form.email.data, form.password.data,form.phone.data,"normal","No")
			db.session.add(newUser)
			db.session.commit()

			session['email'] =  newUser.email
			return redirect(url_for('home'))
	else:
		return render_template('signup.html', form = form)

@app.route("/login",methods=['GET','POST'])
def login():
	if 'email' in session:
		return redirect(url_for('home'))

	form = LoginForm()
	if request.method == 'POST':
		if form.validate() == False:
			return render_template('login.html',form=form)
		else:
			email= form.email.data
			password = form.password.data

			user = User.query.filter_by(email=email).first()
			if user is not None and user.check_password(password):
				session['email'] = form.email.data
				if user.role == 'normal':
					return redirect(url_for('home'))
				if user.role == 'super':
					return redirect(url_for('superadmin'))
				if user.role == 'admin':
					return redirect(url_for('admin'))
			else:
				flash("Incorrect Username or Password")
				return redirect(url_for('login'))
	else:
		return render_template('login.html',form=form)

@app.route('/home')
def home():
	if 'email' not in session:
		return redirect(url_for('login'))
	email = session['email']
	authorized = User.query.filter_by(email=email).first()
	if authorized.role == 'normal':
		return render_template('home.html')
	else:
		return redirect(url_for('logout'))

@app.route('/logout')
def logout():
	session.pop('email',None)
	return render_template('index.html')

if __name__ == "__main__":
	app.run(debug=True)