from flask import Flask, request, render_template, flash, redirect, session
from mysqlconnection import MySQLConnector
app = Flask(__name__)
import re
import bcrypt

mysql = MySQLConnector('TheWall')
app.secret_key = 'Top_Secret'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
password_regex = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{4,8}$')



@app.route('/')
def index():

	if 'user_id'in session:
		return render_template('"wall.html')
	else:
		return render_template("index.html")
	

@app.route('/register', methods=['POST'])
def register():

	bool = True
	firstName = request.form['first_name']
	lastName = request.form['last_name']
	email = request.form['email']
	password = request.form['password']
	password2 = request.form['password2']
	if len(firstName) == 0:
		flash("Sorry not a name")
		bool = False
	if len(lastName) == 0:
		flash("No last name")
		bool = False
	if len(email) == 0:
		flash("No email")
		bool = False
	if len(password) == 0:
		flash("No password")
		bool = False
	if not EMAIL_REGEX.match(email):
		flash("Bad Email")
		bool = False
	if password != password2:
		flash("Passwords Dont match")
		bool = False
	if bool:
		password_hash = bcrypt.hashpw(str(password),bcrypt.gensalt())
		query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES('{}','{}','{}','{}', NOW(), NOW())".format(firstName,lastName,email,password_hash)
		mysql.run_mysql_query(query)
		flash("You just created a NEW TheWall account!")
		
		user = mysql.fetch("SELECT * FROM users WHERE email = '{}' LIMIT 1").format(email)
		session['user_id'] = user[0]['id']
		session['firstName'] = user[0]['first_name']
		print users
		print session
	return redirect('/')
	
	

@app.route('/login', methods=['POST'])
def login():
	email = request.form['email_l']
	pw = request.form['password_l']
	bool = True
	if len(email) == 0 or len(pw) ==0:
		flash('Fil shit Out ')
		bool = False
	if bool:
		user = mysql.fetch("SELECT * FROM users WHERE email = '{}' limit 1".format(pw))
		if(len(user) > 0):
			if user[0]: #there was no email, so user is a list []
				if bcrypt.check_password_hash(user[0]['password'], pw):
					session['user_id'] = user[0]['id']
					session['first_name'] = user[0]['first_name']
					print session
		else:
			flash("Nope")
	# print EMAIL_REGEX.match(user)
	# print password_regex.match(pw)
	# # 	print "ok"
	# # else:
	# # 	print "nahh"
	return redirect('/wall')

@app.route('/wall')
def wall():
	message = mysql.fetch("SELECT * FROM messages")
	return render_template("wall.html", message=message)

@app.route('/post', methods=['POST'])
def post():
	post = request.form['content']
	# message = mysql.fetch("SELECT * FROM messages")
	query = "INSERT INTO messages (message, created_at, updated_at) VALUES ('{}', NOW(), NOW())".format(post)
	mysql.run_mysql_query(query)
	return redirect('/wall')
app.run(debug=True)