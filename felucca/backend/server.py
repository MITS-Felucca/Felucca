import json
import os
import base64
import sys
import time
import config
from datetime import datetime
from flask import abort
from flask import Flask
from flask import request
from flask import jsonify
from flask import Response
from threading import Thread
from time import sleep
from execution_manager import ExecutionManager
from job_manager import JobManager
from resource_manager import ResourceManager
from common.task import Task
from common.job import Job
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../tests/sample_output'))


app = Flask(__name__)
db_name = config.DATABASE_NAME
debug_page_string = ""


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/test/pharos", methods=['POST'])
def update_pharos():
    request_json = request.get_json()
    print(request.get_json())
    print("udpatepharos")
    return {"Status": "ok"}


@app.route("/pharos", methods=['POST'])
def update_kernel():
    """update backend Pharos tool from docker hub
    The form of the POST format: {Content: seipharos/pharos:latest}
    Test command: curl http://localhost:5000/pharos -X POST -d "Content=seipharos/pharos:latest"
                  curl http://localhost:5000/pharos -X POST -d "Content=ubuntu"
    """
    if ResourceManager(db_name).get_updating_kernel() is True:
        return {"Status": "Currently the Pharos toolset is updating. Try later please."}
    BASE_IMAGE = request.get_json()['Content']
    t = Thread(target =  thread_update_kernel,args = (BASE_IMAGE, ))
    t.start()
    return {"Status": "ok"}


def thread_update_kernel(BASE_IMAGE = "seipharos/pharos:latest"):
    JobManager().kill_all_jobs()
    ExecutionManager().update_kernel(BASE_IMAGE)


@app.route("/test_EM_running",methods=['GET'])
def test_EM_running():
    """this is used for testing new execution manager after reconstrction, it will start a thread to load the json and run the cmd

    Args:
    task_type (str): if task_type == "false", this method will load a json with simulated wrong cmd to run, otherwise it will load a correct cmd
    task_id (str): the result under this task_id
    Example test command: curl “http://0.0.0.0:5000/test_new_execution/true/toytest"
    To use this method, we should put the "input.json" and "input_wrong.json" at sample_output" folder in advance
    """
    
    t = Thread(target = thread_test_EM_running, args = ("true", ))
    t.start()
    t = Thread(target = thread_test_EM_running, args = ("false", ))
    t.start()
    return {"Status": "ok"}


def thread_test_EM_running(task_type):

    """this is the implementation for testing new execution manager

    """
    if task_type == "false":
        with open(os.path.join(os.path.dirname(__file__), '../../tests/sample_output/input_wrong.json'),'r') as f:
            json_data = json.load(f)
        job = Job.from_json(json_data)
        job.job_id = "thisisafalseinputcmdtaskjob6"
        task = job.tasks[0]
        task.task_id = "thisisafalseinputcmdtask"
    else:
        with open(os.path.join(os.path.dirname(__file__), '../../tests/sample_output/input.json'),'r') as f:
            json_data = json.load(f)
        job = Job.from_json(json_data)
        job.job_id = "thisisatrueinputcmd_job6"
        task = job.tasks[0]
        task.task_id = "thisisatrueinputcmd_task"

    file_dict = {}
    folder_path = os.path.join("/tmp/Felucca", f"{task.task_id}")

    if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    for input_flag, content in json_data["Tasks"][0]["Files"].items():
        filename = json_data["Tasks"][0]["Input_File_Args"][input_flag] #oo.exe
        file_path = os.path.join("/tmp/Felucca", f"{task.task_id}/{filename}")

        with open(file_path, "wb") as f:
            byte_stream = base64.b64decode(content.encode('utf-8'))
            f.write(byte_stream)
    #this is the simulation for RM changing the task.files from task.files = {"-f":exe_str } to task.files = {"-f": path }
        file_dict[filename] = file_path
        print(f"file_path: {file_path}")
    task.files = file_dict
    ExecutionManager().submit_task(task)


@app.route("/clean-all", methods=['GET'])
def clean_all():
    """Remove all jobs and tasks in database "test"
    Command: curl --request GET http://localhost:5000/clean-all
    """
    ResourceManager("test").remove_all_jobs_and_tasks()
    return {"Status": "ok"}


def submit_job_through_job_manager(job):
    JobManager().submit_job(job)


@app.route("/job", methods=['POST'])
def submit_job():
    """Test command: curl -H "Content-Type: application/json" --request POST -d @/vagrant/tests/sample_output/input.json http://localhost:5000/job"
    """
    if ResourceManager(db_name).get_updating_kernel() is True:
        return {"Status": "Currently the Pharos toolset is updating. Try later please."}

    request_json = request.get_json()
    # print(request.get_json())
    job = ResourceManager(db_name).save_new_job_and_tasks(request_json)
    thread = Thread(target=submit_job_through_job_manager, args=(job, ))
    thread.start()
    return {"Status": "ok"}


@app.route("/job-info/<id>/json", methods=['GET'])
def get_job(id):
    """Test command: curl --request GET http://localhost:5000/job-info/<id>/json

    Test steps:
        1. Modify line 14 & 15 of this file to use database "test"
        2. Run "curl --request GET http://localhost:5000/clean-all"
        3. Submit jobs through browser
        4. Run "curl --request GET http://localhost:5000/job-list/json" to get the list
        5. Run "curl --request GET http://localhost:5000/job-info/<id>/json" where the id is of the first job in the list
        6. Run "curl --request GET http://localhost:5000/clean-all" after use
        7. Remember to modify the name of the database
    """
    job_dict = ResourceManager(db_name).get_job_info(id)
    return job_dict


@app.route("/job-list/json", methods=['GET'])
def get_job_list():
    """Test command: curl --request GET http://localhost:5000/job-list/json
    """
    job_list = ResourceManager(db_name).get_job_list()
    print(JobManager().job_metadata)
    return {"Job_List": job_list}


@app.route("/kill-job/<job_id>", methods=['GET'])
def kill_job(job_id):
    JobManager().kill_job(job_id)
    return {"Status": "ok"}


@app.route("/kill-task/<task_id>", methods=['GET'])
def kill_task(task_id):
    ExecutionManager().kill_task(task_id)
    return {"Status": "ok"}


@app.route("/pharos/metadata", methods=['GET'])
def get_metadata():
    return ResourceManager(db_name).get_all_metadata()


@app.route("/intermediate-result/stdout", methods=['POST'])
def save_realtime_stdout():
    Thread(target=lambda task_id, stdout: ResourceManager(db_name).update_stdout(task_id, stdout),
           args=(request.form['task_id'], request.form['stdout'], )).start()
    return {"status": "ok"}


@app.route("/intermediate-result/stderr", methods=['POST'])
def save_realtime_stderr():
    Thread(target=lambda task_id, stderr: ResourceManager(db_name).update_stderr(task_id, stderr),
           args=(request.form['task_id'], request.form['stderr'], )).start()
    return {"status": "ok"}


@app.route("/result", methods=['POST'])
def get_result():
    status = request.form['status']
    ExecutionManager().save_result(request.form['task_id'],
                                   status)
    JobManager().finish_task(request.form['task_id'])
    return {'is_received': True}


@app.route("/task/<task_id>", methods=['GET'])
def get_task(task_id):
    command = ExecutionManager().get_command_line_input(task_id)
    return {'command_line_input': command}


@app.route("/task/<task_id>/output/<file_name>/json", methods=['GET'])
def get_task_file(task_id, file_name):
    print(task_id)
    file = ResourceManager(db_name).get_output_file(task_id,file_name)
    if file is None:
        abort(404)
    return {"Content": file}


@app.route("/task/<task_id>/stdout/json", methods=['GET'])
def get_stdout(task_id):
    print(task_id)
    stdout = ResourceManager(db_name).get_stdout(task_id)
    if stdout is None:
        abort(404)
    else:
        status_str = ResourceManager(db_name).get_status(task_id)
        return {
            "Status": status_str,
            "Content": stdout
        }


@app.route("/task/<task_id>/stderr/json", methods=['GET'])
def get_stderr(task_id):
    print(task_id)
    stderr = ResourceManager(db_name).get_stderr(task_id)
    if stderr is None:
        abort(404)
    else:
        status_str = ResourceManager(db_name).get_status(task_id)
        return {
            "Status": status_str,
            "Content": stderr
        }


@app.route("/tool-list/json", methods=["GET"])
def get_tool_list():
    tool_list = ResourceManager(db_name).get_all_tools()
    return {"Schemas": tool_list}


@app.route("/tool/<tool_id>/json", methods=["GET"])
def get_single_tool(tool_id):
    tool = ResourceManager(db_name).get_tool_by_id(tool_id)
    if tool is None:
        abort(404)
    else:
        return tool


@app.route("/tool", methods=["POST"])
def insert_new_tool():
    request_json = request.get_json()
    ResourceManager(db_name).insert_new_tool(request_json)
    return {"Status": "ok"}


@app.route("/tool/<tool_id>/delete", methods=["GET"])
def remove_tool(tool_id):
    ResourceManager(db_name).remove_tool_by_id(tool_id)
    return {"Status": "ok"}


@app.route("/tool/<tool_id>", methods=["POST"])
def update_tool(tool_id):
    request_json = request.get_json()
    ResourceManager(db_name).update_tool(tool_id, request_json)
    return {"Status": "ok"}


@app.after_request
def allow_cross_domain(response: Response):
    """Hook to set up response headers."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    return response


def setup_pharos_tools(app):
    # Remove the check for non-debug mode
    # It means "Only run when app has been loaded"
    # Flask will run it twice to enable the "reload" feature in debug mode
    is_initialized = ResourceManager(db_name).setup()
    if is_initialized == False:
        ResourceManager(db_name).initialize_pharos_tools()
        t = Thread(target =  thread_update_kernel)
        t.start()
    # if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    #     ResourceManager(db_name).initialize_pharos_tools()
    #     tool_list = ResourceManager(db_name).get_all_tools()
    #     print(len(tool_list))


setup_pharos_tools(app)
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=config.IS_DEBUG)
