from flask import Flask, render_template, request, redirect, escape, abort,url_for
from  methods import *

app = Flask(__name__)
"""
Check request method and not GET page when not signed in
"""
#TEMPLATE ROUTES
@app.route('/')
def root():
    return render_template('about.html')
#LOGIN PAGE
@app.route('/login-page')
def login():
    return render_template('login.html')
#ABOUT
@app.route('/about')
def bio():
    post = ['steve',"Sam", "Dweet Fi Di Love"]
    return render_template('edit.html' ,post= post)
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
    post = get_post()
    return render_template('blog.html', post = post)
#CREATE NEW POST
@app.route('/create')
def create():
    return render_template('posts.html')

@app.route('/home')
def landing_page():
    return render_template('home.html')

@app.route('/clear',methods = ['GET'])
def clear():
    return render_template('update.html')
@app.route('/play')
def play():
    return render_template('play.html')
#ACTIONS
#EDIT POST
@app.route('/blog/edit/<int:id>', methods  = ['GET', 'POST'])
def edit(id):
    with DbManager(**DBCONGIF) as cursor:
        if request.method == 'POST':       
            author = request.form['author']
            title = request.form['title']
            content = request.form['content']
            SQL = '''UPDATE  post set author = %s, title = %s, content = %s where post_id = %s'''
            cursor.execute(SQL,(author,title,content,id,))        
            return  redirect('/blog')
        else:
            SQL = '''SELECT * FROM post WHERE post_id = %s'''
            cursor.execute(SQL,(id,))
            post = cursor.fetchall()
            content = []
            for i in post:
                content.append(i)
            return render_template('editpost.html', post = content)
#DELETE POST
@app.route('/blog/delete/<int:id>')
def delete(id):
        return delete_post(id)

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
    return redirect(url_for('blog'))

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