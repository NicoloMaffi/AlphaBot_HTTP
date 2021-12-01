import flask

serverweb = flask.Flask(__name__)

@serverweb.route('/')
def index():
    return flask.render_template('index.html')

@serverweb.route('/', methods=['POST'])
def move():
    if flask.request.method == 'POST':
        if flask.request.form.get('direction') == 'forward':
            print("Forward")
        elif flask.request.form.get('direction') == 'backward':
            print("Backward")
        elif flask.request.form.get('direction') == 'right':
            print("Right")
        elif flask.request.form.get('direction') == 'left':
            print("Left")
        elif flask.request.form.get('direction') == 'stop':
            print("Stop")
        else:
            print("Unknown")
    else:
        print('Use POST method!')

    return flask.render_template('index.html')

if __name__ == "__main__":
    serverweb.run(debug=True, host='localhost')