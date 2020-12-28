from flask import Flask, render_template, request, redirect, escape, abort,url_for,session
from methods import *
import hashlib

app = Flask(__name__)
#FOR SESSIONS
app.secret_key = 'MyVerySecretKey'

#TEMPLATE ROUTES
#LOGIN PAGE
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

#USER AUTH AND LOG IN
@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        response = log_in(username= username, password = password )
        print(response)
        if response == 'Wrong password!!':
            return  render_template('login.html',response = response)
        elif response == 'Username not found!!':
            return render_template('login.html', response= response)
        else:
            session['username'] = username
            return redirect(url_for('profile'))

@app.route('/profile') 
def profile():
    username = session['username']
    data = user_profile(username)
    return render_template('profile.html', username = username, recent= data[1], count = data[0],data = data)

#ADMIN PAGE
@app.route('/admin', methods = ['POST','GET'])
def admin():
    title = 'Admin'
    #check session name
    status = f"You are logged in as {session['user']}"
    if session['user'] == 'Admin':
        if request.method == 'GET':
            return render_template('admin.html',status = status, title = title) 
        else:
            #give password to viewlog
            code = request.form['password']
            password = hashlib.sha256(f'{str(code)}'.encode()).hexdigest()
            log_data = view_log(session['user'],password)
            if log_data == 'WRONG PASSWORD!!':
                return render_template('admin.html', response = log_data, status = status,title = title)
            else:
                return render_template('admin.html', log_data = log_data,status = status, title = title)
    else:
        return abort(401)

@app.route('/adminpanel')
def admin_panel():
    title = 'Admin Panel'
    with DbManager(**DBCONFIG) as cursor:
        USERS_SQL = '''SELECT * FROM users'''
        cursor.execute(USERS_SQL)
        users = cursor.fetchall()
        COMMENT_SQL = '''SELECT * FROM comments'''
        cursor.execute(COMMENT_SQL)
        comments = cursor.fetchall()
        LOG_SQL = '''SELECT * FROM log'''
        cursor.execute(LOG_SQL)
        logs = cursor.fetchall()
        POST_SQL = '''SELECT * FROM post'''
        cursor.execute(POST_SQL)
        posts = cursor.fetchall()
        UPLOAD_SQL = '''SELECT * FROM uploads '''
        cursor.execute(UPLOAD_SQL)
        uploads = cursor.fetchall()
        return render_template('adminpanel.html',users= users,comments = comments, logs = logs, posts = posts, uploads = uploads, title = title)


@app.route('/signup', methods=['POST','GET'])
def signup():
    title = 'Signup'
    if request.method == 'GET':
        return render_template('signup.html', title = title)   
    else:
        fname  = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        code = hashlib.sha256(f'{str(password)}'.encode()).hexdigest()
        sign_up(fname,lname,email,username,code)
        return redirect(url_for('profile'))
#VIEW BLOG
@app.route('/blog')
def blog():
    title = 'Blog'
    post = get_all_posts()
    count = len(post)
    username = session['username']
    return render_template('blog.html', post = post, count= count, username = username, title = title)
#CREATE NEW POST
@app.route('/blog/create',methods= ['GET','POST'])
def create():
    title = 'New Post'
    if request.method == 'GET':
        return render_template('newposts.html',title = title)
    else:
        author = request.form['author']
        title = request.form['title']
        content = request.form['content']
        create_post(author,title,content)
        return redirect(url_for('blog'))


@app.route('/clear',methods = ['GET'])
def clear():
    return render_template('update.html')
@app.route('/play')
def play():
    title = 'Play'
    return render_template('play.html', title = title)
#ACTIONS
#SEARCH APP
@app.route('/search/<keyword>', methods=['POST'])
def search(keyword):
    title = f'Results for {keyword}'
    keyword = request.form['keyword']
    result = db_search(keyword)
    authors = result[0]
    posts = result[1]
    return render_template('result.html' ,authors = authors, posts = posts, keyword= keyword,title = title)

#GET POST
@app.route('/blog/<int:id>')
def post(id):
    title  = ' '
    username = session['username']
    count= len(get_all_posts())
    with DbManager(**DBCONFIG) as cursor:
        SQL = '''SELECT * FROM post WHERE post_id = %s'''
        cursor.execute(SQL,(id,))
        post = cursor.fetchall()
        content = []
        for i in post:
            content.append(i)
    return render_template('post.html' ,content= content, count=count, username = username)
    #EDIT POST
@app.route('/blog/edit/<int:id>', methods  = ['GET', 'POST'])
def edit(id):
    username = session['username']
    count = len(get_all_posts())
    with DbManager(**DBCONFIG) as cursor:
        if request.method == 'POST':       
            author = request.form['author']
            title = request.form['title']
            content = request.form['content']
            SQL = '''UPDATE  post SET author = %s, title = %s, content = %s where post_id = %s'''
            cursor.execute(SQL,(author,title,content,id,)) 
            SQL_2 = '''SELECT * FROM post WHERE post_id = %s '''
            cursor.execute(SQL_2,(id,))
            result = cursor.fetchall()       
            return render_template('post.html', content= result , count=count, username = username)
        else:
            SQL = '''SELECT * FROM post WHERE post_id = %s'''
            cursor.execute(SQL,(id,))
            post = cursor.fetchall()
            content = []
            for i in post:
                content.append(i)
            return render_template('editpost.html', post = content,username = username)
#DELETE POST
@app.route('/blog/delete/<int:id>')
def delete(id):
        return delete_post(id)

@app.route('/play/search', methods=['POST'])
def search_letter():
    letter = request.form['letter']
    phrase  = request.form['phrase']
    result = str(search4letters(letter, phrase))
    return render_template('play.html', result = result)

@app.route('/play/lucky_no', methods=['POST','GET'])
def lucky():
    guess = int(request.form.get('guess',False)) 
    response = lucky_number(guess)
    return render_template('play.html',response = response)

@app.route('/play/keygen')
def keygen():
    key = password_gen()
    return render_template('play.html', key = key)
    
@app.route('/play/bmi', methods=['POST'] )
def bmi():
    name = request.form['name']
    weight = int(request.form['weight'])
    height = float(request.form['height'])   
    bmi = bmi_calc(name,weight,height)
    return render_template('play.html', bmi = bmi)

if __name__ == '__main__':
    app.run(port = 3000,debug=True)
