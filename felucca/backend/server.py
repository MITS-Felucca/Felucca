from flask import Flask
from flask import request
from time import sleep
from execution_manager import ExecutionManager
from job_manager import JobManager
from resource_manager import ResourceManager
from common.task import Task
from common.job import Job
from datetime import datetime
import json,os
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


@app.route("/job", methods=['POST'])
def submit_job():
    """Test command: curl -H "Content-Type: application/json" --request POST -d @/vagrant/tests/sample_output/input.json http://localhost:5000/job"
    """
    request_json = request.get_json()
    job = ResourceManager().save_new_job_and_tasks(request_json)
    # TODO: submit job through JobManager
    # JobManager().submit_job(job)
    return {"status": "ok"}


@app.route("/job/<id>", methods=['GET'])
def get_job(id):
    # TODO: return job info
    print(id)
    return {"message": f"You are asking for job info of id {id}"}

@app.route("/job-list", methods=['GET'])
def get_job_list():
    # TODO: Return a list of jobs in json
    pass

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
