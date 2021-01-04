from datetime import datetime
import random
import hashlib
from flask import Flask,request,render_template,abort,redirect,url_for
import mysql.connector

DBCONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password' : 'admin',
    'database' : 'myappDB'
}
class DbManager():
    def __init__(self,**DBCONFIG)->None:
        self.config = DBCONFIG
    
    def __enter__(self)->'cursor':
        self.conn = mysql.connector.connect(**DBCONFIG)
        self.cursor = self.conn.cursor(buffered=True)
        return self.cursor

    def __exit__(self,arg1,arg2,arg3)->None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

time_stamp = datetime.now().strftime('%c')

#activity log func
#sign_up function to log details in txt file    
def sign_up(fname:str,lname:str,email:str,username:str,password:str,time= str):
    with DbManager(**DBCONFIG) as cursor:
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('SIGN UP',(username)))
        SQL = '''INSERT INTO users (first_name,last_name, email,username,password) 
        VALUES (%s,%s,%s,%s,%s)'''
        return cursor.execute(SQL,(fname,lname,email,username,password))
#log in func takes in username and password
def log_in(username:str,password:str):
     with DbManager(**DBCONFIG) as cursor:
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('LOG IN',username))
        USER_SQL = '''SELECT username, password FROM users  '''
        cursor.execute(USER_SQL)
        users = dict(cursor.fetchall())
        for user in users:
            if username in users:
                if  users[username]== hashlib.sha256(password.encode()).hexdigest():
                    SQL = '''SELECT * FROM post WHERE author  = %s'''
                    posts = cursor.execute(SQL, (username,))
                    return posts
                #TO GET  POST WRITTEN BY USERNAME
                else:
                    response = 'Wrong password!!'
                    return response
                    break
        else:
            response = 'Username not found!!'
            return response
#FIX THIS SECTION
def user_profile(username):
    with DbManager(**DBCONFIG) as cursor:
        AUTHORS_SQL = '''SELECT DISTINCT  first_name, last_name, username FROM users'''
        cursor.execute(AUTHORS_SQL)
        authors = cursor.fetchall()
        
        #SQL_1 = '''SELECT * FROM post WHERE post_status = %s'''
        #user_details = cursor.execute()
    count = len(get_all_posts(username))        #GET NUMBER OF ALL POSTS IN DB
    allposts = private_post(username)           #GET ALL 
    #count =  len(allposts)
    recent = []
    for k,v  in enumerate(allposts):
        if int(k) <10:
            recent.append(v)
    return [count,recent, allposts, authors]

def profile_data(username):
    with DbManager(**DBCONFIG) as cursor:
        PROFILE_SQL = '''SELECT * FROM users WHERE username = %s'''
        cursor.execute(PROFILE_SQL, (username,))
        return cursor.fetchall()

def edit_profile(username,first_name,last_name,email,uname,about):
    with DbManager(**DBCONFIG) as cursor:
        PROFILE_SQL = '''UPDATE users SET first_name = %s, last_name = %s,
        email = %s, username = %s, about = %s  WHERE username = %s '''
        return cursor.execute(PROFILE_SQL,(first_name,last_name,email,uname, about,username))
#UPDATE VIEW LOG FUNTION
def view_log(username,password):
    with DbManager(**DBCONFIG) as cursor:
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('VIEW LOG',username))
        USER_SQL = '''SELECT username, password FROM users  '''
        cursor.execute(USER_SQL)
        users = dict(cursor.fetchall())
        if username in users:
            if password == users[username]:
                SQL = '''SELECT * FROM log ORDER BY id DESC'''
                cursor.execute(SQL)
                log_data = cursor.fetchall()
                return log_data
            else:
                response= "WRONG PASSWORD!!"
                return response
        else:
            abort(401)

#CREATE POST
def create_post(author,title,content,privacy)-> None:
    with DbManager(**DBCONFIG) as cursor:
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('CREATE POST',author))
        SQL = '''INSERT INTO post(author, title, content,privacy) VALUES (%s,%s,%s,%s)'''
        return cursor.execute(SQL,(author,title,content,privacy))
#get  posts for personal profile
#private and public posts
def private_post(username):   
    with DbManager(**DBCONFIG) as cursor:
        SQL = """ SELECT * FROM post  WHERE author = %s  ORDER BY date DESC"""
        cursor.execute(SQL, (username,))
        return cursor.fetchall()
    
#GET POST FROM DB
def get_all_posts(username:str) ->'Posts':
    #CHECK USER ID AND RETURN PUBLIC AND ALL USER ID'S POST
    with DbManager(**DBCONFIG) as cursor:
        LOG_SQL ="""INSERT INTO  log (Action_done ,username) VALUES(%s,%s)"""
        cursor.execute(LOG_SQL,('Get Posts',username))
        AUTHORS_SQL = '''SELECT DISTINCT  first_name, last_name, username FROM users'''
        cursor.execute(AUTHORS_SQL)
        users = cursor.fetchall()
        ALL_PERSONAL_POSTS = """ SELECT * FROM post  WHERE author = %s  ORDER BY date DESC"""
        cursor.execute(ALL_PERSONAL_POSTS,(username,))
        all_personal_posts = cursor.fetchall() 
        ALL_PUBLIC_POSTS = """SELECT * FROM post WHERE privacy = 'NO' ORDER BY date DESC """
        cursor.execute(ALL_PUBLIC_POSTS) 
        all_public_posts = cursor.fetchall()
        ALL_USER_PUBLIC = """SELECT * FROM post WHERE privacy = 'NO'  AND author = %s ORDER BY date DESC """
        cursor.execute(ALL_USER_PUBLIC,(username,)) 
        all_user_posts = cursor.fetchall()
        return [all_personal_posts,all_public_posts,all_user_posts,users]

def post_privacy(status):     #UNUSED FUNCTION
    with DbManager(**DBCONFIG) as cursor:
        if status == 'YES':
            SQL = '''ALTER post SET post_status = 1'''
            return cursor.execute()
        elif  status  == 'NO':
            SQL = 'ALTER post SET post_status = 0'
            return cursor.execute

#SEARCH FUNCTION
# FIX BUG 
def db_search(keyword):
    with DbManager(**DBCONFIG) as cursor:  
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('SEARCH',keyword))
        #SQL_POST = """SELECT content FROM  post WHERE content  LIKE '%s%%' """
        #cursor.execute(SQL_POST,keyword)
        #posts = cursor.fetchall()
        SQL_AUTHORS = """SELECT author FROM post WHERE content LIKE  '%s%%' """
        cursor.execute(SQL_AUTHORS,keyword)
        authors = cursor.fetchall()
        return authors
        

def  edit_post(id):
    with DbManager(**DBCONFIG) as cursor:
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('EDIT POST',id))
        SQL = '''SELECT * FROM post WHERE post_id  = %s'''
        cursor.execute(SQL,(id,))
        post = cursor.fetchall()
        content = []
        for i in post:
            content.append(i)
        return content

def delete_post(id):
    with DbManager(**DBCONFIG) as cursor:
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('DELETE POST',id))
        delete = '''DELETE FROM post WHERE post_id  = %s'''
        cursor.execute(delete,(id,))
        return redirect(url_for('blog'))        
#generate number and asks user to guess
def lucky_number(guess):
    my_number = random.randint(1,3)
    print('DEBUG MODE:', my_number)
    if guess > my_number:
        response = 'GUESS LOWER'
        return response
    elif guess < my_number:
        response = 'GUESS HIGHER'
        return response
    else:
        response= f'You got it right my guess was {my_number}'
        return response
#password generator
def password_gen():
    number = ['12345678']
    letters = ['abcdefghijklmnopqrstuvwxyz']
    upper = []
    for i in letters:
        upper.append(i.upper())

    symbols = ['@!#$%^&*()}{][":><?']
    gen = str(number +letters + upper + symbols)
    length = 16
    password = random.sample(gen,length)
    return ''.join(password)
##search phrase function
def search4letters(letter,phrase):
    result = list(set(letter).intersection(set(phrase)))

    return str(result)[1:-1]
#calc mi function
def bmi_calc(name: str,weight:int, height:float):
    bmi = int(weight) // float((height)** 2)
    if bmi > 24:
        return f'{name.capitalize()}:You kinda fat hommie --- {bmi}'
    elif bmi < 12:
        return f'{name.capitalize()}: Eey you underweight bro --- {bmi}'
    else:
        return f'{name.capitalize()}: Bro you winning at this bmi shit --- {bmi}'



'''post = get_all_posts()
date = post[0][4] 

print(datetime.strftime(date,'%c'))
USER FRIENDLY TIME FORMAT WITH TIME SAVED IN DB'''
