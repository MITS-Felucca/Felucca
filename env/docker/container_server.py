from flask import Flask
from flask import request
import requests
import subprocess
from threading import Thread
app = Flask(__name__)


@app.route("/task", methods=['POST'])
def submit_task():
    task_executor = Thread(target=task_execute, args=(request.form['task_id'],
                                                      request.form['command_line_input']))
    task_executor.start()
    return {'is_received': True}


def task_execute(task_id, command_line_input):

    try:
        completed_process = subprocess.run(command_line_input, shell=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(e)
        requests.post('http://172.17.0.1:5000/result', data={'task_id': task_id,
                                                             'status': 'Error'})
        return

    status = 'Success'
    if completed_process.returncode != 0:
        status = 'Failure'

    requests.post('http://172.17.0.1:5000/result', data={'task_id': task_id,
                                                         'status': status,
                                                         'stderr': completed_process.stderr,
                                                         'stdout': completed_process.stdout})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)