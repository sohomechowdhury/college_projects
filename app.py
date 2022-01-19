#import sqlalchemy.engine
import MySQLdb
import MySQLdb.cursors
from flask import Flask, render_template, request, session, redirect, url_for
#from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_mail import Mail
import json
from flask_mysqldb import  MySQL
import re



local_server = True
with open('config.json','r') as c:
    params = json.load(c)["params"]
app = Flask(__name__)
app.secret_key = 'skey'

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_password']
)
mail=Mail(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'registration'
mysql=MySQL(app)
'''class Login(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(80), unique=True, nullable=False)'''
'''class Sign_up(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    signup_id = db.Column(db.String(80), primary_key=True)
    signup_pass = db.Column(db.String(80), unique=True, nullable=False)'''

@app.route('/')
def home():  # put application's code here
    return render_template('home.html',params=params)
@app.route('/backhome')
def backhome():  # put application's code here
    return render_template('home.html',params=params)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', params=params)

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM sign_up WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('dashboard.html', msg = msg,params=params)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg, params=params)
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
@app.route('/sign_up', methods=['GET' , 'POST'])
def sign_up():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form :
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM sign_up WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO sign_up VALUES (NULL, % s, % s)', (username, password))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            mail.send_message('New user', sender=username, recipients=[params['gmail_user']],
                              body=username + "\n" + password
                              )
    elif request.method == 'POST':
        msg = 'Please fill out the form !'


    return render_template('sign_up.html',params=params)
if __name__ == '__main__':
    app.run(debug=True)
