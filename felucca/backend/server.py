from flask import Flask
from flask import request
from execution_manager import ExecutionManager

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/result", methods=['POST'])
def get_result():
    status = request.form['status']
    ExecutionManager().save_result(request.form['task_id'],
                                   status,
                                   request.form['stderr'],
                                   None if status == 'Error' else request.form['stdout'])
    return {'is_received': True}

@app.route("/task/<task_id>", method=['GET'])
def get_task(task_id):
    return {'command_line_input': ExecutionManager().get_command_line_input(task_id)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)