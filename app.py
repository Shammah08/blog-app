from flask import Flask, render_template, request, redirect, escape, abort,url_for,session
from models import *
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
        session.pop('username',None)
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        response = log_in(username= username, password = password )
        if response == 'Wrong password!!':
            return  render_template('login.html',response = response)
        elif response == 'Username not found!!':
            return render_template('login.html', response= response)
        else:
            #SUCCESSFUL LOGIN
            session['username'] = username
            
            return redirect(url_for('profile'))

@app.route('/logout')
def log_out():
    title = 'Logout'
    try:
        username = session['username']
        session.pop('username',None)
        return redirect('login')
    except KeyError:
        return render_template('error.html',title = title)
#VISIT OWN PROFILE- PERSONAL
@app.route('/profile') 
def profile():
    title = 'My Profile'
    try:
        username = session['username']
        profile = profile_data(username)
        data = user_profile(username)
        posts = get_all_posts(username)
        count = len(posts[1])
        mycount = len(posts[0])
       
        return render_template('profile.html', profile=profile,username = username, count = count,title = title,data = data,mycount = mycount)
    except KeyError:
        return render_template('error.html',title= title)
#VISIT ANY USERS PROFILE AS GUEST
@app.route('/profile/guest-<guest_username>')
def guest_profile(guest_username):
    try:
        username = session['username']
        #Check the user requesting the profile and the user profile being requested
        if username != guest_username:
            profile = profile_data(guest_username)
            data = get_all_posts(guest_username)
            count = len(data[1])
            mycount = len(data[2])
            print(mycount)
            title = f"{guest_username}'s profile"
            return render_template('profile.html', profile=profile,username = username, count = count,mycount=mycount,title = title,data = data,guest_username= guest_username)
        else:
            #WHEN YOU VISIT YOUR PROFILE
            return redirect(url_for('profile'))
    except KeyError:
        title = username
        return render_template('error.html',title= title)
#ADMIN PAGE
@app.route('/admin', methods = ['POST','GET'])
def admin():
    title = 'Administration'
    try:
        #check session name
        status = f"You are logged in as {session['username']}"
        if session['username'] == 'Admin':
            if request.method == 'GET':
                return render_template('admin.html',status = status, title = title) 
            else:
                #give password to viewlog
                code = request.form['password']
                password = hashlib.sha256(f'{str(code)}'.encode()).hexdigest()
                log_data = view_log(session['username'],password)
                if log_data == 'WRONG PASSWORD!!':
                    return render_template('admin.html', response = log_data, status = status,title = title)
                else:
                    return render_template('admin.html', log_data = log_data,status = status, title = title)
        else:
            #standard user error
            return abort(401)
    except KeyError:
        return render_template('error.html',title = title)
#MIGRATE THE SQL QUERIES TO THE Methods.py FILE
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
        session['username']=username
        return redirect(url_for('setting'))

@app.route('/settings',methods = ['POST', 'GET'])
def setting():
    username= session['username']
    if request.method == 'GET':
        data = profile_data(username)
        return render_template('settings.html', data = data,username = username)
    else:
        first_name = request.form['fname']
        last_name = request.form['lname']
        email= request.form['email']
        uname = request.form['username']
        about = request.form['about']
        edit_profile(username,first_name,last_name,email,uname,about)
        data = profile_data(username)
        status = 'Update Successful!!'
        return render_template('settings.html',data=data, status = status,username = username)
@app.route('/blog')
def blog():
    title = 'Blog'
    try:
        username = session['username']
        post = get_all_posts(username)
        count = len(post[1])        
        return render_template('blog.html', post = post, count= count, username = username, title = title)
    except KeyError:
        return render_template('error.html', title = title)
#CREATE NEW POST
@app.route('/blog/create',methods= ['GET','POST'])
def create():
    title = 'New Post'
    username = session['username']
    if request.method == 'GET':
        return render_template('newposts.html',title = title, username = username)
    else:
        author = request.form['author']
        title = request.form['title']
        content = request.form['content']
        privacy = request.form['privacy'].capitalize()
        create_post(author,title,content,privacy)
        if privacy == 'Yes':
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('blog'))

@app.route('/about')
def about():
    return render_template('about.html')

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
    username = session['username']
    data = get_all_posts(username)
    count = len(data[1])
    with DbManager(**DBCONFIG) as cursor:
        SQL = '''SELECT * FROM post WHERE post_id = %s'''
        cursor.execute(SQL,(id,))
        content = cursor.fetchall()
        #title = content[0][2]
   
        return render_template('post.html' ,content= content, count=count, username = username,)
#BLOG NAVIGATION
# FIX TO NAVIGATE THROUGH PUBLIC POSTS ONLY  
@app.route('/blog/next/<int:id>')
def next(id):
    username = session['username']
    try:
        posts = get_all_posts(username)[1]
        all_id = []
        for item in posts:
            all_id.append(item[0])
        for i in all_id:
            if id in all_id:
                position = all_id.index(id)
                if position  ==  0 :
                    return post(id)
                else:
                    nxt = position -1
                    return post(all_id[nxt])
    except:
        print( '<h1> An error occured')

@app.route('/blog/previous/<int:id>')
def previous(id):
    try:
        username = session['username']
        posts = get_all_posts(username)[1]
        all_id = []
        for item in posts:
            all_id.append(item[0])
        for i in all_id:
            if id in all_id:
                position = int(all_id.index(id))
                if position == len(all_id) - 1:
                    print(len(all_id))
                    return post(id)
                else:
                    print(len(all_id))
                    prev = position + 1
                    return post(all_id[prev])

    except :
        print( '<h1> An error occured')
    #EDIT POST
    #MIGRATE SQL TO MODELS.PY FILE
@app.route('/blog/edit/<int:id>', methods  = ['GET', 'POST'])
def edit(id):
    username = session['username']
    count = len(get_all_posts(username)[1])
    with DbManager(**DBCONFIG) as cursor:
        if request.method == 'POST':       
            author = request.form['author']
            title = request.form['title']
            content = request.form['content']
            privacy = request.form['privacy'].capitalize()
            EDIT_SQL = '''UPDATE  post SET author = %s, title = %s, content = %s, privacy = %s WHERE post_id = %s'''
            cursor.execute(EDIT_SQL,(author,title,content,privacy,id,)) 
            UPDATED_SQL = '''SELECT * FROM post WHERE post_id = %s '''
            cursor.execute(UPDATED_SQL,(id,))
            result = cursor.fetchall()       
            return render_template('post.html', content= result , count=count, username = username)
        else:
            SQL = '''SELECT * FROM post WHERE post_id = %s'''
            cursor.execute(SQL,(id,))
            post = cursor.fetchall()
            return render_template('editpost.html', post = post,username = username)
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