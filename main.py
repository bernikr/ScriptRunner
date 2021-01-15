import os
import subprocess
import threading
from time import time, sleep

from flask import Flask, Response, abort

app = Flask(__name__)

SCRIPT_DIR = os.getenv('SCRIPT_DIR', os.path.dirname(os.path.realpath(__file__))+'/scripts')


@app.route('/')
def index():
    return 'Hello World'


@app.route('/run/<script>')
def run(script):
    scripts = os.listdir(SCRIPT_DIR)
    if script + '.py' not in scripts:
        abort(404, 'Script not found')

    p = subprocess.Popen(['python', SCRIPT_DIR + '/' + script + '.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    timeout = [time() + 60]

    def stop():
        while True:
            if time() > timeout[0]:
                p.kill()
                break
            sleep(timeout[0] - time())

    threading.Thread(target=stop).start()

    def generate():
        while True:
            timeout[0] = time() + 60
            r = p.stdout.readline()
            if len(r) == 0:
                break
            yield r

    return Response(generate(), mimetype='text/plain', content_type='text/event-stream')


if __name__ == '__main__':
    app.run()
