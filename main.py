import os
import sys
import gevent
from gevent import subprocess
from time import time

from flask import Flask, Response, abort, request

app = Flask(__name__)

SCRIPT_DIR = os.getenv('SCRIPT_DIR', os.path.dirname(os.path.realpath(__file__)) + '/scripts')


@app.route('/')
def index():
    return 'Hello World'


def process_response(args, timeout=60):
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stoptime = [time() + timeout]

    def stop():
        while p.poll() is None:
            if time() > stoptime[0]:
                print('Terminated')
                p.kill()
                break
            gevent.sleep(stoptime[0] - time())

    gevent.spawn(stop)

    def generate():
        while True:
            stoptime[0] = time() + timeout
            r = p.stdout.readline()
            if len(r) == 0:
                break
            yield r

    return Response(generate(), mimetype='text/event-stream')


@app.route('/install')
def install():
    return process_response([sys.executable, '-m', 'pip', 'install', '-r', SCRIPT_DIR + '/requirements.txt'],
                            request.args.get('timeout', default=600, type=int))


@app.route('/run/<script>')
def run(script):
    scripts = os.listdir(SCRIPT_DIR)
    if script + '.py' not in scripts:
        abort(404, 'Script not found')

    return process_response(['python', SCRIPT_DIR + '/' + script + '.py'],
                            request.args.get('timeout', default=60, type=int))


@app.route('/test')
def test():
    n = request.args.get('n', default=10, type=int)

    def generate():
        for i in range(n):
            yield str(i) + '\n'
            gevent.sleep(1)
    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run()

application = app
