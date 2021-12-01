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
        match flask.request.form.get('direction'):
            case 'forward':
                alphabot.forward()
            case 'backward':
                alphabot.backward()
            case 'right':
                alphabot.right()
            case 'left':
                alphabot.left()
            case 'stop':
                alphabot.stop()
            case _:
                print("Unknown")
    else:
        print('Use POST method!')

    return flask.render_template('index.html')

if __name__ == "__main__":
    serverweb.run(debug=True, host='0.0.0.0')