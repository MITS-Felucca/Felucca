import json
import os
from datetime import datetime
from flask import abort
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

app = Flask(__name__)
db_name = "test"
# db_name = "felucca"

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

@app.route("/test_new_execution")
def test_new_execution():
    """this is used for testing new execution manager after reconstrction

    Test command: curl “http://0.0.0.0:5000/test_new_execution", to use this, we should put the input.json at the "backend" folder in advance 
    """
    with open("input.json",'r') as f:
        json_data = json.load(f)
    job = Job.from_json(json_data)
    job.job_id = "this_is_a_test_job_id"
    task = job.tasks[0]
    task.task_id = "this_is_a_test_task_id2"
    

    file_dict = {}
    folder_path = os.path.join("/tmp/Felucca", f"{task.task_id}")

    if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    
    for filename, content in json_data["Tasks"][0]["Files"].items():
        file_path = os.path.join("/tmp/Felucca", f"{task.task_id}/{filename}")
        
        
        with open(file_path, "wb") as f:
            f.write(bytes.fromhex(content))
        file_dict[filename] = file_path
    task.files = file_dict
    ExecutionManager().submit_task(task)
           
    return ("test2 finished\n")

@app.route("/clean-all", methods=['GET'])
def clean_all():
    """Remove all jobs and tasks in database "test"
    Command: curl --request GET http://localhost:5000/clean-all
    """
    ResourceManager("test").remove_all_jobs_and_tasks()
    return {"status": "ok"}

@app.route("/job", methods=['POST'])
def submit_job():
    """Test command: curl -H "Content-Type: application/json" --request POST -d @/vagrant/tests/sample_output/input.json http://localhost:5000/job"
    """
    request_json = request.get_json()
    print(request.get_json())
    job = ResourceManager(db_name).save_new_job_and_tasks(request_json)
    JobManager().submit_job(job)
    return {"status": "ok"}


@app.route("/job-info/<id>/json", methods=['GET'])
def get_job(id):
    """Test command: curl --request GET http://localhost:5000/job-info/<id>/json

    Test steps:
        1. Modify line 14 & 15 of this file to use database "test"
        2. Run "curl --request GET http://localhost:5000/clean-all"
        3. Run "curl --request GET http://localhost:5000/generate-sample"
        4. Run "curl --request GET http://localhost:5000/job-list/json" to get the list
        5. Run "curl --request GET http://localhost:5000/job-info/<id>/json" where the id is of the first job in the list
        6. Run "curl --request GET http://localhost:5000/clean-all" after use
        7. Remember to modify the name of the database
    """
    job_dict = ResourceManager(db_name).get_job_info(id)
    print(job_dict)
    return job_dict

@app.route("/job-list/json", methods=['GET'])
def get_job_list():
    """Test command: curl --request GET http://localhost:5000/job-list/json
    """
    job_list = ResourceManager(db_name).get_job_list()
    return {"Job_List": job_list}

@app.route("/generate-sample", methods=['GET'])
def generate_samples():
    """Generate three jobs with two tasks in database "test"
    Command: curl --request GET http://localhost:5000/generate-sample
    """
    ResourceManager("test").generate_sample_jobs()
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


@app.route("/task/<task_id>/<file_type>/<file_name>/json", methods=['GET'])
def get_task_file(task_id, file_type, file_name):
    print(task_id)
    if file_type == "output":
        file = ResourceManager(db_name).get_output_file(task_id, file_name)
        if file is None:
            abort(404)
        return {"Content": file}
    elif file_type == "log":
        file = ResourceManager(db_name).get_log_file(task_id, file_name)
        if file is None:
            abort(404)
        return {"Content": file}
    else:
        abort(404)


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
