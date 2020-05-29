from flask import Flask
from flask import request
from execution_manager import ExecutionManager
from common.task import Task

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/test")
def test():
    task = Task("/vagrant/Felucca/tests/oo.exe", "meaningless", "ooanalyzer -j output.json -R results -f /vagrant/Felucca/tests/oo.exe")
    task.task_id = 2333
    ExecutionManager().submit_task(task)

@app.route("/result", methods=['POST'])
def get_result():
    status = request.form['status']
    ExecutionManager().save_result(int(request.form['task_id']),
                                   status,
                                   request.form['stderr'],
                                   None if status == 'Error' else request.form['stdout'])
    return {'is_received': True}

@app.route("/task/<task_id>", methods=['GET'])
def get_task(task_id):
    return {'command_line_input': ExecutionManager().get_command_line_input(int(task_id))}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
