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

# error messages
NO_ERROR = "None"
EMPTY_FIELDS_ERROR = "Please fill every fields!"
WRONG_USERNAME_ERROR = "Invalid username. Please try again!"
WRONG_PASSWORD_ERROR = "Invalid password. Please try again!"
USERNAME_ALREADY_EXISTS_ERROR = "Username '%s' already exists. Please try another one!"
PASSWORDS_DONT_MATCH = "Passwords do not match. Please Try again!"

webserver = flask.Flask(__name__)
# for sessions
webserver.secret_key = "VX9R76p}e53.:x!CD,O1lKYFz+K~Ld\"%"

alphabot = AlphaBot.AlphaBot()
alphabot.stop()

#funcion for checking credentials
def log_in_check(username, password):
    if username == "" or password == "":
        return EMPTY_FIELDS_ERROR

    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()
    # try if the credential are in the db and match with the input
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

# funcion that put the data in the db on sign up
def sign_up_check(username, password, repeat_password):
    if username == "" or password == "" or repeat_password == "":
        return EMPTY_FIELDS_ERROR

    if password != repeat_password:
        conn.close()
        return PASSWORDS_DONT_MATCH

    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    if curs.execute(f"SELECT * FROM users WHERE username = ?;", (username,)).fetchall() != []:
        conn.close()
        return USERNAME_ALREADY_EXISTS_ERROR

    salt = "".join(random.choices(ALPHABET, k = len(PEPPER)))
    hashed_password = hashlib.sha512((password + salt + PEPPER).encode()).hexdigest()
    sign_up_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    curs.execute(f"INSERT INTO users VALUES (?, ?, ?, ?);", (username, hashed_password, salt, sign_up_date))
    conn.commit()

    conn.close()

    return NO_ERROR

# save the log in in the db
def save_log_in(username):
    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    log_in_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    curs.execute(f"INSERT INTO access_history VALUES (?, ?, ?)", (None, username, log_in_date))
    conn.commit()

    conn.close()

# read the complex movement in the db and return it
def complex_movements_pool():
    res = None

    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    row = curs.execute(f"SELECT movement_name FROM complex_movements;").fetchall()

    if row != []:
        res = [movement[0] for movement in row]

    conn.close()

    return res
# 
def instruction_parser(name):
    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    instruction = curs.execute(f"SELECT instruction FROM complex_movements WHERE movement_name = ?;", (name,)).fetchall()

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

def save_movement(movement, username):
    conn = sqlite3.connect(DATABASE_PATH)
    curs = conn.cursor()

    input_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    curs.execute(f"INSERT INTO movement_history VALUES (?, ?, ?, ?);", (None, username, movement, input_date))
    conn.commit()

    conn.close()

@webserver.route('/', methods=['POST', 'GET'])
def index():
    error = None

    if flask.request.method == 'POST':
        if flask.request.form.get('log_in'):
            username = flask.request.form.get('username')
            password = flask.request.form.get('password')

            error =  log_in_check(username, password)

            if error == NO_ERROR:
                save_log_in(username)

                flask.session["username"] = username

                return flask.redirect(flask.url_for('controller'))
        elif flask.request.form.get('sign_up'):
            return flask.redirect(flask.url_for('sign_up'))

    return flask.render_template('index.html', error=error)

@webserver.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    error = None

    if flask.request.method == 'POST':
        if flask.request.form.get('confirm'):
            username = flask.request.form.get('username')
            password = flask.request.form.get('password')
            repeat_password = flask.request.form.get('repeat_password')

            error = sign_up_check(username, password, repeat_password)

            if error == NO_ERROR:
                return flask.redirect(flask.url_for('index'))

    return flask.render_template('sign_up.html', error=error)

@webserver.route('/set_movement', methods=['POST', 'GET'])
def set_movement():
    result = {"state": "error"}

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

        save_movement(movement, flask.session.get("username"))

        result = {"state": "normal"}

    return flask.jsonify(result)

@webserver.route('/controller', methods=['POST', 'GET'])
def controller():
    if not flask.session["username"]:
        return flask.redirect(flask.url_for('index'))

    return flask.render_template('controller.html', complex_movements=complex_movements_pool())

@webserver.route("/log_out", methods=["POST", "GET"])
def log_out():
    flask.session.pop('username', default=None)

    return flask.redirect(flask.url_for('index'))

if __name__ == "__main__":
    webserver.run(debug=True, host="127.0.0.1")
