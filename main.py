import hashlib
import flask
import sqlite3
import random
import string
import datetime
import time
import AlphaBot

# Charset for salt generation
CHARSET = string.ascii_letters + string.digits + string.punctuation

PEPPER = """N`_Dep(F%uzQ=|JV\\x)]XI[ByuQtB.VwUZ@z@|ySMx\\B5?uonW5"0*Pqik}4ntC4"""

DATABASE_PATH = './data.db'

# Error messages
NO_ERROR = "None"
EMPTY_FIELDS_ERROR = "Please fill every fields!"
WRONG_USERNAME_ERROR = "Invalid username. Please try again!"
WRONG_PASSWORD_ERROR = "Invalid password. Please try again!"
USERNAME_ALREADY_EXISTS_ERROR = "Username '%s' already exists. Please try another one!"
PASSWORDS_DONT_MATCH = "Passwords do not match. Please Try again!"
INTERNAL_ERROR = "We are experiencing some errors. Please try again later!"

# Web app initialization
app = flask.Flask(__name__)
# Secret key for sessions
app.secret_key = """_;Dr`Q6V2[cpMNY<$h>(343q\\o0q~J;a|x4\\+V4g_qw~XA$U]YZk.eIQq4;aqXCD"""

# AlphaBot controller initialization
alphabot = AlphaBot.AlphaBot()
alphabot.stop()

# Log in authentication
def log_in_check(username, password):
    # User input validation
    if username == "" or password == "":
        return EMPTY_FIELDS_ERROR

    # Database connection + error handling
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        curs = conn.cursor()
    except sqlite3.OperationalError:
        return INTERNAL_ERROR

    # Getting user data record from database + error handling
    try:
        rec = curs.execute("SELECT password, salt FROM users WHERE username = ?;", (username,)).fetchall()
    except sqlite3.OperationalError:
        return INTERNAL_ERROR
    finally:
        conn.close()
    
    # Username authentication
    if rec == []:
        return WRONG_USERNAME_ERROR

    # Getting hashed password and salt from record
    db_password = rec[0][0]
    salt = rec[0][1]
    
    # Password authentication
    if hashlib.sha512((password + salt + PEPPER).encode()).hexdigest() != db_password:
        return WRONG_PASSWORD_ERROR

    return NO_ERROR

# User registration
def sign_up_check(username, password, repeat_password):
    # User input validation
    if username == "" or password == "" or repeat_password == "":
        return EMPTY_FIELDS_ERROR

    # Matching passwords
    if password != repeat_password:
        return PASSWORDS_DONT_MATCH

    # Database connection + error handling
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        curs = conn.cursor()
    except sqlite3.OperationalError:
        return INTERNAL_ERROR

    # Getting user data record from database + error handling
    try:
        # If a match is found the user already exists
        if curs.execute(f"SELECT * FROM users WHERE username = ?;", (username,)).fetchall() != []:
            conn.close()
            return USERNAME_ALREADY_EXISTS_ERROR
    except sqlite3.OperationalError:
        conn.close()
        return INTERNAL_ERROR

    # Generating salt
    salt = "".join(random.choices(CHARSET, k = len(PEPPER)))
    # Hashing password: sha512(clear_password + salt + pepper)
    hashed_password = hashlib.sha512((password + salt + PEPPER).encode()).hexdigest()
    # Getting user sign up date
    sign_up_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Inserting user into database table + error handling
    try:
        curs.execute(f"INSERT INTO users VALUES (?, ?, ?, ?);", (username, hashed_password, salt, sign_up_date))
        conn.commit()
    except sqlite3.OperationalError:
        return INTERNAL_ERROR
    finally:
        conn.close()

    return NO_ERROR

# User log in tracking
def save_log_in(username):
    # Database connection + error handling
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        curs = conn.cursor()
    except sqlite3.OperationalError:
        return INTERNAL_ERROR

    log_in_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    curs.execute(f"INSERT INTO access_history VALUES (?, ?, ?)", (None, username, log_in_date))
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

@app.route('/', methods=['POST', 'GET'])
def index():
    error = None

    if flask.request.method == 'POST':
        if flask.request.form.get('log_in'):
            username = flask.request.form['username']
            password = flask.request.form['password']

            error =  log_in_check(username, password)

            if error == NO_ERROR:
                save_log_in(username)

                flask.session['username'] = username

                return flask.redirect(flask.url_for('controller'))
        elif flask.request.form.get('sign_up'):
            return flask.redirect(flask.url_for('sign_up'))

    return flask.render_template('index.html', error=error)

@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    error = None

    if flask.request.method == 'POST':
        if flask.request.form.get('confirm'):
            username = flask.request.form['username']
            password = flask.request.form['password']
            repeat_password = flask.request.form['repeat_password']

            error = sign_up_check(username, password, repeat_password)

            if error == NO_ERROR:
                return flask.redirect(flask.url_for('index'))

    return flask.render_template('sign_up.html', error=error)

@app.route('/set_movement', methods=['POST', 'GET'])
def set_movement():
    result = {"state": "error"}

    if flask.request.method == 'POST':
        movement = flask.request.form['movement']

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

        save_movement(movement, flask.session["username"])

        result = {"state": "normal"}

    return flask.jsonify(result)

@app.route('/controller', methods=['POST', 'GET'])
def controller():
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('index'))

    if flask.request.method == 'POST':
        if flask.request.form.get('log_out'):
            return flask.redirect(flask.url_for('log_out'))

    return flask.render_template('controller.html', complex_movements=complex_movements_pool())

@app.route("/log_out", methods=["POST", "GET"])
def log_out():
    flask.session.pop('username', default=None)

    return flask.redirect(flask.url_for('index'))

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")