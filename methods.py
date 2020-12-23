from datetime import datetime
import random
import hashlib
from flask import Flask,request,render_template,abort,redirect,url_for
import mysql.connector

DBCONGIF = {
    'host': 'localhost',
    'user': 'admin',
    'password' : 'admin',
    'database' : 'myappDB'
}
class DbManager():
    def __init__(self,**DBCONGIF)->None:
        self.config = DBCONGIF
    
    def __enter__(self)->'cursor':
        self.conn = mysql.connector.connect(**DBCONGIF)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self,arg1,arg2,arg3)->None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

time_stamp = datetime.now().strftime('%c')

#activity log func
#sign_up function to log details in txt file    
def sign_up(fname:str,lname:str,email:str,username:str,password:str,time= str):
    with DbManager(**DBCONGIF) as cursor:
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('SIGN UP',(username)))
        SQL = '''INSERT INTO users (first_name,last_name, email,username,password) 
        VALUES (%s,%s,%s,%s,%s)'''
        return cursor.execute(SQL,(fname,lname,email,username,password))
#log in func takes in username and password
def log_in(username:str,password:str):
     with DbManager(**DBCONGIF) as cursor:
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('LOG IN',username))
        USER_SQL = '''SELECT username, password FROM users  '''
        cursor.execute(USER_SQL)
        users = dict(cursor.fetchall())
        for user in users:
            if username in users:
                print('User ndio huyu',username)
                print('Password ni ii apa',users[username])
                if  users[username]== hashlib.sha256(password.encode()).hexdigest():
                    blog = get_post()
                    count =  len(blog)
                    recent = []
                    for k,v  in enumerate(blog):
                        if int(k) <5:
                            recent.append(v)
                    return recent
                else:
                    response = 'Wrong password!!'
                    return response
                    break
            else:
                response = 'Username not found!!'
                return response
                break
#log_in('admin',hashlib.sha256('root'.encode()).hexdigest())
#UPDATE VIEW LOG FUNTION
def view_log(username,password):
    with DbManager(**DBCONGIF) as cursor:
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('VIEW LOG',username))
        
        if username in users:
            if password == users[username]:
                SQL = '''SELECT * FROM log'''
                cursor.execute(SQL)
                log_data = cursor.fetchall()
                return log_data
            else:
                response= "WRONG PASSWORD!!"
                return response
        else:
            abort(401)
#FUNCTION TO UPDATE LOG
#ADD CODE TO CHECK IF ADMIN OR SUPERUSER
def update_log(update):
    with open('log.log','w') as vlog:
        updates = input('New stuff: ')
        print(f'These are the new updates by admin\n{updates} \nOn: {time_stamp}|', file=vlog,end='\n')
    return 'successful log update'

#CREATE POST
def create_post(author,title,content)-> None:
    with DbManager(**DBCONGIF) as cursor:
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('CREATE POST',author))
        SQL = '''INSERT INTO post(author, title, content) VALUES (%s,%s,%s)'''
        return cursor.execute(SQL,(author,title,content))
    
#GET POST FROM DB
def get_post() ->'Posts':
    #CHECK USER ID AND RETURN PUBLIC AND ALL USER ID'S POST
    with DbManager(**DBCONGIF) as cursor:
        #LOG ACTION ------FIX
        #LOG_SQL ='''INSERT INTO  log ("GET POST" ,username) VALUES(%s,%s)'''
        SQL = '''SELECT * FROM post ORDER BY date DESC '''
        cursor.execute(SQL)
        post = cursor.fetchall()
        return post

def db_search(keyword):
    with DbManager(**DBCONGIF) as cursor:  
        LOG_SQL ='''INSERT INTO  log (Action_done,username) VALUES(%s,%s)'''
        cursor.execute(LOG_SQL,('SEARCH',keyword))
        #SQL_POST = """SELECT content FROM  post WHERE content  LIKE '%s%%' """
        #cursor.execute(SQL_POST,keyword)
        #posts = cursor.fetchall()
        SQL_AUTHORS = """SELECT author FROM post WHERE content LIKE  '' """
        cursor.execute(SQL_AUTHORS)
        authors = cursor.fetchall()
        return authors
        #pprint.pprint(posts)
        

def  edit_post(id):
    with DbManager(**DBCONGIF) as cursor:
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
    with DbManager(**DBCONGIF) as cursor:
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



'''post = get_post()
date = post[0][4] 

print(datetime.strftime(date,'%c'))
USER FRIENDLY TIME FORMAT WITH TIME SAVED IN DB'''
