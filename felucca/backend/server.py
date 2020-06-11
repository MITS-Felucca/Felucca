from flask import Flask
from flask import request
from flask import jsonify
from flask import Response

from time import sleep
from execution_manager import ExecutionManager
from job_manager import JobManager
from resource_manager import ResourceManager
from common.task import Task
from common.job import Job
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/test")
def test():
    now = datetime.now()
    task = Task("../../tests/sample_output/oo.exe", "meaningless",
                "ooanalyzer -j output.json -R results -F facts -f ../../tests/sample_output/oo.exe")
    dummy_job = Job("Test Job", "OOanalyer Job", now)
    dummy_job.tasks = [task]
    job_id, tasks_id = JobManager().submit_job(dummy_job)

    # task = Task("/vagrant/Felucca/tests/oo.exe", "meaningless", "ooanalyzer -j output.json -R results -f /vagrant/Felucca/tests/oo.exe")
    # task.task_id = '5ed166559fde8c0531988a64'
    # ExecutionManager().submit_task(task)
    sleep(20)
    job = ResourceManager().get_job_by_id(job_id)
    print(job.name)
    print(job.comments)
    print(job.created_time)
    # print(job.tasks)
    print(job.status)

    print("=======================")
    task = ResourceManager().get_tasks_by_job_id(job_id)[0]
    print(task.command_line_input)
    print(task.executable_file)
    print(task.status)
    print(task.stdout)
    print(task.stderr)
    print(task.output)
    print(task.log)

    print("=======================")
    task = ResourceManager().get_task_by_id(tasks_id[0])
    print(task.command_line_input)
    print(task.executable_file)
    print(task.status)
    print(task.stdout)
    print(task.stderr)
    print(task.output)
    print(task.log)
    return {"status": "ok"}


@app.route("/result", methods=['POST'])
def get_result():
    status = request.form['status']
    ExecutionManager().save_result(request.form['task_id'],
                                   status,
                                   request.form['stderr'],
                                   None if status == 'Error' else request.form['stdout'])
    JobManager().finish_task(request.form['task_id'])
    return {'is_received': True}


@app.route("/task/<task_id>", methods=['GET'])
def get_task(task_id):
    return {'command_line_input': ExecutionManager().get_command_line_input(task_id)}


@app.route("/debug/job-list")
def debug_get_job_list():
    return {
        "Job_List": [
            {
                "Comment": "Just for test0",
                "Created_Time": 1591826345.0,
                "Finished_Time": 0,
                "ID": "5ee157a95113f5b43b39a3ce",
                "Name": "Test_job0",
                "Status": "Failed",
                "Task_Number": 2,
                "Tasks": []
            },
            {
                "Comment": "Just for test1",
                "Created_Time": 1591826345.0,
                "Finished_Time": 0,
                "ID": "5ee157a95113f5b43b39a3d2",
                "Name": "Test_job1",
                "Status": "Pending",
                "Task_Number": 0,
                "Tasks": []
            },
            {
                "Comment": "Just for test2",
                "Created_Time": 1591826345.0,
                "Finished_Time": 0,
                "ID": "5ee157a95113f5b43b39a3d4",
                "Name": "Test_job2",
                "Status": "Pending",
                "Task_Number": 0,
                "Tasks": []
            }
        ]
    }


@app.route("/debug/job-info/<job_id>")
def debug_get_job_info(job_id):
    return {
        "Comment": "Just for test0",
        "Created_Time": 1591828405.0,
        "Finished_Time": 0,
        "ID": "5ee15fb507b312261cd65a2f",
        "Name": "Test_job0",
        "Status": "Failed",
        "Task_Number": 2,
        "Tasks": [
            {
                "Arguments": {
                    "-F": "facts",
                    "-R": "results",
                    "-f": "oo.exe",
                    "-j": "output.json"
                },
                "Finished_Time": 1591828405.0,
                "ID": "5ee15fb507b312261cd65a30",
                "Log": [
                    "facts",
                    "results"
                ],
                "Output": [
                    "output.json"
                ],
                "Status": "Successful",
                "Stderr": "sample stderr",
                "Stdout": "sample stdout"
            },
            {
                "Arguments": {
                    "-F": "facts",
                    "-R": "results",
                    "-f": "oo.exe",
                    "-j": "output.json"
                },
                "Finished_Time": 0,
                "ID": "5ee15fb507b312261cd65a31",
                "Log": [],
                "Output": [],
                "Status": "Failed",
                "Stderr": "",
                "Stdout": ""
            }
        ]
    }


@app.route("/debug/job", methods=[ "POST" ])
def debug_job_submission():
    print(request.get_json())
    return {"Status": "ok"}


@app.after_request
def allow_cross_domain(response: Response):
    """Hook to set up response headers."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
