import hashlib
import flask
import sqlite3
import random
import string
import datetime
import time
import AlphaBot

ALPHABET = string.ascii_letters + string.digits + string.punctuation

PEPPER = """N`_Dep(F%uzQ=|JV\\x)]XI[ByuQtB.VwUZ@z@|ySMx\\B5?uonW5"0*Pqik}4ntC4}8GZd4/pdYDv(h6KGz)Prf0c^R:#&g_6]R-hR:tlI(3n5aey3NB3$OiabgCru?Po"""

DATABASE_PATH = './data.db'

NO_ERROR = "None"
EMPTY_FIELDS_ERROR = "Please fill every fields!"
WRONG_USERNAME_ERROR = "Invalid username. Please try again!"
WRONG_PASSWORD_ERROR = "Invalid password. Please try again!"
USERNAME_ALREADY_EXISTS_ERROR = "Username '%s' already exists. Please try another one!"
PASSWORDS_DONT_MATCH = "Passwords do not match. Please Try again!"

webserver = flask.Flask(__name__)

alphabot = AlphaBot.AlphaBot()
alphabot.stop()

def login_check(username, password):
    if username == "" or password == "":
        return EMPTY_FIELDS_ERROR

    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    try:
        row = curs.execute("SELECT password, salt FROM users WHERE username = ?;", (username,)).fetchall()
    except:
        print("Error")

    if row == []:
        conn.close()
        return WRONG_USERNAME_ERROR

    salt = row[0][1]
    db_password = row[0][0]
    
    if hashlib.sha512((password + salt + PEPPER).encode()).hexdigest() != db_password:
        conn.close()
        return WRONG_PASSWORD_ERROR

    conn.close()

    return NO_ERROR

def signin_checker(username, password1, password2):
    if username == "" or password1 == "" or password2 == "":
        return EMPTY_FIELDS_ERROR

    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    if curs.execute(f"SELECT * FROM users WHERE username = '{username}';").fetchall() != []:
        conn.close()
        return USERNAME_ALREADY_EXISTS_ERROR

    if password1 != password2:
        conn.close()
        return PASSWORDS_DONT_MATCH

    salt = "".join(random.choices(ALPHABET, k = len(PEPPER)))
    hashed_password = hashlib.sha512((password1 + salt + PEPPER).encode()).hexdigest()
    signin_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    curs.execute(f"INSERT INTO users VALUES (?, ?, ?, ?);", (username, hashed_password, salt, signin_date))
    conn.commit()

    conn.close()

    return NO_ERROR

def save_login(username):
    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    login_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    curs.execute(f"INSERT INTO access_history VALUES (?, ?, ?)", (None, username, login_date))
    conn.commit()

    conn.close()

def complex_movements_pool():
    res = None

    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    row = curs.execute(f"SELECT movement_name FROM complex_movements;").fetchall()

    if row != []:
        res = [movement[0] for movement in row]

    conn.close()

    return res

def instruction_parser(name):
    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    instruction = curs.execute(f"SELECT instruction FROM complex_movements WHERE movement_name = '{name}';").fetchall()

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

def save_movement(movement):
    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    username = flask.request.cookies.get("username")
    input_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    curs.execute(f"INSERT INTO movement_history VALUES (?, ?, ?, ?);", (None, username, movement, input_date))
    conn.commit()

    conn.close()

@webserver.route('/', methods=['POST', 'GET'])
def index():
    error_mssg = None

    if flask.request.method == 'POST':
        if flask.request.form.get('log_in'):
            username = flask.request.form.get('uname')
            password = flask.request.form.get('passwd')

            error =  login_check(username, password)

            if error == NO_ERROR:
                save_login(username)

                resp = flask.make_response(flask.redirect(flask.url_for('controller_page')))
                resp.set_cookie("username", username)

                return resp
            else:
                error_mssg = error
        elif flask.request.form.get('sign_in'):
            return flask.redirect(flask.url_for('signin'))

    return flask.render_template('index.html', error=error_mssg)

@webserver.route('/signin', methods=['POST', 'GET'])
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
            elif error_code == USERNAME_ALREADY_EXISTS_ERROR:
                error_mssg = f"Username '{username}' already exists. Please try another one!"
            elif error_code == PASSWORDS_DONT_MATCH:
                error_mssg = "Passwords do not match. Please Try again!"
            else:
                return flask.redirect(flask.url_for('index'))

    return flask.render_template('signin.html', error=error_mssg)

@webserver.route('/controller_page', methods=['POST', 'GET'])
def controller_page():
    return flask.render_template('controller.html', complex_movements=complex_movements_pool())

@webserver.route('/controller', methods=['POST', 'GET'])
def controller():
    result = {"state": "ERROR"}

    if flask.request.method == 'POST':
        movement = flask.request.form.get('movement')

        if movement == 'forward':
            alphabot.forward()
        elif movement == 'backward':
            alphabot.backward()
        elif movement == 'right':
            alphabot.right()
        elif movement == 'left':
            alphabot.left()
        elif movement == 'stop':
            alphabot.stop()
        else:
            instruction_parser(movement)

        save_movement(movement)

        result = {"state": "OK"}

    return flask.jsonify(result)

if __name__ == "__main__":
    webserver.run(debug=True, host="127.0.0.1")