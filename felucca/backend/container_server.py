import json
import os
import requests
import subprocess
import time
from flask import Flask
from threading import Thread
from common.status import Status

SERVER_IP = '172.17.0.1'
SERVER_PORT = '5000'
app = Flask(__name__)

update_period = 0.5 # In seconds
stdout_file_name = 'stdout.log'
stderr_file_name = 'stderr.log'

def read_stderr(process):
    """Continuously read the stderr from the running process,
    then store them in the log files.

    Args:
        process (Return value of subprocess.Popen): The running process
    """
    stderr = ""
    last_time = time.time()

    # Read stderr continuously
    while process.poll() is None:
        err_line = process.stderr.readline().decode('utf-8')
        stderr += err_line
        current_time = time.time()
        if stderr != "" and current_time - last_time > update_period:
            last_time = current_time
            # Send the new stderr to the server
            requests.post('http://%s:%s/intermediate-result/stderr' % (SERVER_IP, SERVER_PORT),
                          data={'task_id': task_id,
                                'stderr': stderr})
            stderr = ""

    # Read all stderr left after the process finished
    for line in iter(lambda: process.stderr.readline(), b''):
        err_line = line.decode('utf-8')
        stderr += err_line

    if stderr != "":
        requests.post('http://%s:%s/intermediate-result/stderr' % (SERVER_IP, SERVER_PORT),
                      data={'task_id': task_id,
                            'stderr': stderr})

def task_execute():
    """Execute a task using its command line input.

    After the task is finished, it will send its output through HTTP post request.

    :return:
        Returned Nothing.
    """
    try:
        process = subprocess.Popen(command_line_input, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        thread = Thread(target=read_stderr, args=(process, ))

        stdout = ""
        last_time = time.time()
        thread.start()

        # Read stdout continuously
        while process.poll() is None:
            out_line = process.stdout.readline().decode('utf-8')
            stdout += out_line
            current_time = time.time()
            if stdout != "" and current_time - last_time > update_period:
                last_time = current_time
                # Send the new stdout to the server
                requests.post('http://%s:%s/intermediate-result/stdout' % (SERVER_IP, SERVER_PORT),
                              data={'task_id': task_id,
                                    'stdout': stdout})
                stdout = ""

        # Read all stdout left after the process finished
        for line in iter(lambda: process.stdout.readline(), b''):
            out_line = line.decode('utf-8')
            stdout += out_line

        if stdout != "":
            requests.post('http://%s:%s/intermediate-result/stdout' % (SERVER_IP, SERVER_PORT),
                          data={'task_id': task_id,
                                'stdout': stdout})

        thread.join()

        status = Status.Successful.name
        if process.returncode != 0:
            status = Status.Failed.name

        requests.post('http://%s:%s/result' % (SERVER_IP, SERVER_PORT), data={'task_id': task_id,
                                                                          'status': status,
                                                                          'stdout': "",
                                                                          'stderr': ""})
    except Exception as e:
        requests.post('http://%s:%s/result' % (SERVER_IP, SERVER_PORT), data={'task_id': task_id,
                                                                              'status': Status.Error.name,
                                                                              'stderr': str(e)})
    return

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