import os
import subprocess
import sys
import threading
from time import time, sleep

from flask import Flask, Response, abort, request

app = Flask(__name__)

SCRIPT_DIR = os.getenv('SCRIPT_DIR', os.path.dirname(os.path.realpath(__file__)) + '/scripts')


@app.route('/')
def index():
    return 'Hello World'


def process_response(process, timeout=60):
    stoptime = [time() + timeout]

    def stop():
        while process.poll() is None:
            if time() > stoptime[0]:
                print('Terminated')
                process.kill()
                break
            sleep(stoptime[0] - time())

    threading.Thread(target=stop).start()

    def generate():
        while True:
            stoptime[0] = time() + timeout
            r = process.stdout.readline()
            if len(r) == 0:
                break
            yield r

    return Response(generate(), mimetype='text/event-stream')


@app.route('/install')
def install():
    p = subprocess.Popen([sys.executable, '-m', 'pip', 'install', '-r', SCRIPT_DIR + '/requirements.txt'],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process_response(p, request.args.get('timeout', default=600, type=int))


@app.route('/run/<script>')
def run(script):
    scripts = os.listdir(SCRIPT_DIR)
    if script + '.py' not in scripts:
        abort(404, 'Script not found')

    p = subprocess.Popen(['python', SCRIPT_DIR + '/' + script + '.py'],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    return process_response(p, request.args.get('timeout', default=60, type=int))


@app.route('/test')
def test():
    n = request.args.get('n', default=10, type=int)
    
    def generate():
        for i in range(n):
            yield str(i) + '\n'
            sleep(1)
    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run()

application = app
