import flask
import AlphaBot

serverweb = flask.Flask(__name__)

alphabot = AlphaBot.AlphaBot()
alphabot.stop()

@serverweb.route('/')
def index():
    return flask.render_template('index.html')

@serverweb.route('/', methods=['POST'])
def move():
    if flask.request.method == 'POST':
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
        else:
            print("Unknown")
    else:
        print('Use POST method!')

    return flask.render_template('index.html')

if __name__ == "__main__":
    serverweb.run(debug=True, host='0.0.0.0')