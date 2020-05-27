from flask import Flask
from flask import request
app = Flask(__name__)


@app.route("/task/<task_id>", methods=['GET'])
def get_task(task_id):
    if task_id == '1':
        return {'command_line_input': 'ooanalyzer -j output.json -F facts -R results -f /test/oo.exe'}
    elif task_id == '2':
        return {'command_line_input': 'ooanalyzer -j output.json -F facts -R results -f /backend/oo.exe'}
    elif task_id == '3':
        return {'command_line_input': 1}
    return 'task_id not found', 404


@app.route("/result", methods=['POST'])
def print_result():
    print(request.form)
    return 'OK', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)