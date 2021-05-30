import os
import sys

from flask import Flask, Response, abort, render_template
from gevent import subprocess
from flask_sockets import Sockets

app = Flask(__name__)
sockets = Sockets(app)

SCRIPT_DIR = os.getenv('SCRIPT_DIR', os.path.dirname(os.path.realpath(__file__)) + '/scripts')


@app.route('/')
def index():
    return 'Hello World'


def process_socket(ws, args):
    print('start process:', ' '.join(args))
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while not ws.closed:
        try:
            for line in iter(p.stdout.readline, b''):
                ws.send(line)
            if p.poll() is None:
                ws.send("process closed stdout and stderr but didn't terminate; terminating now.")
                p.terminate()
        except:
            break
    print('client disconnected, killing process')
    p.terminate()


@app.route('/install')
def install():
    return render_template("run.html", path=f"/install")


@app.route('/run/<script>')
def run(script):
    return render_template("run.html", path=f"/run/{script}")


@sockets.route('/ws/install')
def install_socket(ws):
    return process_socket(ws, [sys.executable, '-m', 'pip', 'install', '-r', SCRIPT_DIR + '/requirements.txt'])


@sockets.route('/ws/run/<script>')
def run_socket(ws, script):
    scripts = os.listdir(SCRIPT_DIR)
    if script + '.py' not in scripts:
        abort(404, 'Script not found')

    return process_socket(ws, ['python', '-u', SCRIPT_DIR + '/' + script + '.py'])


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()

application = app
