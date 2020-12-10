from datetime import datetime
import random
from flask import Flask,request,render_template,abort
import mysql.connector

DBCONGIF = {
    'host': 'localhost',
    'user': 'admin',
    'password' : 'admin',
    'database' : 'myappDB'
}
#CREATE CONNECTION TO DB
conn = mysql.connector.connect(**DBCONGIF)
#CONFIG CURSOR TO ACCESS DB I.E READ AND WRITE
cursor = conn.cursor()

time_stamp = datetime.now().strftime('%c')
users = {
    'steve': '1234',
    "shammah": '1234',
    'admin' : 'admin',
    'superuser': '0000'
}
#activity log func
def log_details(username:str,action:str):
    with open('log.log','a') as log:
        print(f'{username.upper()} accessed the log on {time_stamp}\nAction: {action.upper()}|', file=log, end='\n',sep = '|')
        #print(username.form, username.remote_addr, username.user_agent, file=log, end='\n')
    return 'success'
#sign_up function to log details in txt file    
def sign_up(fname:str,lname:str,email:str,password:str,time_stamp:str):
    username = (' ').join((fname,lname))
    log_details(username,'signup')
    users[username] = password  
    signup = '''INSERT INTO signup (first_name,last_name, email,password) 
    VALUES
    (%s,%s,%s,%s)'''
    cursor.execute(signup,(fname,lname,email,password))
    conn.commit()
    cursor.close()
    conn.close()
    with open('signup.log', 'a') as signup:
        print(f'Username: {username.upper()}\nEmail : {email.capitalize()}\nPassword : {password}\nTimestamp: {time_stamp}|', file=signup, end='\n')
    users[fname] = password
    return('successful sign in')
#log in func takes in username and password
def log_in(username,password):
    for account in users:
        #ADD ADMIN LOG IN 
        if username in users:   #check username
            if users[username] == password: #check password
                log_details(username,'login')
                log = '''INSERT INTO login (username, password)
                VALUES
                (%s,%s)'''
                cursor.execute(log,(username,password))
                conn.commit()
                cursor.close()
                conn.close()
                return'successful login'
            else:
                return'wrong password'
        else:
            return 'User not found'
#func to view log
def view_log(username,password):
    log_details(username, 'view log')
    if username in users:
        if password == users[username]:
            with open('log.log') as vlog:
                content = vlog.read()
                new = []
                for item in content.split('|'):
                    new.append(item)
                return new
        else:
            return 'Wrong password'
    else:
        abort(401)
#FUNCTION TO UPDATE LOG
#ADD CODE TO CHECK IF ADMIN OR SUPERUSER
def update_log(update):
    log_details('admin' ,'update log')
    with open('log.log','w') as vlog:
        updates = input('New stuff: ')
        print(f'These are the new updates by admin\n{updates} \nOn: {time_stamp}|', file=vlog,end='\n')
    return 'successful log update'
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
    result.sort()
    return str(result)[1:-1]
#calc mi function
def bmi_calc(name: str,weight:int, height:float):
    bmi = int(weight) // float((height)** 2)
    with open('log.log', 'a') as user_log:
        print(f'{name.upper()}, calculated his bmi on {time_stamp} |', file=user_log, end='\n')
    with open('signup.log', 'a') as bmi_log:
        print(f'{name.upper()}, of weight {weight} and height {height} \n Got {bmi} as his bmi \n {time_stamp} |',file=bmi_log, end='\n ' )
        if bmi > 24:
            return f'{name.capitalize()}:You kinda fat hommie --- {bmi}'
        elif bmi < 12:
            return f'{name.capitalize()}: Eey you underweight bro --- {bmi}'
        else:
            return f'{name.capitalize()}: Bro you winning at this bmi shit --- {bmi}'
