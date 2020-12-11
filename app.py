from flask import Flask, render_template, request, redirect, escape, abort
from datetime import datetime
from methods import *
import mysql.connector

app = Flask(__name__)

"""
Check request method and not GET page when not signed in
"""
#TEMPLATE ROUTES
#LOGIN PAGE
@app.route('/login-page')
def login():
    return render_template('login.html')
#ABOUT
@app.route('/about')
def bio():
    return render_template('about.html')
#SIGN UP PAGE
@app.route('/signup-page')
def sign():
    return render_template('signup.html')
#ADMIN PAGE
@app.route('/admin')
def admin():
    return render_template('admin.html')
    
@app.route('/login', methods = ['POST','GET'])
def log():
    username = request.form['username']
    password = request.form['password']
    return log_in(username, password)

@app.route('/signup', methods=['POST'])
def signup():
    fname  = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    password = request.form['password']
    return sign_up(fname,lname,email,password,time_stamp)
#VIEW BLOG
@app.route('/blog')
def blog():
    return render_template('blog.html')
#CREATE NEW POST
@app.route('/create')
def create():
    return render_template('posts.html')

@app.route('/')
@app.route('/home')
def landing_page():
    return render_template('home.html')

@app.route('/clear',methods = ['POST','GET'])
def clear():
    return render_template('update.html')
@app.route('/play')
def play():
    return render_template('play.html')

#finish up on this update log
#ACTIONS
@app.route('/update')
def update_data():
    update = request.form['update']
    return update_log(update)

@app.route('/view-data', methods=['POST'])
def view_data():
    username = request.form['username']
    password = request.form['password']
    data = view_log(username,password)
    return render_template('admin.html', data = data) 

@app.route('/post', methods=['POST','GET'])
def post():
    author = request.form['author']
    title = request.form['title']
    content = request.form['content']
    save = create_post(author,title,content)
    return render_template('posts.html', save = save)

@app.route('/search', methods=['POST'])
def search():
    letter = request.form['letter']
    phrase  = request.form['phrase']
    result = str(search4letters(letter, phrase))
    return render_template('home.html', result = result)

@app.route('/lucky_no', methods=['POST','GET'])
def lucky():
    guess = int(request.form.get('guess',False)) 
    response = lucky_number(guess)
    return render_template('home.html',response = response)

@app.route('/keygen')
def keygen():
    key = password_gen()
    return render_template('home.html', key = key)
    
@app.route('/bmi', methods=['POST'] )
def bmi():
    name = request.form['name']
    weight = int(request.form['weight'])
    height = float(request.form['height'])   
    bmi = bmi_calc(name,weight,height)
    return render_template('home.html', bmi = bmi)

if __name__ == '__main__':
    app.run(port = 3000,debug=True)