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
        match flask.request.form.get('name'):
            case 'dritto':
                alphabot.forward()
            case 'sinistra':
                alphabot.left()
            case 'fermo':
                alphabot.stop()
            case 'destra':
                alphabot.right()
            case 'indietro':
                alphabot.backward()
            case _:
                print('sconosciuto')
    else:
        print('Utilizzare il metodo GET.')

    return flask.render_template('movement.html')

if __name__ == "__main__":
    serverweb.run(debug=True, host='localhost')