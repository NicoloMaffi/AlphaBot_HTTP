import hashlib
import flask
import sqlite3
#import AlphaBot

serverweb = flask.Flask(__name__)

#alphabot = AlphaBot.AlphaBot()
#alphabot.stop()

def login_checker(username, password):
    res = False

    conn = sqlite3.connect('./data.db')
    curs = conn.cursor()

    row = curs.execute(f"SELECT password, salt FROM users WHERE username = '{username}';").fetchall()

    if row != []:
        res = hashlib.sha512((password + row[0][1]).encode()).hexdigest() == row[0][0]

    conn.close()

    return res

def complex_movements_pool():
    res = None

    conn = sqlite3.connect('./data.db')
    curs = conn.cursor()

    row = curs.execute(f"SELECT name FROM complex_movements;").fetchall()

    if row != []:
        res = [movement[0] for movement in row]

    conn.close()

    return res

@serverweb.route('/', methods=['POST', 'GET'])
def index():
    error = None

    if flask.request.method == 'POST':
        if flask.request.form.get('log_in'):
            username = flask.request.form.get('uname')
            password = flask.request.form.get('passwd')

            if login_checker(username, password):
                return flask.redirect(flask.url_for('controller'))
            else:
                error = 'Invalid credentials. Please Try again!'
        if flask.request.form.get('sign_in'):
            return flask.redirect(flask.url_for('signin'))

    return flask.render_template('index.html', error=error)

@serverweb.route('/signin', methods=['POST', 'GET'])
def signin():
    if flask.request.method == 'POST':
        pass

    return flask.render_template('signin.html')

@serverweb.route('/controller', methods=['POST', 'GET'])
def controller():
    if flask.request.method == 'POST':
        if flask.request.form.get('direction') == 'forward':
            #alphabot.forward()
            print("forward")
        elif flask.request.form.get('direction') == 'backward':
            #alphabot.backward()
            print("backward")
        elif flask.request.form.get('direction') == 'right':
            #alphabot.right()
            print("right")
        elif flask.request.form.get('direction') == 'left':
            #alphabot.left()
            print("left")
        elif flask.request.form.get('direction') == 'stop':
            #alphabot.stop()
            print("stop")
        else:
            print("Unknown")

    return flask.render_template('controller.html', complex_movements=complex_movements_pool())

if __name__ == "__main__":
    serverweb.run(debug=True, host="127.0.0.1")#host='0.0.0.0')