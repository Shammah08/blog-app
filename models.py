from datetime import datetime
import random
import hashlib
from flask import abort, redirect, url_for
import mysql.connector

DBCONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'admin',
    'database': 'myappDB'
}


class DbManager:
    def __init__(self, **DBCONFIG) -> None:
        self.config = DBCONFIG

    def __enter__(self) -> 'cursor':
        self.conn = mysql.connector.connect(**DBCONFIG)
        self.cursor = self.conn.cursor(buffered=True)
        return self.cursor

    def __exit__(self, arg1, arg2, arg3) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()


time_stamp = datetime.now().strftime('%c')

# activity log func
# sign_up function to log details in txt file
def sign_up(fname: str, lname: str, email: str, username: str, password: str):
    with DbManager(**DBCONFIG) as cursor:
        ACTIVITY_LOG = '''INSERT INTO activity(username, log_action, log_detail)
        VALUES (%s,%s,%s)'''
        cursor.execute(ACTIVITY_LOG,(username,'Sign Up',str(fname,lname)))
        SQL = '''INSERT INTO users (first_name,last_name, email,username,password) 
        VALUES (%s,%s,%s,%s,%s)'''
        return cursor.execute(SQL, (fname, lname, email, username, password))


# log in func takes in username and password


def log_in(username: str, password: str):
    with DbManager(**DBCONFIG) as cursor:
        USER_SQL = '''SELECT username, password FROM users  '''
        cursor.execute(USER_SQL)
        users = dict(cursor.fetchall())
        for user in users:
            if username in users:
                if users[username] == hashlib.sha256(password.encode()).hexdigest():
                    ACTIVITY_LOG = '''INSERT INTO activity(username, log_action, log_detail)
                    VALUES (%s,%s,%s)'''
                    cursor.execute(ACTIVITY_LOG,(username,'Log In','Success'))
                    SQL = '''SELECT * FROM post WHERE author  = %s'''
                    posts = cursor.execute(SQL, (username,))
                    return posts
                # TO GET  POST WRITTEN BY USERNAME
                else:
                    ACTIVITY_LOG = '''INSERT INTO activity(username, log_action, log_detail)
                    VALUES (%s,%s,%s)'''
                    cursor.execute(ACTIVITY_LOG,(username,'Log In','Wrong Password'))
                    response = 'Wrong password!!'
                    return response
        else:
            ACTIVITY_LOG = '''INSERT INTO activity(username, log_action, log_detail)
            VALUES (%s,%s,%s)'''
            cursor.execute(ACTIVITY_LOG,(username,'Log In','User Not Found'))
            response = 'Username not found!!'
            return response


# FIX THIS SECTION


def user_profile(userid):
    with DbManager(**DBCONFIG) as cursor:
        AUTHORS_SQL = '''SELECT DISTINCT  first_name, last_name, username, userid FROM users'''
        cursor.execute(AUTHORS_SQL)
        authors = cursor.fetchall()
    count = len(get_all_posts(userid)) # GET NUMBER OF ALL POSTS IN DB
    allposts = private_post(userid)[1]  # GET ALL
    recent = []
    for k, v in enumerate(allposts):
        if int(k) < 10:
            recent.append(v)
    return [count, recent, allposts, authors]


def profile_data(username):
    with DbManager(**DBCONFIG) as cursor:
        ACTIVITY_LOG = '''INSERT INTO activity(username, log_action)
        VALUES (%s,%s)'''
        cursor.execute(ACTIVITY_LOG,(username,'Profile Visit'))
        PROFILE_SQL = '''SELECT * FROM users WHERE username = %s'''
        cursor.execute(PROFILE_SQL, (username,))
        return cursor.fetchall()


# TO DO LIST
def add_to_do(userid: int, task: str, status: str) -> None:
    with DbManager(**DBCONFIG) as cursor:
        ACTIVITY_LOG = '''INSERT INTO activity(userid, log_action, log_detail)
        VALUES (%s,%s,%s)'''
        cursor.execute(ACTIVITY_LOG,(userid,'To-Do',status))
        SQL = '''INSERT INTO ToDoTest (TaskName, TaskStatus, userid) VALUES (%s, %s, %s) '''
        return cursor.execute(SQL, (task, status, userid))
        



def get_to_do(user_id: int) -> tuple:
    with DbManager(**DBCONFIG) as cursor:
        SQL = """SELECT * FROM ToDoTest WHERE userid= %s """
        cursor.execute(SQL, (user_id,))
        return cursor.fetchall()


def edit_to_do(id: int, username: str, task: str, status: str) -> tuple:
    with DbManager(**DBCONFIG) as cursor:
        ACTIVITY_LOG = '''INSERT INTO activity(username, log_action, log_detail)
        VALUES (%s,%s,%s)'''
        cursor.execute(ACTIVITY_LOG,(username,'Edit To-Do', id))
        SQL = '''UPDATE ToDoTest SET task = %s, status = %s  WHERE id = %s'''
        return cursor.execute(SQL, (task, status, username, id))


def edit_profile(userid, first_name, last_name, email, username, about):
    with DbManager(**DBCONFIG) as cursor:
        ACTIVITY_LOG = '''INSERT INTO activity(userid, username, log_action)
        VALUES (%s,%s,%s)'''
        cursor.execute(ACTIVITY_LOG,(userid,username,'Edit Profile'))
        EDIT_SQL = '''UPDATE users SET first_name = %s,  last_name = %s, email = %s, about = %s WHERE userid = %s'''
        return cursor.execute(EDIT_SQL, (first_name, last_name, email, about, userid))


# UPDATE VIEW LOG FUNcTION


def view_log(userid, password):
    with DbManager(**DBCONFIG) as cursor:
        USER_SQL = '''SELECT userid, password FROM users  '''
        cursor.execute(USER_SQL)
        users = dict(cursor.fetchall())
        if userid in users:
            if password == users[userid]:
                SQL = '''SELECT * FROM log ORDER BY id DESC'''
                cursor.execute(SQL)
                log_data = cursor.fetchall()
                ACTIVITY_LOG = '''INSERT INTO activity(userid, log_action, log_detail)
                VALUES (%s,%s,%s)'''
                cursor.execute(ACTIVITY_LOG,(userid,'View Log', 'Success'))
                return log_data
            else:
                ACTIVITY_LOG = '''INSERT INTO activity(userid, log_action, log_detail)
                VALUES (%s,%s,%s)'''
                cursor.execute(ACTIVITY_LOG,(userid,'View Log', 'Wrong passord'))
                response = "WRONG PASSWORD!!"
                return response
        else:
            ACTIVITY_LOG = '''INSERT INTO activity(userid, log_action, log_detail)
            VALUES (%s,%s,%s)'''
            cursor.execute(ACTIVITY_LOG,(userid,'View Log', 'Restricted Access'))
            abort(401)


# CREATE POST


def create_post(author, title, content, privacy, userid: int) -> None:
    with DbManager(**DBCONFIG) as cursor:
        ACTIVITY_LOG = '''INSERT INTO activity(userid,username, log_action, log_detail)
        VALUES (%s,%s,%s,%s)'''
        cursor.execute(ACTIVITY_LOG,(userid,author,'Create Post', title))
        SQL = '''INSERT INTO post(author, title, content,user_id,privacy) VALUES (%s,%s,%s,%s, %s)'''
        return cursor.execute(SQL, (author, title, content, userid, privacy))


# get  posts for personal profile
# private and public posts

def private_post(userid: int) -> list:
    with DbManager(**DBCONFIG) as cursor:
        ALL_POSTS = """ SELECT title, post_id FROM post  WHERE user_id = %s  ORDER BY date DESC"""
        cursor.execute(ALL_POSTS, (userid,))
        all_post = cursor.fetchall()
        ID_SQL = '''SELECT post_id FROM post WHERE user_id = %s'''
        cursor.execute(ID_SQL, (userid,))
        post_id = cursor.fetchall()
        return [post_id, all_post]


#  POST COMMENT


def comment(userid: int,username:str , post_id: int, comment: str)  ->None:
    with DbManager(**DBCONFIG) as cursor:
        ACTIVITY_LOG = '''INSERT INTO activity(userid,username, log_action, log_detail)
        VALUES (%s,%s,%s,%s)'''
        cursor.execute(ACTIVITY_LOG,(userid,username,'Comment',post_id))
        LOG_SQL = """INSERT INTO  log (Action_done ,username) VALUES(%s,%s)"""
        cursor.execute(LOG_SQL, ('Comment', userid))
        SQL = ''' INSERT INTO comments (userid, post_id, comment_body) VALUES (%s, %s, %s)'''
        return cursor.execute(SQL,(userid,post_id,comment))


# GET POST FROM DB


def get_all_posts(userid: int) -> 'Posts':
    # CHECK USER ID AND RETURN PUBLIC AND ALL USER ID'S POST
    with DbManager(**DBCONFIG) as cursor:
        ACTIVITY_LOG = '''INSERT INTO activity(userid, log_action)
        VALUES (%s,%s)'''
        cursor.execute(ACTIVITY_LOG,(userid,'Get Posts'))
        USERS = '''SELECT DISTINCT  first_name, last_name, username,userid FROM users'''
        cursor.execute(USERS)
        users = cursor.fetchall()
        ALL_PERSONAL_POSTS = """ SELECT * FROM post  WHERE user_id = %s  ORDER BY date DESC"""
        cursor.execute(ALL_PERSONAL_POSTS, (userid,))
        all_personal_posts = cursor.fetchall()
        ALL_PUBLIC_POSTS = """SELECT * FROM post WHERE privacy = 'NO' ORDER BY date DESC """
        cursor.execute(ALL_PUBLIC_POSTS)
        all_public_posts = cursor.fetchall()
        ALL_USER_PUBLIC = """SELECT * FROM post WHERE privacy = 'NO'  AND user_id = %s ORDER BY date DESC """
        cursor.execute(ALL_USER_PUBLIC, (userid,))
        all_user_posts = cursor.fetchall()
        return [all_personal_posts, all_public_posts, all_user_posts, users]


def post_privacy(status):  # UNUSED FUNCTION
    with DbManager(**DBCONFIG) as cursor:
        if status == 'YES':
            SQL = '''ALTER post SET post_status = 1'''
            return cursor.execute(SQL)
        elif status == 'NO':
            SQL = 'ALTER post SET post_status = 0'
            return cursor.execute(SQL)


# SEARCH FUNCTION
# FIX BUG


def db_search(userid: int, keyword: str) -> tuple:
    with DbManager(**DBCONFIG) as cursor:
        ACTIVITY_LOG = '''INSERT INTO activity(userid, log_action, log_detail)
        VALUES (%s,%s,%s)'''
        cursor.execute(ACTIVITY_LOG,(userid,'Search', keyword))
        SQL_POST = """SELECT content FROM  post WHERE content  LIKE '%s' """
        cursor.execute(SQL_POST,keyword)
        posts = cursor.fetchall()
        SQL_AUTHORS = """SELECT DISTINCT author FROM post WHERE content LIKE  '%s' """
        cursor.execute(SQL_AUTHORS, keyword)
        authors = cursor.fetchall()
        return (authors, posts)


def edit_post(userid: int,post_id: int, author: str, title: str, content: str, privacy: str) -> list: #UNUSED FUNCTION
    with DbManager(**DBCONFIG) as cursor:
        ACTIVITY_LOG = '''INSERT INTO activity(userid, username, log_action, log_detail)
        VALUES (%s,%s,%s)'''
        cursor.execute(ACTIVITY_LOG,(userid,username,'Edit Post', title))
        EDIT_SQL = '''UPDATE  post SET title = %s, content = %s, privacy = %s WHERE post_id = %s'''
        cursor.execute(EDIT_SQL, (title, content, privacy, post_id))
        UPDATED_SQL = '''SELECT * FROM post WHERE post_id = %s'''
        cursor.execute(UPDATED_SQL, (post_id,))
        return cursor.fetchall()

def get_edit_post(userid: int, postid: int, title) -> tuple:
    SQL = '''SELECT * FROM post WHERE post_id = %s'''
    cursor.execute(SQL, (post_id,))
    return cursor.fetchall()


def delete_post(userid: int, id: int) ->None:
    with DbManager(**DBCONFIG) as cursor:
        ACTIVITY_LOG = '''INSERT INTO activity(userid, username,log_action,log_detai)
        VALUES (%s,%s,%s,%s)'''
        cursor.execute(ACTIVITY_LOG,(userid, username, 'Delete Post', title))
        DELETE_SQL = '''DELETE FROM post WHERE post_id  = %s'''
        cursor.execute(DELETE_SQL, (id,))
        return redirect(url_for('blog'))
    # generate number and asks user to guess


def lucky_number(guess):
    my_number = random.randint(1, 3)
    print('DEBUG MODE:', my_number)
    if guess > my_number:
        response = 'GUESS LOWER'
        return response
    elif guess < my_number:
        response = 'GUESS HIGHER'
        return response
    else:
        response = f'You got it right my guess was {my_number}'
        return response


# password generator


def password_gen():
    number = ['1234567890']
    lower_case = ['abcdefghijklmnopqrstuvwxyz']
    upper_case = []
    for i in lower_case:
        upper_case.append(i.upper())
    # symbols = ['@!#$%&']
    gen = str(number + lower_case + upper_case)
    length = 10
    password = random.sample(gen, length)
    print(gen)
    return ' '.join(password)


# search phrase function


def search4letters(letter, phrase):
    result = list(set(letter).intersection(set(phrase)))
    return str(result)[1:-1]


# calc mi function


def bmi_calc(name: str, weight: int, height: float):
    bmi = int(weight) // float((height) ** 2)
    if bmi > 24:
        return f'{name.capitalize()}:You kinda fat hommie --- {bmi}'
    elif bmi < 12:
        return f'{name.capitalize()}: Eey you underweight bro --- {bmi}'
    else:
        return f'{name.capitalize()}: Bro you winning at this bmi shit --- {bmi}'
