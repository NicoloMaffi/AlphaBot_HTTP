import flask
import AlphaBot

serverweb = flask.Flask(__name__)

alphabot = AlphaBot.AlphaBot()
alphabot.stop()

@serverweb.route('/')
def index():
    return flask.render_template('movement.html')

@serverweb.route('/', methods=['POST'])
def move():
    if flask.request.method == 'POST':
        if flask.request.form.get('name') == 'dritto':
            alphabot.forward()
        elif flask.request.form.get('name') == 'indietro':
            alphabot.backward()
        elif flask.request.form.get('name') == 'destra':
            alphabot.right()
        elif flask.request.form.get('name') == 'sinistra':
            alphabot.left()
        elif flask.request.form.get('name') == 'fermo':
            alphabot.stop()
        else:
            print('sconosciuto')
    else:
        print('Utilizzare il metodo GET.')

    return flask.render_template('movement.html')

if __name__ == "__main__":
    serverweb.run(debug=True, host='localhost')
