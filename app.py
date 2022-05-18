import hashlib
import flask
import sqlite3
import random
import string
import datetime
import time
import lib.AlphaBot as AlphaBot

CHARSET = string.ascii_letters + string.digits + string.punctuation

PEPPER = """N`_Dep(F%uzQ=|JV\\x)]XI[ByuQtB.VwUZ@z@|ySMx\\B5?uonW5"0*Pqik}4ntC4"""

DATABASE_PATH = './data/data.db'

NO_ERROR = "None"
EMPTY_FIELDS_ERROR = "Please fill every fields!"
WRONG_USERNAME_ERROR = "Invalid username. Please try again!"
WRONG_PASSWORD_ERROR = "Invalid password. Please try again!"
USERNAME_ALREADY_EXISTS_ERROR = "Username '{}' already exists. Please try another one!"
PASSWORDS_DONT_MATCH = "Passwords do not match. Please Try again!"
INTERNAL_ERROR = "We are experiencing some errors. Please try again later!"

app = flask.Flask(__name__)
app.secret_key = """_;Dr`Q6V2[cpMNY<$h>(343q\\o0q~J;a|x4\\+V4g_qw~XA$U]YZk.eIQq4;aqXCD"""

alphabot = AlphaBot.AlphaBot()
alphabot.stop()

def log_in_check(username, password):
    if username == "" or password == "":
        return EMPTY_FIELDS_ERROR

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        curs = conn.cursor()
    except sqlite3.OperationalError:
        return INTERNAL_ERROR

    try:
        rec = curs.execute("SELECT password, salt FROM users WHERE username = ?;", (username,)).fetchall()
    except sqlite3.OperationalError:
        return INTERNAL_ERROR
    finally:
        conn.close()
    
    if rec == []:
        return WRONG_USERNAME_ERROR

    db_password = rec[0][0]
    salt = rec[0][1]

    if hashlib.sha512((password + salt + PEPPER).encode()).hexdigest() != db_password:
        return WRONG_PASSWORD_ERROR

    return NO_ERROR

def sign_up_check(username, password, repeat_password):
    if username == "" or password == "" or repeat_password == "":
        return EMPTY_FIELDS_ERROR

    if password != repeat_password:
        return PASSWORDS_DONT_MATCH

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        curs = conn.cursor()
    except sqlite3.OperationalError:
        return INTERNAL_ERROR

    try:
        if curs.execute(f"SELECT * FROM users WHERE username = ?;", (username,)).fetchall() != []:
            conn.close()
            return USERNAME_ALREADY_EXISTS_ERROR.format(username)
    except sqlite3.OperationalError:
        conn.close()
        return INTERNAL_ERROR

    salt = "".join(random.choices(CHARSET, k = len(PEPPER)))
    hashed_password = hashlib.sha512((password + salt + PEPPER).encode()).hexdigest()
    sign_up_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        curs.execute(f"INSERT INTO users VALUES (?, ?, ?, ?);", (username, hashed_password, salt, sign_up_date))
        conn.commit()
    except sqlite3.OperationalError:
        return INTERNAL_ERROR
    finally:
        conn.close()

    return NO_ERROR

def save_log_in(username):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        curs = conn.cursor()
    except sqlite3.OperationalError:
        return INTERNAL_ERROR

    log_in_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        curs.execute(f"INSERT INTO access_history VALUES (?, ?, ?)", (None, username, log_in_date))
        conn.commit()
    except sqlite3.OperationalError:
        return INTERNAL_ERROR
    finally:
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

@app.route('/', methods = ["GET", "POST"])
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

@app.route('/sign_up', methods = ["GET", "POST"])
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

@app.route('/set_movement', methods = ["GET", "POST"])
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

@app.route('/controller', methods = ["GET", "POST"])
def controller():
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('index'))

    if flask.request.method == 'POST':
        if flask.request.form['log_out']:
            return flask.redirect(flask.url_for('log_out'))

    return flask.render_template('controller.html', complex_movements=complex_movements_pool())

@app.route("/log_out", methods = ["GET", "POST"])
def log_out():
    flask.session.pop('username', default = None)

    return flask.redirect(flask.url_for('index'))

# Web API

@app.route("/api/v1/sensors/obstacles")
def obstacles_api():
    return flask.jsonify(alphabot.getObstacleSensorsStatus())

@app.route("/api/v1/motors/left", methods = ["GET"])
def left_motors_api():
    resp = {"status": 1}

    if flask.request.method == "GET":
        try:
            pwm = flask.request.args.get("pwm")
            time = flask.request.args.get("time")

            alphabot.setMotor(int(pwm), 0, float(time))
        except:
            resp["status"] = 0
    else:
        resp["status"] = 0

    return flask.jsonify(resp)

@app.route("/api/v1/motors/right", methods = ["GET"])
def right_motors_api():
    resp = {"status": 1}

    if flask.request.method == "GET":
        try:
            pwm = flask.request.args.get("pwm")
            time = flask.request.args.get("time")

            alphabot.setMotor(0, int(pwm), float(time))
        except:
            resp["status"] = 0
    else:
        resp["status"] = 0

    return flask.jsonify(resp)

@app.route("/api/v1/motors/both", methods = ["GET"])
def both_motors_api():
    resp = {"status": 1}

    if flask.request.method == "GET":
        try:
            pwmL = flask.request.args.get("pwmL")
            pwmR = flask.request.args.get("pwmR")
            time = flask.request.args.get("time")

            alphabot.setMotor(int(pwmL), int(pwmR), float(time))
        except:
            resp["status"] = 0
    else:
        resp["status"] = 0

    return flask.jsonify(resp)

@app.route("/api/v1/camera", methods = ["GET"])
def camera():
    pass

if __name__ == "__main__":
    print('\n\
        888b     d888  .d8888b.     888b     d888      8888888b.  d8b\n\
        8888b   d8888 d88P  "88b    8888b   d8888      888   Y88b Y8P\n\
        88888b.d88888 Y88b. d88P    88888b.d88888      888    888\n\
        888Y88888P888  "Y8888P"     888Y88888P888      888   d88P 888\n\
        888 Y888P 888 .d88P88K.d88P 888 Y888P 888      8888888P"  888\n\
        888  Y8P  888 888"  Y888P"  888  Y8P  888      888        888\n\
        888   "   888 Y88b .d8888b  888   "   888      888        888\n\
        888       888  "Y8888P" Y88b888       888      888        888\n\
    ')

    app.run(debug = False, host = "0.0.0.0")