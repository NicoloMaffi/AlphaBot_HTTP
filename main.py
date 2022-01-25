import hashlib
import flask
import sqlite3
import random
import string
import datetime
import time
import AlphaBot_test

DATABASE_PATH = './data.db'

NO_ERROR = 0
EMPTY_FIELDS_ERROR = -1
WRONG_UNAME_ERROR = -2
WRONG_PASSWD_ERROR = -3
UNAME_ALREADY_EXISTS_ERROR = -4
PASSWDS_DONT_MATCH = -5

serverweb = flask.Flask(__name__)

alphabot = AlphaBot_test.AlphaBot()
alphabot.stop()

def login_checker(username, password):
    if username == "" or password == "":
        return EMPTY_FIELDS_ERROR

    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    row = curs.execute(f"SELECT password, salt FROM users WHERE username = '{username}';").fetchall()

    if row == []:
        conn.close()
        return WRONG_UNAME_ERROR
    
    if hashlib.sha512((password + row[0][1]).encode()).hexdigest() != row[0][0]:
        conn.close()
        return WRONG_PASSWD_ERROR

    conn.close()

    return NO_ERROR

def signin_checker(username, password1, password2):
    if username == "" or password1 == "" or password2 == "":
        return EMPTY_FIELDS_ERROR

    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    if curs.execute(f"SELECT * FROM users WHERE username = '{username}';").fetchall() != []:
        conn.close()
        return UNAME_ALREADY_EXISTS_ERROR

    if password1 != password2:
        conn.close()
        return PASSWDS_DONT_MATCH

    salt = "".join(random.choices(string.printable, k = random.randint(10, 20)))
    hashed_password = hashlib.sha512((password1 + salt).encode()).hexdigest()
    signin_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    curs.execute(f"INSERT INTO users VALUES (?, ?, ?, ?);", (username, hashed_password, salt, signin_date))
    conn.commit()

    conn.close()

    return NO_ERROR

def save_login(username):
    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    login_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    curs.execute(f"INSERT INTO accesses_history VALUES (?, ?, ?)", (None, username, login_date))
    conn.commit()

    conn.close()

def complex_movements_pool():
    res = None

    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    row = curs.execute(f"SELECT name FROM complex_movements;").fetchall()

    if row != []:
        res = [movement[0] for movement in row]

    conn.close()

    return res

def instruction_parser(name):
    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    instruction = curs.execute(f"SELECT instruction FROM complex_movements WHERE name = '{name}';").fetchall()

    conn.close()

    instruction = instruction[0][0].split(":")

    for i in range(0, len(instruction), 2):
        dir = instruction[i].upper()
        wait = int(instruction[i + 1])

        if dir == "F":
            alphabot.forward()
        elif dir == "B":
            alphabot.backward()
        elif dir == "L":
            alphabot.left()
        elif dir == "R":
            alphabot.right()
        elif dir == "S":
            alphabot.stop()

        time.sleep(wait / 1000)

def save_movements_input(movement):
    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    input_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    curs.execute(f"SELECT user_cod, access_date FROM accesses_history")
    lastPersonAccess = curs.fetchall()[-1][0]

    curs.execute(f"INSERT INTO movements_history VALUES (?, ?, ?, ?)", (None, lastPersonAccess, movement, input_date))
    
    conn.commit()

    conn.close()

@serverweb.route('/', methods=['POST', 'GET'])
def index():
    error_mssg = None
    error_code = NO_ERROR

    if flask.request.method == 'POST':
        if flask.request.form.get('log_in'):
            username = flask.request.form.get('uname')
            password = flask.request.form.get('passwd')

            error_code = login_checker(username, password)

            if error_code == EMPTY_FIELDS_ERROR:
                error_mssg = "Please fill every fields!"
            elif error_code == WRONG_UNAME_ERROR:
                error_mssg = "Invalid username. Please try again!"
            elif error_code == WRONG_PASSWD_ERROR:
                error_mssg = "Invalid password. Please try again!"
            else:
                save_login(username)
                return flask.redirect(flask.url_for('controller'))
        elif flask.request.form.get('sign_in'):
            return flask.redirect(flask.url_for('signin'))

    return flask.render_template('index.html', error=error_mssg)

@serverweb.route('/signin', methods=['POST', 'GET'])
def signin():
    error_mssg = None
    error_code = NO_ERROR

    if flask.request.method == 'POST':
        if flask.request.form.get('confirm'):
            username = flask.request.form.get('uname')
            password1 = flask.request.form.get('passwd')
            password2 = flask.request.form.get('repasswd')

            error_code = signin_checker(username, password1, password2)

            if error_code == EMPTY_FIELDS_ERROR:
                error_mssg = "Please fill every fields!"
            elif error_code == UNAME_ALREADY_EXISTS_ERROR:
                error_mssg = f"Username '{username}' already exists. Please try another one!"
            elif error_code == PASSWDS_DONT_MATCH:
                error_mssg = "Passwords do not match. Please Try again!"
            else:
                return flask.redirect(flask.url_for('index'))

    return flask.render_template('signin.html', error=error_mssg)

@serverweb.route('/controller', methods=['POST', 'GET'])
def controller():
    if flask.request.method == 'POST':

        movement = flask.request.form.get('direction')
        if flask.request.form.get('direction') == 'forward':
            alphabot.forward()
        elif flask.request.form.get('direction') == 'backward':
            alphabot.backward()
        elif flask.request.form.get('direction') == 'right':
            alphabot.right()
        elif flask.request.form.get('direction') == 'left':
            alphabot.left()
        elif flask.request.form.get('direction') == 'stop':
            alphabot.stop()
        elif flask.request.form.get('submitmov'):
            movement = flask.request.form.get('complexmovspool')
            instruction_parser(movement)

        save_movements_input(movement)

    return flask.render_template('controller.html', complex_movements=complex_movements_pool())

if __name__ == "__main__":
    serverweb.run(debug=True, host="127.0.0.1")#host='0.0.0.0')