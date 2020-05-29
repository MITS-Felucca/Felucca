import json
import os
import requests
import subprocess
from flask import Flask
from threading import Thread
from common.status import Status

SERVER_IP = '172.17.0.1'
SERVER_PORT = '5000'
app = Flask(__name__)


def task_execute():
    """Execute a task using its command line input.

    After the task is finished, it will send its output through HTTP post request.

    :return:
        Returned Nothing.
    """
    try:
        completed_process = subprocess.run(command_line_input, shell=True, capture_output=True)
    except Exception as e:
        requests.post('http://%s:%s/result' % (SERVER_IP, SERVER_PORT), data={'task_id': task_id,
                                                                              'status': Status.Error.name,
                                                                              'stderr': str(e)})
        return

    status = Status.Successful.name
    if completed_process.returncode != 0:
        status = Status.Failed.name
        
    requests.post('http://%s:%s/result' % (SERVER_IP, SERVER_PORT), data={'task_id': task_id,
                                                                          'status': status,
                                                                          'stderr': completed_process.stderr,
                                                                          'stdout': completed_process.stdout})


def get_command_line_input():
    """Get the command line from backend using task id.

    :return:
        string: The command line input.
    """

    try:
        r = requests.get('http://%s:%s/task/%s' % (SERVER_IP, SERVER_PORT, task_id))
    except requests.exceptions.RequestException as e:
        print(e)
        return

    if r.status_code != requests.codes.ok:
        print("GET request failed: %d" % r.status_code)
        return

    return json.loads(r.content)['command_line_input']


task_id = os.environ['TASK_ID']  # get task id
command_line_input = get_command_line_input()  # get command line input

task_executor = Thread(target=task_execute, args=())
task_executor.start()


@app.route("/task", methods=['GET'])
def get_task():
    """Return task information for debug use

    :return:
        dict: dict contains key task_id and command_line_input
    """
    return {'task_id': task_id, 'command_line_input': command_line_input}


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)