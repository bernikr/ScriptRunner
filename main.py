import os
import sys

from flask import Flask, Response, abort, request
from gevent import subprocess, sleep

app = Flask(__name__)

SCRIPT_DIR = os.getenv('SCRIPT_DIR', os.path.dirname(os.path.realpath(__file__)) + '/scripts')


@app.route('/')
def index():
    return 'Hello World'


def process_response(args):
    print('start process: ', ' '.join(args))
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def generate():
        try:
            for line in iter(p.stdout.readline, b''):
                yield line
            if p.poll() is None:
                print("process closed stdout and stderr but didn't terminate; terminating now.")
                p.terminate()
        except GeneratorExit:
            # occurs when new output is yielded to a disconnected client
            print('client disconnected, killing process')
            p.terminate()

    return Response(generate(), mimetype='text/event-stream')


@app.route('/install')
def install():
    return process_response([sys.executable, '-m', 'pip', 'install', '-r', SCRIPT_DIR + '/requirements.txt'])


@app.route('/run/<script>')
def run(script):
    scripts = os.listdir(SCRIPT_DIR)
    if script + '.py' not in scripts:
        abort(404, 'Script not found')

    return process_response(['python', '-u', SCRIPT_DIR + '/' + script + '.py'])


if __name__ == '__main__':
    app.run()

application = app
