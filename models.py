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
        LOG_ACTIVITY = '''INSERT INTO activity(username, log_action, log_detail)
        VALUES (%s,%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(username,'Sign Up',str(fname,lname)))
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
                    LOG_ACTIVITY = '''INSERT INTO activity(username, log_action, log_detail)
                    VALUES (%s,%s,%s)'''
                    cursor.execute(LOG_ACTIVITY,(username,'Log In','Success'))
                    SQL = '''SELECT * FROM post WHERE author  = %s'''
                    posts = cursor.execute(SQL, (username,))
                    return posts
                # TO GET  POST WRITTEN BY USERNAME
                else:
                    LOG_ACTIVITY = '''INSERT INTO activity(username, log_action, log_detail)
                    VALUES (%s,%s,%s)'''
                    cursor.execute(LOG_ACTIVITY,(username,'Log In','Wrong Password'))
                    response = 'Wrong password!!'
                    return response
        else:
            LOG_ACTIVITY = '''INSERT INTO activity(username, log_action, log_detail)
            VALUES (%s,%s,%s)'''
            cursor.execute(LOG_ACTIVITY,(username,'Log In','User Not Found'))
            response = 'Username not found!!'
            return response


# ADMIN PANEL

def admin(username: str, userid: int) -> list:
     with DbManager(**DBCONFIG) as cursor:
        LOG_ACTIVITY = '''INSERT INTO activity(userid,username, log_action)
        VALUES (%s,%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(userid,username,'Admin Panel'))
        USERS_SQL = '''SELECT * FROM users'''
        cursor.execute(USERS_SQL)
        users = cursor.fetchall()
        COMMENT_SQL = '''SELECT * FROM comments'''
        cursor.execute(COMMENT_SQL)
        comments = cursor.fetchall()
        ACTIVITY_LOG = '''SELECT * FROM activity'''
        cursor.execute(ACTIVITY_LOG)
        logs = cursor.fetchall()
        POST_SQL = '''SELECT * FROM post'''
        cursor.execute(POST_SQL)
        posts = cursor.fetchall()
        UPLOAD_SQL = '''SELECT * FROM uploads '''
        cursor.execute(UPLOAD_SQL)
        uploads = cursor.fetchall()
        return [users, comments, logs, posts, uploads]

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
        LOG_ACTIVITY = '''INSERT INTO activity(username, log_action)
        VALUES (%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(username,'Profile Visit'))
        PROFILE_SQL = '''SELECT * FROM users WHERE username = %s'''
        cursor.execute(PROFILE_SQL, (username,))
        return cursor.fetchall()


# TO DO LIST
def add_to_do(userid: int, task: str, status: str) -> None:
    with DbManager(**DBCONFIG) as cursor:
        LOG_ACTIVITY = '''INSERT INTO activity(userid, log_action, log_detail)
        VALUES (%s,%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(userid,'To-Do',status))
        SQL = '''INSERT INTO ToDoTest (TaskName, TaskStatus, userid) VALUES (%s, %s, %s) '''
        return cursor.execute(SQL, (task, status, userid))
        



def get_to_do(user_id: int) -> tuple:
    with DbManager(**DBCONFIG) as cursor:
        SQL = """SELECT * FROM ToDoTest WHERE userid= %s """
        cursor.execute(SQL, (user_id,))
        return cursor.fetchall()


def edit_to_do(id: int, username: str, task: str, status: str) -> tuple:
    with DbManager(**DBCONFIG) as cursor:
        LOG_ACTIVITY = '''INSERT INTO activity(username, log_action, log_detail)
        VALUES (%s,%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(username,'Edit To-Do', id))
        SQL = '''UPDATE ToDoTest SET task = %s, status = %s  WHERE id = %s'''
        return cursor.execute(SQL, (task, status, username, id))


def task_delete(taskid: int, username: str, userid: int):
    with DbManager(**DBCONFIG) as cursor:
        LOG_ACTIVITY = '''INSERT INTO activity(userid, username, log_action, log_detail)
        VALUES (%s,%s,%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(userid, username,'Delete To-Do', taskid))
        DELETE_TASK  = '''DELETE FROM ToDoTest WHERE taskid = %s'''
        return cursor.execute(DELETE_TASK, (taskid,))


def edit_profile(userid, first_name, last_name, email, username, about):
    with DbManager(**DBCONFIG) as cursor:
        LOG_ACTIVITY = '''INSERT INTO activity(userid, username, log_action)
        VALUES (%s,%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(userid,username,'Edit Profile'))
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
                LOG_ACTIVITY = '''INSERT INTO activity(userid, log_action, log_detail)
                VALUES (%s,%s,%s)'''
                cursor.execute(LOG_ACTIVITY,(userid,'View Log', 'Success'))
                return log_data
            else:
                LOG_ACTIVITY = '''INSERT INTO activity(userid, log_action, log_detail)
                VALUES (%s,%s,%s)'''
                cursor.execute(LOG_ACTIVITY,(userid,'View Log', 'Wrong passord'))
                response = "WRONG PASSWORD!!"
                return response
        else:
            LOG_ACTIVITY = '''INSERT INTO activity(userid, log_action, log_detail)
            VALUES (%s,%s,%s)'''
            cursor.execute(LOG_ACTIVITY,(userid,'View Log', 'Restricted Access'))
            abort(401)


# CREATE POST


def create_post(author, title, content, privacy, userid: int) -> None:
    with DbManager(**DBCONFIG) as cursor:
        LOG_ACTIVITY = '''INSERT INTO activity(userid,username, log_action, log_detail)
        VALUES (%s,%s,%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(userid,author,'Create Post', title))
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
        LOG_ACTIVITY = '''INSERT INTO activity(userid,username, log_action, log_detail)
        VALUES (%s,%s,%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(userid,username,'Comment',post_id))
        SQL = ''' INSERT INTO comments (userid, post_id, comment_body) VALUES (%s, %s, %s)'''
        return cursor.execute(SQL,(userid,post_id,comment))


#  DELETE COMMENT


def del_comment(userid: int,username: str, comment_id: int, comment: str, post_id: int)  ->None:
    with DbManager(**DBCONFIG) as cursor:
        LOG_ACTIVITY = '''INSERT INTO activity(userid,username, log_action, log_detail)
        VALUES (%s,%s,%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(userid,username,'Delete Comment',comment_id))
        DELETE_SQL = ''' DELETE  FROM comments WHERE comment_id = %s'''
        return cursor.execute(DELETE_SQL,(comment_id,))


# GET POST FROM DB


def get_all_posts(userid: int) -> 'Posts':
    # CHECK USER ID AND RETURN PUBLIC AND ALL USER ID'S POST
    with DbManager(**DBCONFIG) as cursor:
        LOG_ACTIVITY = '''INSERT INTO activity(userid, log_action)
        VALUES (%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(userid,'Get Posts'))
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


def db_search(userid: int, username: str, keyword: str) -> list:
    with DbManager(**DBCONFIG) as cursor:
        LOG_ACTIVITY = '''INSERT INTO activity(userid, username, log_action, log_detail)
        VALUES (%s,%s,%s, %s)'''
        cursor.execute(LOG_ACTIVITY,(userid, username, 'Search', keyword))
        POST_SQL =  """SELECT content, post_id FROM post WHERE content LIKE CONCAT('%', %s, '%')"""
        cursor.execute(POST_SQL, (keyword,))
        posts = cursor.fetchall()
        TITLE_SQL = "SELECT title, post_id FROM post WHERE title LIKE CONCAT('%', %s, '%')"
        cursor.execute(TITLE_SQL, (keyword,))
        titles = cursor.fetchall()
        COMMENT_SQL = "SELECT comment_body, post_id FROM comments WHERE comment_body LIKE CONCAT('%', %s, '%')"
        cursor.execute(COMMENT_SQL, (keyword,))
        comments = cursor.fetchall()
        USER_SQL = "SELECT username FROM users WHERE username LIKE %s";
        cursor.execute(USER_SQL, (keyword,))
        users = cursor.fetchall()
        return [users,posts, titles, comments]



def edit_post(userid: int,post_id: int, author: str, title: str, content: str, privacy: str) -> list: #UNUSED FUNCTION
    with DbManager(**DBCONFIG) as cursor:
        LOG_ACTIVITY = '''INSERT INTO activity(userid, username, log_action, log_detail)
        VALUES (%s,%s,%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(userid,author,'Edit Post', title))
        EDIT_SQL = '''UPDATE  post SET title = %s, content = %s, privacy = %s WHERE post_id = %s'''
        cursor.execute(EDIT_SQL, (title, content, privacy, post_id))
        UPDATED_SQL = '''SELECT * FROM post WHERE post_id = %s'''
        cursor.execute(UPDATED_SQL, (post_id,))
        return cursor.fetchall()

def get_edit_post(userid: int, postid: int, title) -> tuple:
    with DbManager(**DBCONFIG) as cursor:
        SQL = '''SELECT * FROM post WHERE post_id = %s'''
        cursor.execute(SQL, (postid,))
        return cursor.fetchall()


def delete_post(userid: int, id: int) ->None:
    with DbManager(**DBCONFIG) as cursor:
        LOG_ACTIVITY = '''INSERT INTO activity(userid, username,log_action,log_detai)
        VALUES (%s,%s,%s,%s)'''
        cursor.execute(LOG_ACTIVITY,(userid, username, 'Delete Post', title))
        DELETE_SQL = '''DELETE FROM post WHERE post_id  = %s'''
        return cursor.execute(DELETE_SQL, (id,))
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
