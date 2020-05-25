from flask import Flask
from flask import request
app = Flask(__name__)


@app.route("/result", methods=['POST'])
def print_result():
    print(request.form)
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)