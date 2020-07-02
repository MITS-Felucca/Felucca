import json
import os
import base64
import sys
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
@app.route("/update_kernel", methods=['GET'])
def test_update_kernel():
    """update backend Phraos tool from docker hub
    
    Test command: curl http://localhost:5000/update_kernel
    """
    ExecutionManager().update_kernel()
    return {"status": "ok"}
    
@app.route("/test_new_execution/<task_type>/<task_id>",methods=['GET','POST'])
def test_new_execution(task_type, task_id):
    """this is used for testing new execution manager after reconstrction, it will start a thread to load the json and run the cmd
    
    Args:
    task_type (str): if task_type == "false", this method will load a json with simulated wrong cmd to run, otherwise it will load a correct cmd
    task_id (str): the result under this task_id
    Example test command: curl “http://0.0.0.0:5000/test_new_execution/true/toytest"
    To use this method, we should put the "input.json" and "input_wrong.json" at sample_output" folder in advance
    """

    t = Thread(target = thread_test_new_execution, args = (task_type, task_id, ))
    t.start()

    return ("start testing: task_type:{task_type} task_id:{task_id}\n")

@app.route("/clean-all", methods=['GET'])
def clean_all():
    """Remove all jobs and tasks in database "test"
    Command: curl --request GET http://localhost:5000/clean-all
    """
    ResourceManager("test").remove_all_jobs_and_tasks()
    return {"status": "ok"}

def submit_job_through_job_manager(job):
    JobManager().submit_job(job)

@app.route("/job", methods=['POST'])
def submit_job():
    """Test command: curl -H "Content-Type: application/json" --request POST -d @/vagrant/tests/sample_output/input.json http://localhost:5000/job"
    """
    request_json = request.get_json()
    print(request.get_json())
    job = ResourceManager(db_name).save_new_job_and_tasks(request_json)
    thread = Thread(target=submit_job_through_job_manager, args=(job, ))
    thread.start()
    # JobManager().submit_job(job)
    return {"status": "ok"}


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
    return {"Job_List": job_list}

@app.route("/kill-job/<job_id>", methods=['GET'])
def kill_job(job_id):
    JobManager().kill_job(job_id)
    return {"status": "ok"}

@app.route("/kill-task/<task_id>", methods=['GET'])
def kill_task(task_id):
    ExecutionManager().kill_task(task_id)
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
        return {"Content": stdout}

@app.route("/task/<task_id>/stderr/json", methods=['GET'])
def get_stderr(task_id):
    print(task_id)
    stderr = ResourceManager(db_name).get_stderr(task_id)
    if stderr is None:
        abort(404)
    else:
        return {"Content": stderr}

@app.route("/tool-list/json", methods=["GET"])
def get_tool_list():
    tool_list = ResourceManager(db_name).get_all_tools()
    return {"Schemas": tool_list}


@app.route("/debug/job-list/json")
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


@app.route("/debug/job-info/<job_id>/json")
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
                "Output": [
                    "output.json",
                    "facts",
                    "results"
                ],
                "Status": "Successful",
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
            }
        ]
    }


@app.route("/debug/job", methods=[ "POST" ])
def debug_job_submission():
    print(request.get_json())
    return {"Status": "ok"}


@app.route("/debug/tool-list/json", methods=[ "GET" ])
def debug_get_schema():
    return {"Schemas": [{
        "Tool_Name": "OOAnalyzer",
        "Program_Name": "ooanalyzer",
        "Is_Pharos": True,
        "Classes": [
            {
                "Name": "OOAnalyzer v1.0 options:",
                "Arguments": [
                    {
                        "Full_Name": "--json",
                        "Abbreviation": "-j",
                        "Description": "specify the JSON output file",
                        "Is_Required": False,
                        "Default_Value": "output.json",
                        "Type": "Output_File_Args"
                    },
                    {
                        "Full_Name": "--new-method",
                        "Abbreviation": "-n",
                        "Description": "function at address is a new() method",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--delete-method",
                        "Abbreviation": "",
                        "Description": "function at address is a delete() method",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--no-guessing",
                        "Abbreviation": "",
                        "Description": "do not perform hypothetical reasoning. never use except for experiments",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--ignore-rtti",
                        "Abbreviation": "",
                        "Description": "ignore RTTI metadata if present",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--prolog-facts",
                        "Abbreviation": "-F",
                        "Description": "specify the Prolog facts output file",
                        "Is_Required": False,
                        "Default_Value": "fact",
                        "Type": "Output_File_Args"
                    },
                    {
                        "Full_Name": "--prolog-results",
                        "Abbreviation": "-R",
                        "Description": "specify the Prolog results output file",
                        "Is_Required": False,
                        "Default_Value": "result",
                        "Type": "Output_File_Args"
                    },
                    {
                        "Full_Name": "--prolog-debug",
                        "Abbreviation": "-d",
                        "Description": "enable debugging in the Prolog analysis",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--prolog-trace",
                        "Abbreviation": "",
                        "Description": "enable output of prolog commands, queries, and results",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--prolog-low-level-tracing",
                        "Abbreviation": "",
                        "Description": "enable prolog's low-level tracing",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    }
                ]
            },
            {
                "Name": "CERT/Pharos options:",
                "Arguments": [
                    {
                        "Full_Name": "--help",
                        "Abbreviation": "-h",
                        "Description": "display help",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--verbose",
                        "Abbreviation": "-v",
                        "Description": "[=arg(=3)] enable verbose logging (1-14, default 3)",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--timing",
                        "Abbreviation": "",
                        "Description": "Include duration field in log messages",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--batch",
                        "Abbreviation": "-b",
                        "Description": "suppress colors, progress bars, etc.",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--allow-64bit",
                        "Abbreviation": "",
                        "Description": "allow analysis of 64-bit executables",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--include-func",
                        "Abbreviation": "-i",
                        "Description": "limit analysis to a specific function",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--exclude-func",
                        "Abbreviation": "-e",
                        "Description": "exclude analysis of a specific function",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--config",
                        "Abbreviation": "-C",
                        "Description": "pharos configuration file (can be specified multiple times)",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_File_Args"
                    },
                    {
                        "Full_Name": "--dump-config",
                        "Abbreviation": "",
                        "Description": "display current active config parameters",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--no-user-file",
                        "Abbreviation": "",
                        "Description": "don't load the user's configuration file",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--no-site-file",
                        "Abbreviation": "",
                        "Description": "don't load the site's configuration file",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--apidb",
                        "Abbreviation": "",
                        "Description": "path to sqlite or JSON file containing API and type information",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_File_Args"
                    },
                    {
                        "Full_Name": "--library",
                        "Abbreviation": "-l",
                        "Description": "specify the path to the pharos library directory",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--timeout",
                        "Abbreviation": "",
                        "Description": "time limit (sec) for the entire analysis",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--per-function-timeout",
                        "Abbreviation": "",
                        "Description": "CPU limit (sec) per function",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--partitioner-timeout",
                        "Abbreviation": "",
                        "Description": "time limit (sec) for the partitioner",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--maximum-memory",
                        "Abbreviation": "",
                        "Description": "maximum memory (Mib) for the entire anlaysis",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--per-function-maximum-memory",
                        "Abbreviation": "",
                        "Description": "maximum memory (Mib) per function",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--maximum-instructions-per-block",
                        "Abbreviation": "",
                        "Description": "limit the number of instructions per basic block",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--maximum-iterations-per-function",
                        "Abbreviation": "",
                        "Description": "limit the number of CFG iterations per function",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--maximum-nodes-per-condition",
                        "Abbreviation": "",
                        "Description": "limit the number of tree nodes per ITE condition",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--threads",
                        "Abbreviation": "",
                        "Description": "[=arg(=1)] Number of threads to use, if this program uses threads.  A value of zero means to use all available processors. A negative value means to use that many less than the number of available processors.",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--file",
                        "Abbreviation": "-f",
                        "Description": "executable to be analyzed",
                        "Is_Required": True,
                        "Default_Value": "",
                        "Type": "Input_File_Args"
                    }
                ]
            },
            {
                "Name": "ROSE/Partitioner options:",
                "Arguments": [
                    {
                        "Full_Name": "--partitioner",
                        "Abbreviation": "",
                        "Description": "specify the function parititioner",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--serialize",
                        "Abbreviation": "",
                        "Description": "file which caches function partitioning information",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_File_Args"
                    },
                    {
                        "Full_Name": "--ignore-serialize-version",
                        "Abbreviation": "",
                        "Description": "reject version mismatch errors when reading a serialized file",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--no-semantics",
                        "Abbreviation": "",
                        "Description": "disable semantic analysis during parititioning",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--pdebug",
                        "Abbreviation": "",
                        "Description": "enable partitioner debugging",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--no-executable-entry",
                        "Abbreviation": "",
                        "Description": "do not mark the entry point segment as executable",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--mark-executable",
                        "Abbreviation": "",
                        "Description": "mark all segments as executable during partitioning",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--log",
                        "Abbreviation": "",
                        "Description": "log facility control string",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Text_Args"
                    },
                    {
                        "Full_Name": "--stockpart",
                        "Abbreviation": "",
                        "Description": "deprecated, use --parititioner=rose",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    },
                    {
                        "Full_Name": "--rose-version",
                        "Abbreviation": "",
                        "Description": "output ROSE version information and exit immediately",
                        "Is_Required": False,
                        "Default_Value": "",
                        "Type": "Input_Flag_Args"
                    }
                ]
            }]
        },
        {
            "Tool_Name": "ApiAnalyzer",
            "Program_Name": "apianalyzer",
            "Is_Pharos": True,
            "Classes": [
                {
                    "Name": "ApiAnalyzer v2.0.07 options:",
                    "Arguments": [
                        {
                            "Full_Name": "--sig_file",
                            "Abbreviation": "-S",
                            "Description": "Specify the API signature file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--graphviz",
                            "Abbreviation": "-G",
                            "Description": "Specify the graphviz output file (for troubleshooting)",
                            "Is_Required": False,
                            "Default_Value": "graphviz",
                            "Type": "Output_File_Args"
                        },
                        {
                            "Full_Name": "--path",
                            "Abbreviation": "-P",
                            "Description": "Set the search path output level (nopath, sigpath, fullpath)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--format",
                            "Abbreviation": "-F",
                            "Description": "Set output format: json or text",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--out_file",
                            "Abbreviation": "-O",
                            "Description": "Set output file",
                            "Is_Required": False,
                            "Default_Value": "output",
                            "Type": "Output_File_Args"
                        },
                        {
                            "Full_Name": "--category",
                            "Abbreviation": "-C",
                            "Description": "Select signature categories for which to search",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        }
                    ]
                },
                {
                    "Name": "CERT/Pharos options:",
                    "Arguments": [
                        {
                            "Full_Name": "--help",
                            "Abbreviation": "-h",
                            "Description": "display help",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--verbose",
                            "Abbreviation": "-v",
                            "Description": "[=arg(=3)] enable verbose logging (1-14, default 3)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timing",
                            "Abbreviation": "",
                            "Description": "Include duration field in log messages",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--batch",
                            "Abbreviation": "-b",
                            "Description": "suppress colors, progress bars, etc.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--allow-64bit",
                            "Abbreviation": "",
                            "Description": "allow analysis of 64-bit executables",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--include-func",
                            "Abbreviation": "-i",
                            "Description": "limit analysis to a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--exclude-func",
                            "Abbreviation": "-e",
                            "Description": "exclude analysis of a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--config",
                            "Abbreviation": "-C",
                            "Description": "pharos configuration file (can be specified multiple times)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--dump-config",
                            "Abbreviation": "",
                            "Description": "display current active config parameters",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-user-file",
                            "Abbreviation": "",
                            "Description": "don't load the user's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-site-file",
                            "Abbreviation": "",
                            "Description": "don't load the site's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--apidb",
                            "Abbreviation": "",
                            "Description": "path to sqlite or JSON file containing API and type information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--library",
                            "Abbreviation": "-l",
                            "Description": "specify the path to the pharos library directory",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the entire analysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-timeout",
                            "Abbreviation": "",
                            "Description": "CPU limit (sec) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--partitioner-timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the partitioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) for the entire anlaysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-instructions-per-block",
                            "Abbreviation": "",
                            "Description": "limit the number of instructions per basic block",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-iterations-per-function",
                            "Abbreviation": "",
                            "Description": "limit the number of CFG iterations per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-nodes-per-condition",
                            "Abbreviation": "",
                            "Description": "limit the number of tree nodes per ITE condition",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--threads",
                            "Abbreviation": "",
                            "Description": "[=arg(=1)] Number of threads to use, if this program uses threads.  A value of zero means to use all available processors. A negative value means to use that many less than the number of available processors.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--file",
                            "Abbreviation": "-f",
                            "Description": "executable to be analyzed",
                            "Is_Required": True,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        }
                    ]
                },
                {
                    "Name": "ROSE/Partitioner options:",
                    "Arguments": [
                        {
                            "Full_Name": "--partitioner",
                            "Abbreviation": "",
                            "Description": "specify the function parititioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--serialize",
                            "Abbreviation": "",
                            "Description": "file which caches function partitioning information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--ignore-serialize-version",
                            "Abbreviation": "",
                            "Description": "reject version mismatch errors when reading a serialized file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-semantics",
                            "Abbreviation": "",
                            "Description": "disable semantic analysis during parititioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--pdebug",
                            "Abbreviation": "",
                            "Description": "enable partitioner debugging",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-executable-entry",
                            "Abbreviation": "",
                            "Description": "do not mark the entry point segment as executable",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--mark-executable",
                            "Abbreviation": "",
                            "Description": "mark all segments as executable during partitioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--log",
                            "Abbreviation": "",
                            "Description": "log facility control string",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--stockpart",
                            "Abbreviation": "",
                            "Description": "deprecated, use --parititioner=rose",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--rose-version",
                            "Abbreviation": "",
                            "Description": "output ROSE version information and exit immediately",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        }
                    ]
                }
            ]
        },
        {
            "Tool_Name": "APILookup",
            "Program_Name": "apilookup",
            "Is_Pharos": True,
            "Classes": [
                {
                    "Name": "APILookup Options:",
                    "Arguments": [
                        {
                            "Full_Name": "--json",
                            "Abbreviation": "-j",
                            "Description": "[=FILENAME(=-)] Ouput JSON to given file.  Default is to stdout (-).",
                            "Is_Required": False,
                            "Default_Value": "output",
                            "Type": "Output_File_Args"
                        },
                        {
                            "Full_Name": "--pretty-json",
                            "Abbreviation": "-p",
                            "Description": "[=arg(=4)] Pretty-print json.  Argument is the indent width",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--regexp",
                            "Abbreviation": "-r",
                            "Description": "Treat symbols as regular expressions",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--case-insensitive-regexp",
                            "Abbreviation": "-c",
                            "Description": "Treat symbols as case-insensitive regular expressions",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--symbols",
                            "Abbreviation": "-s",
                            "Description": "Symbols to be queried",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        }
                    ]
                },
                {
                    "Name": "CERT/Pharos options:",
                    "Arguments": [
                        {
                            "Full_Name": "--help",
                            "Abbreviation": "-h",
                            "Description": "display help",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--verbose",
                            "Abbreviation": "-v",
                            "Description": "[=arg(=3)] enable verbose logging (1-14, default 3)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timing",
                            "Abbreviation": "",
                            "Description": "Include duration field in log messages",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--batch",
                            "Abbreviation": "-b",
                            "Description": "suppress colors, progress bars, etc.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--allow-64bit",
                            "Abbreviation": "",
                            "Description": "allow analysis of 64-bit executables",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--include-func",
                            "Abbreviation": "-i",
                            "Description": "limit analysis to a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--exclude-func",
                            "Abbreviation": "-e",
                            "Description": "exclude analysis of a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--config",
                            "Abbreviation": "-C",
                            "Description": "pharos configuration file (can be specified multiple times)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--dump-config",
                            "Abbreviation": "",
                            "Description": "display current active config parameters",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-user-file",
                            "Abbreviation": "",
                            "Description": "don't load the user's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-site-file",
                            "Abbreviation": "",
                            "Description": "don't load the site's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--apidb",
                            "Abbreviation": "",
                            "Description": "path to sqlite or JSON file containing API and type information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--library",
                            "Abbreviation": "-l",
                            "Description": "specify the path to the pharos library directory",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the entire analysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-timeout",
                            "Abbreviation": "",
                            "Description": "CPU limit (sec) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--partitioner-timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the partitioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) for the entire anlaysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-instructions-per-block",
                            "Abbreviation": "",
                            "Description": "limit the number of instructions per basic block",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-iterations-per-function",
                            "Abbreviation": "",
                            "Description": "limit the number of CFG iterations per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-nodes-per-condition",
                            "Abbreviation": "",
                            "Description": "limit the number of tree nodes per ITE condition",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--threads",
                            "Abbreviation": "",
                            "Description": "[=arg(=1)] Number of threads to use, if this program uses threads.  A value of zero means to use all available processors. A negative value means to use that many less than the number of available processors.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--file",
                            "Abbreviation": "-f",
                            "Description": "executable to be analyzed",
                            "Is_Required": True,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        }
                    ]
                },
                {
                    "Name": "ROSE/Partitioner options:",
                    "Arguments": [
                        {
                            "Full_Name": "--partitioner",
                            "Abbreviation": "",
                            "Description": "specify the function parititioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--serialize",
                            "Abbreviation": "",
                            "Description": "file which caches function partitioning information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--ignore-serialize-version",
                            "Abbreviation": "",
                            "Description": "reject version mismatch errors when reading a serialized file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-semantics",
                            "Abbreviation": "",
                            "Description": "disable semantic analysis during parititioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--pdebug",
                            "Abbreviation": "",
                            "Description": "enable partitioner debugging",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-executable-entry",
                            "Abbreviation": "",
                            "Description": "do not mark the entry point segment as executable",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--mark-executable",
                            "Abbreviation": "",
                            "Description": "mark all segments as executable during partitioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--log",
                            "Abbreviation": "",
                            "Description": "log facility control string",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--stockpart",
                            "Abbreviation": "",
                            "Description": "deprecated, use --parititioner=rose",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--rose-version",
                            "Abbreviation": "",
                            "Description": "output ROSE version information and exit immediately",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        }
                    ]
                }
            ]
        },
        {
            "Tool_Name": "CallAnalyzer",
            "Program_Name": "callanalyzer",
            "Is_Pharos": True,
            "Classes": [
                {
                    "Name": "callanalyzer 0.8 Options:",
                    "Arguments": [
                        {
                            "Full_Name": "--allow-unknown",
                            "Abbreviation": "",
                            "Description": "Output call information even when there is no useful parameter information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--show-symbolic",
                            "Abbreviation": "",
                            "Description": "Output symbolic values for <abstr> values",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--json",
                            "Abbreviation": "-j",
                            "Description": "Output json representation to given file ('-' for stdout)",
                            "Is_Required": False,
                            "Default_Value": "output",
                            "Type": "Output_File_Args"
                        },
                        {
                            "Full_Name": "--pretty-json",
                            "Abbreviation": "-p",
                            "Description": "[=arg(=4)] Pretty-print json.  Argument is the indent width",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--calls",
                            "Abbreviation": "",
                            "Description": "File containing a list of calls to output information about",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        }
                    ]
                },
                {
                    "Name": "CERT/Pharos options:",
                    "Arguments": [
                        {
                            "Full_Name": "--help",
                            "Abbreviation": "-h",
                            "Description": "display help",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--verbose",
                            "Abbreviation": "-v",
                            "Description": "[=arg(=3)] enable verbose logging (1-14, default 3)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timing",
                            "Abbreviation": "",
                            "Description": "Include duration field in log messages",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--batch",
                            "Abbreviation": "-b",
                            "Description": "suppress colors, progress bars, etc.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--allow-64bit",
                            "Abbreviation": "",
                            "Description": "allow analysis of 64-bit executables",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--include-func",
                            "Abbreviation": "-i",
                            "Description": "limit analysis to a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--exclude-func",
                            "Abbreviation": "-e",
                            "Description": "exclude analysis of a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--config",
                            "Abbreviation": "-C",
                            "Description": "pharos configuration file (can be specified multiple times)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--dump-config",
                            "Abbreviation": "",
                            "Description": "display current active config parameters",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-user-file",
                            "Abbreviation": "",
                            "Description": "don't load the user's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-site-file",
                            "Abbreviation": "",
                            "Description": "don't load the site's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--apidb",
                            "Abbreviation": "",
                            "Description": "path to sqlite or JSON file containing API and type information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--library",
                            "Abbreviation": "-l",
                            "Description": "specify the path to the pharos library directory",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the entire analysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-timeout",
                            "Abbreviation": "",
                            "Description": "CPU limit (sec) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--partitioner-timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the partitioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) for the entire anlaysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-instructions-per-block",
                            "Abbreviation": "",
                            "Description": "limit the number of instructions per basic block",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-iterations-per-function",
                            "Abbreviation": "",
                            "Description": "limit the number of CFG iterations per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-nodes-per-condition",
                            "Abbreviation": "",
                            "Description": "limit the number of tree nodes per ITE condition",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--threads",
                            "Abbreviation": "",
                            "Description": "[=arg(=1)] Number of threads to use, if this program uses threads.  A value of zero means to use all available processors. A negative value means to use that many less than the number of available processors.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--file",
                            "Abbreviation": "-f",
                            "Description": "executable to be analyzed",
                            "Is_Required": True,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        }
                    ]
                },
                {
                    "Name": "ROSE/Partitioner options:",
                    "Arguments": [
                        {
                            "Full_Name": "--partitioner",
                            "Abbreviation": "",
                            "Description": "specify the function parititioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--serialize",
                            "Abbreviation": "",
                            "Description": "file which caches function partitioning information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--ignore-serialize-version",
                            "Abbreviation": "",
                            "Description": "reject version mismatch errors when reading a serialized file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-semantics",
                            "Abbreviation": "",
                            "Description": "disable semantic analysis during parititioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--pdebug",
                            "Abbreviation": "",
                            "Description": "enable partitioner debugging",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-executable-entry",
                            "Abbreviation": "",
                            "Description": "do not mark the entry point segment as executable",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--mark-executable",
                            "Abbreviation": "",
                            "Description": "mark all segments as executable during partitioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--log",
                            "Abbreviation": "",
                            "Description": "log facility control string",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--stockpart",
                            "Abbreviation": "",
                            "Description": "deprecated, use --parititioner=rose",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--rose-version",
                            "Abbreviation": "",
                            "Description": "output ROSE version information and exit immediately",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        }
                    ]
                }
            ]
        },
        {
            "Tool_Name": "DumpMASM",
            "Program_Name": "dumpmasm",
            "Is_Pharos": True,
            "Classes": [
                {
                    "Name": "Dump MASM v0.02 options:",
                    "Arguments": [
                        {
                            "Full_Name": "--hex-bytes",
                            "Abbreviation": "-h",
                            "Description": "number of hex bytes to show per instruction",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--basic-block-lines",
                            "Abbreviation": "-l",
                            "Description": "split basic blocks with lines",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--format",
                            "Abbreviation": "",
                            "Description": "write output in specified format",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--reasons",
                            "Abbreviation": "-r",
                            "Description": "split basic blocks with lines",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        }
                    ]
                },
                {
                    "Name": "CERT/Pharos options:",
                    "Arguments": [
                        {
                            "Full_Name": "--help",
                            "Abbreviation": "-h",
                            "Description": "display help",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--verbose",
                            "Abbreviation": "-v",
                            "Description": "[=arg(=3)] enable verbose logging (1-14, default 3)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timing",
                            "Abbreviation": "",
                            "Description": "Include duration field in log messages",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--batch",
                            "Abbreviation": "-b",
                            "Description": "suppress colors, progress bars, etc.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--allow-64bit",
                            "Abbreviation": "",
                            "Description": "allow analysis of 64-bit executables",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--include-func",
                            "Abbreviation": "-i",
                            "Description": "limit analysis to a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--exclude-func",
                            "Abbreviation": "-e",
                            "Description": "exclude analysis of a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--config",
                            "Abbreviation": "-C",
                            "Description": "pharos configuration file (can be specified multiple times)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--dump-config",
                            "Abbreviation": "",
                            "Description": "display current active config parameters",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-user-file",
                            "Abbreviation": "",
                            "Description": "don't load the user's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-site-file",
                            "Abbreviation": "",
                            "Description": "don't load the site's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--apidb",
                            "Abbreviation": "",
                            "Description": "path to sqlite or JSON file containing API and type information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--library",
                            "Abbreviation": "-l",
                            "Description": "specify the path to the pharos library directory",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the entire analysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-timeout",
                            "Abbreviation": "",
                            "Description": "CPU limit (sec) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--partitioner-timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the partitioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) for the entire anlaysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-instructions-per-block",
                            "Abbreviation": "",
                            "Description": "limit the number of instructions per basic block",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-iterations-per-function",
                            "Abbreviation": "",
                            "Description": "limit the number of CFG iterations per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-nodes-per-condition",
                            "Abbreviation": "",
                            "Description": "limit the number of tree nodes per ITE condition",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--threads",
                            "Abbreviation": "",
                            "Description": "[=arg(=1)] Number of threads to use, if this program uses threads.  A value of zero means to use all available processors. A negative value means to use that many less than the number of available processors.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--file",
                            "Abbreviation": "-f",
                            "Description": "executable to be analyzed",
                            "Is_Required": True,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        }
                    ]
                },
                {
                    "Name": "ROSE/Partitioner options:",
                    "Arguments": [
                        {
                            "Full_Name": "--partitioner",
                            "Abbreviation": "",
                            "Description": "specify the function parititioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--serialize",
                            "Abbreviation": "",
                            "Description": "file which caches function partitioning information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--ignore-serialize-version",
                            "Abbreviation": "",
                            "Description": "reject version mismatch errors when reading a serialized file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-semantics",
                            "Abbreviation": "",
                            "Description": "disable semantic analysis during parititioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--pdebug",
                            "Abbreviation": "",
                            "Description": "enable partitioner debugging",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-executable-entry",
                            "Abbreviation": "",
                            "Description": "do not mark the entry point segment as executable",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--mark-executable",
                            "Abbreviation": "",
                            "Description": "mark all segments as executable during partitioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--log",
                            "Abbreviation": "",
                            "Description": "log facility control string",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--stockpart",
                            "Abbreviation": "",
                            "Description": "deprecated, use --parititioner=rose",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--rose-version",
                            "Abbreviation": "",
                            "Description": "output ROSE version information and exit immediately",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        }
                    ]
                }
            ]
        },
        {
            "Tool_Name": "FN2Hash",
            "Program_Name": "fn2hash",
            "Is_Pharos": True,
            "Classes": [
                {
                    "Name": "fn2hash v0.04 options:",
                    "Arguments": [
                        {
                            "Full_Name": "--min-instructions",
                            "Abbreviation": "-m",
                            "Description": "(=1) Minimum number of instructions needed to output data for a function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--basic-blocks",
                            "Abbreviation": "-B",
                            "Description": "Output optional basic block level data",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--json",
                            "Abbreviation": "-j",
                            "Description": "Output as JSON to the given file.  ('-' means stdout)",
                            "Is_Required": False,
                            "Default_Value": "output",
                            "Type": "Output_File_Args"
                        },
                        {
                            "Full_Name": "--pretty-json",
                            "Abbreviation": "-p",
                            "Description": "[=arg(=4)] Pretty-print json.  Argument is the indent width",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        }
                    ]
                },
                {
                    "Name": "CERT/Pharos options:",
                    "Arguments": [
                        {
                            "Full_Name": "--help",
                            "Abbreviation": "-h",
                            "Description": "display help",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--verbose",
                            "Abbreviation": "-v",
                            "Description": "[=arg(=3)] enable verbose logging (1-14, default 3)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timing",
                            "Abbreviation": "",
                            "Description": "Include duration field in log messages",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--batch",
                            "Abbreviation": "-b",
                            "Description": "suppress colors, progress bars, etc.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--allow-64bit",
                            "Abbreviation": "",
                            "Description": "allow analysis of 64-bit executables",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--include-func",
                            "Abbreviation": "-i",
                            "Description": "limit analysis to a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--exclude-func",
                            "Abbreviation": "-e",
                            "Description": "exclude analysis of a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--config",
                            "Abbreviation": "-C",
                            "Description": "pharos configuration file (can be specified multiple times)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--dump-config",
                            "Abbreviation": "",
                            "Description": "display current active config parameters",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-user-file",
                            "Abbreviation": "",
                            "Description": "don't load the user's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-site-file",
                            "Abbreviation": "",
                            "Description": "don't load the site's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--apidb",
                            "Abbreviation": "",
                            "Description": "path to sqlite or JSON file containing API and type information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--library",
                            "Abbreviation": "-l",
                            "Description": "specify the path to the pharos library directory",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the entire analysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-timeout",
                            "Abbreviation": "",
                            "Description": "CPU limit (sec) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--partitioner-timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the partitioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) for the entire anlaysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-instructions-per-block",
                            "Abbreviation": "",
                            "Description": "limit the number of instructions per basic block",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-iterations-per-function",
                            "Abbreviation": "",
                            "Description": "limit the number of CFG iterations per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-nodes-per-condition",
                            "Abbreviation": "",
                            "Description": "limit the number of tree nodes per ITE condition",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--threads",
                            "Abbreviation": "",
                            "Description": "[=arg(=1)] Number of threads to use, if this program uses threads.  A value of zero means to use all available processors. A negative value means to use that many less than the number of available processors.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--file",
                            "Abbreviation": "-f",
                            "Description": "executable to be analyzed",
                            "Is_Required": True,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        }
                    ]
                },
                {
                    "Name": "ROSE/Partitioner options:",
                    "Arguments": [
                        {
                            "Full_Name": "--partitioner",
                            "Abbreviation": "",
                            "Description": "specify the function parititioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--serialize",
                            "Abbreviation": "",
                            "Description": "file which caches function partitioning information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--ignore-serialize-version",
                            "Abbreviation": "",
                            "Description": "reject version mismatch errors when reading a serialized file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-semantics",
                            "Abbreviation": "",
                            "Description": "disable semantic analysis during parititioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--pdebug",
                            "Abbreviation": "",
                            "Description": "enable partitioner debugging",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-executable-entry",
                            "Abbreviation": "",
                            "Description": "do not mark the entry point segment as executable",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--mark-executable",
                            "Abbreviation": "",
                            "Description": "mark all segments as executable during partitioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--log",
                            "Abbreviation": "",
                            "Description": "log facility control string",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--stockpart",
                            "Abbreviation": "",
                            "Description": "deprecated, use --parititioner=rose",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--rose-version",
                            "Abbreviation": "",
                            "Description": "output ROSE version information and exit immediately",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        }
                    ]
                }
            ]
        },
        {
            "Tool_Name": "FN2Yara",
            "Program_Name": "fn2yara",
            "Is_Pharos": True,
            "Classes": [
                {
                    "Name": "fn2yara 0.06 Options:",
                    "Arguments": [
                        {
                            "Full_Name": "--output-filename",
                            "Abbreviation": "-o",
                            "Description": "output filename (defaults to the filename suffixed by .yara",
                            "Is_Required": False,
                            "Default_Value": "output",
                            "Type": "Output_File_Args"
                        },
                        {
                            "Full_Name": "--min-instructions",
                            "Abbreviation": "-m",
                            "Description": "(=5) Minimum number of instructions needed for an instruction block to be output for a function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--max-string-bytes",
                            "Abbreviation": "-M",
                            "Description": "(=10000) Maximum size allowed for a yara string (in bytes) to be output for a function (no rule generated if any string exceeds this)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--basic-blocks",
                            "Abbreviation": "-B",
                            "Description": "Split rules strictly by basic blocks",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--comparison",
                            "Abbreviation": "-c",
                            "Description": "Output a yara single rule that matches all instruction blocks found in the program",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--threshold",
                            "Abbreviation": "-T",
                            "Description": "(=100) A percentage threshold for the number of strings that need to match in any given rule",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--prefix",
                            "Abbreviation": "-p",
                            "Description": "Prefix for rule names",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--address-only",
                            "Abbreviation": "-a",
                            "Description": "Only output addresses of candidate functions, rather than rules.  Not in YARA format.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--include-thunks",
                            "Abbreviation": "",
                            "Description": "include thunks in output",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--oldway",
                            "Abbreviation": "-O",
                            "Description": "use old hacky way to PIC",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        }
                    ]
                },
                {
                    "Name": "CERT/Pharos options:",
                    "Arguments": [
                        {
                            "Full_Name": "--help",
                            "Abbreviation": "-h",
                            "Description": "display help",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--verbose",
                            "Abbreviation": "-v",
                            "Description": "[=arg(=3)] enable verbose logging (1-14, default 3)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timing",
                            "Abbreviation": "",
                            "Description": "Include duration field in log messages",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--batch",
                            "Abbreviation": "-b",
                            "Description": "suppress colors, progress bars, etc.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--allow-64bit",
                            "Abbreviation": "",
                            "Description": "allow analysis of 64-bit executables",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--include-func",
                            "Abbreviation": "-i",
                            "Description": "limit analysis to a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--exclude-func",
                            "Abbreviation": "-e",
                            "Description": "exclude analysis of a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--config",
                            "Abbreviation": "-C",
                            "Description": "pharos configuration file (can be specified multiple times)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--dump-config",
                            "Abbreviation": "",
                            "Description": "display current active config parameters",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-user-file",
                            "Abbreviation": "",
                            "Description": "don't load the user's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-site-file",
                            "Abbreviation": "",
                            "Description": "don't load the site's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--apidb",
                            "Abbreviation": "",
                            "Description": "path to sqlite or JSON file containing API and type information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--library",
                            "Abbreviation": "-l",
                            "Description": "specify the path to the pharos library directory",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the entire analysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-timeout",
                            "Abbreviation": "",
                            "Description": "CPU limit (sec) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--partitioner-timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the partitioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) for the entire anlaysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-instructions-per-block",
                            "Abbreviation": "",
                            "Description": "limit the number of instructions per basic block",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-iterations-per-function",
                            "Abbreviation": "",
                            "Description": "limit the number of CFG iterations per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-nodes-per-condition",
                            "Abbreviation": "",
                            "Description": "limit the number of tree nodes per ITE condition",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--threads",
                            "Abbreviation": "",
                            "Description": "[=arg(=1)] Number of threads to use, if this program uses threads.  A value of zero means to use all available processors. A negative value means to use that many less than the number of available processors.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--file",
                            "Abbreviation": "-f",
                            "Description": "executable to be analyzed",
                            "Is_Required": True,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        }
                    ]
                },
                {
                    "Name": "ROSE/Partitioner options:",
                    "Arguments": [
                        {
                            "Full_Name": "--partitioner",
                            "Abbreviation": "",
                            "Description": "specify the function parititioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--serialize",
                            "Abbreviation": "",
                            "Description": "file which caches function partitioning information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--ignore-serialize-version",
                            "Abbreviation": "",
                            "Description": "reject version mismatch errors when reading a serialized file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-semantics",
                            "Abbreviation": "",
                            "Description": "disable semantic analysis during parititioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--pdebug",
                            "Abbreviation": "",
                            "Description": "enable partitioner debugging",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-executable-entry",
                            "Abbreviation": "",
                            "Description": "do not mark the entry point segment as executable",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--mark-executable",
                            "Abbreviation": "",
                            "Description": "mark all segments as executable during partitioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--log",
                            "Abbreviation": "",
                            "Description": "log facility control string",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--stockpart",
                            "Abbreviation": "",
                            "Description": "deprecated, use --parititioner=rose",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--rose-version",
                            "Abbreviation": "",
                            "Description": "output ROSE version information and exit immediately",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        }
                    ]
                }
            ]
        },
        {
            "Tool_Name": "MKIR",
            "Program_Name": "mkir",
            "Is_Pharos": True,
            "Classes": [
                {
                    "Name": "mkir options:",
                    "Arguments": [
                        {
                            "Full_Name": "--dot",
                            "Abbreviation": "-d",
                            "Description": "directory to write graphviz file(s) instead of stdout",
                            "Is_Required": False,
                            "Default_Value": "graphviz",
                            "Type": "Output_File_Args"
                        }
                    ]
                },
                {
                    "Name": "CERT/Pharos options:",
                    "Arguments": [
                        {
                            "Full_Name": "--help",
                            "Abbreviation": "-h",
                            "Description": "display help",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--verbose",
                            "Abbreviation": "-v",
                            "Description": "[=arg(=3)] enable verbose logging (1-14, default 3)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timing",
                            "Abbreviation": "",
                            "Description": "Include duration field in log messages",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--batch",
                            "Abbreviation": "-b",
                            "Description": "suppress colors, progress bars, etc.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--allow-64bit",
                            "Abbreviation": "",
                            "Description": "allow analysis of 64-bit executables",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--include-func",
                            "Abbreviation": "-i",
                            "Description": "limit analysis to a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--exclude-func",
                            "Abbreviation": "-e",
                            "Description": "exclude analysis of a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--config",
                            "Abbreviation": "-C",
                            "Description": "pharos configuration file (can be specified multiple times)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--dump-config",
                            "Abbreviation": "",
                            "Description": "display current active config parameters",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-user-file",
                            "Abbreviation": "",
                            "Description": "don't load the user's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-site-file",
                            "Abbreviation": "",
                            "Description": "don't load the site's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--apidb",
                            "Abbreviation": "",
                            "Description": "path to sqlite or JSON file containing API and type information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--library",
                            "Abbreviation": "-l",
                            "Description": "specify the path to the pharos library directory",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the entire analysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-timeout",
                            "Abbreviation": "",
                            "Description": "CPU limit (sec) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--partitioner-timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the partitioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) for the entire anlaysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-instructions-per-block",
                            "Abbreviation": "",
                            "Description": "limit the number of instructions per basic block",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-iterations-per-function",
                            "Abbreviation": "",
                            "Description": "limit the number of CFG iterations per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-nodes-per-condition",
                            "Abbreviation": "",
                            "Description": "limit the number of tree nodes per ITE condition",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--threads",
                            "Abbreviation": "",
                            "Description": "[=arg(=1)] Number of threads to use, if this program uses threads.  A value of zero means to use all available processors. A negative value means to use that many less than the number of available processors.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--file",
                            "Abbreviation": "-f",
                            "Description": "executable to be analyzed",
                            "Is_Required": True,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        }
                    ]
                },
                {
                    "Name": "ROSE/Partitioner options:",
                    "Arguments": [
                        {
                            "Full_Name": "--partitioner",
                            "Abbreviation": "",
                            "Description": "specify the function parititioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--serialize",
                            "Abbreviation": "",
                            "Description": "file which caches function partitioning information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--ignore-serialize-version",
                            "Abbreviation": "",
                            "Description": "reject version mismatch errors when reading a serialized file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-semantics",
                            "Abbreviation": "",
                            "Description": "disable semantic analysis during parititioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--pdebug",
                            "Abbreviation": "",
                            "Description": "enable partitioner debugging",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-executable-entry",
                            "Abbreviation": "",
                            "Description": "do not mark the entry point segment as executable",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--mark-executable",
                            "Abbreviation": "",
                            "Description": "mark all segments as executable during partitioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--log",
                            "Abbreviation": "",
                            "Description": "log facility control string",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--stockpart",
                            "Abbreviation": "",
                            "Description": "deprecated, use --parititioner=rose",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--rose-version",
                            "Abbreviation": "",
                            "Description": "output ROSE version information and exit immediately",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        }
                    ]
                }
            ]
        },
        {
            "Tool_Name": "PathAnalyzer",
            "Program_Name": "pathanalyzer",
            "Is_Pharos": True,
            "Classes": [
                {
                    "Name": "PathAnalyzer version 0.3 options:",
                    "Arguments": [
                        {
                            "Full_Name": "--dot",
                            "Abbreviation": "-d",
                            "Description": "The directory to write DOT file(s)",
                            "Is_Required": False,
                            "Default_Value": "dot",
                            "Type": "Output_File_Args"
                        },
                        {
                            "Full_Name": "--z3",
                            "Abbreviation": "-z",
                            "Description": "Save z3 output file (for troubleshooting)",
                            "Is_Required": False,
                            "Default_Value": "z3",
                            "Type": "Output_File_Args"
                        },
                        {
                            "Full_Name": "--goal",
                            "Abbreviation": "-g",
                            "Description": "The goal address",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--start",
                            "Abbreviation": "-s",
                            "Description": "The starting address",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        }
                    ]
                },
                {
                    "Name": "CERT/Pharos options:",
                    "Arguments": [
                        {
                            "Full_Name": "--help",
                            "Abbreviation": "-h",
                            "Description": "display help",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--verbose",
                            "Abbreviation": "-v",
                            "Description": "[=arg(=3)] enable verbose logging (1-14, default 3)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timing",
                            "Abbreviation": "",
                            "Description": "Include duration field in log messages",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--batch",
                            "Abbreviation": "-b",
                            "Description": "suppress colors, progress bars, etc.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--allow-64bit",
                            "Abbreviation": "",
                            "Description": "allow analysis of 64-bit executables",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--include-func",
                            "Abbreviation": "-i",
                            "Description": "limit analysis to a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--exclude-func",
                            "Abbreviation": "-e",
                            "Description": "exclude analysis of a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--config",
                            "Abbreviation": "-C",
                            "Description": "pharos configuration file (can be specified multiple times)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--dump-config",
                            "Abbreviation": "",
                            "Description": "display current active config parameters",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-user-file",
                            "Abbreviation": "",
                            "Description": "don't load the user's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-site-file",
                            "Abbreviation": "",
                            "Description": "don't load the site's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--apidb",
                            "Abbreviation": "",
                            "Description": "path to sqlite or JSON file containing API and type information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--library",
                            "Abbreviation": "-l",
                            "Description": "specify the path to the pharos library directory",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the entire analysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-timeout",
                            "Abbreviation": "",
                            "Description": "CPU limit (sec) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--partitioner-timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the partitioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) for the entire anlaysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-instructions-per-block",
                            "Abbreviation": "",
                            "Description": "limit the number of instructions per basic block",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-iterations-per-function",
                            "Abbreviation": "",
                            "Description": "limit the number of CFG iterations per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-nodes-per-condition",
                            "Abbreviation": "",
                            "Description": "limit the number of tree nodes per ITE condition",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--threads",
                            "Abbreviation": "",
                            "Description": "[=arg(=1)] Number of threads to use, if this program uses threads.  A value of zero means to use all available processors. A negative value means to use that many less than the number of available processors.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--file",
                            "Abbreviation": "-f",
                            "Description": "executable to be analyzed",
                            "Is_Required": True,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        }
                    ]
                },
                {
                    "Name": "ROSE/Partitioner options:",
                    "Arguments": [
                        {
                            "Full_Name": "--partitioner",
                            "Abbreviation": "",
                            "Description": "specify the function parititioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--serialize",
                            "Abbreviation": "",
                            "Description": "file which caches function partitioning information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--ignore-serialize-version",
                            "Abbreviation": "",
                            "Description": "reject version mismatch errors when reading a serialized file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-semantics",
                            "Abbreviation": "",
                            "Description": "disable semantic analysis during parititioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--pdebug",
                            "Abbreviation": "",
                            "Description": "enable partitioner debugging",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-executable-entry",
                            "Abbreviation": "",
                            "Description": "do not mark the entry point segment as executable",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--mark-executable",
                            "Abbreviation": "",
                            "Description": "mark all segments as executable during partitioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--log",
                            "Abbreviation": "",
                            "Description": "log facility control string",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--stockpart",
                            "Abbreviation": "",
                            "Description": "deprecated, use --parititioner=rose",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--rose-version",
                            "Abbreviation": "",
                            "Description": "output ROSE version information and exit immediately",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        }
                    ]
                }
            ]
        },
        {
            "Tool_Name": "PathFinder",
            "Program_Name": "pathfinder",
            "Is_Pharos": True,
            "Classes": [
                {
                    "Name": "PathFinder version 0.1 options:",
                    "Arguments": [
                        {
                            "Full_Name": "--target",
                            "Abbreviation": "-t",
                            "Description": "The goal address",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--source",
                            "Abbreviation": "-s",
                            "Description": "The source address",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--engine",
                            "Abbreviation": "-e",
                            "Description": "The analysis engine (probably spacer)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        }
                    ]
                },
                {
                    "Name": "CERT/Pharos options:",
                    "Arguments": [
                        {
                            "Full_Name": "--help",
                            "Abbreviation": "-h",
                            "Description": "display help",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--verbose",
                            "Abbreviation": "-v",
                            "Description": "[=arg(=3)] enable verbose logging (1-14, default 3)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timing",
                            "Abbreviation": "",
                            "Description": "Include duration field in log messages",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--batch",
                            "Abbreviation": "-b",
                            "Description": "suppress colors, progress bars, etc.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--allow-64bit",
                            "Abbreviation": "",
                            "Description": "allow analysis of 64-bit executables",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--include-func",
                            "Abbreviation": "-i",
                            "Description": "limit analysis to a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--exclude-func",
                            "Abbreviation": "-e",
                            "Description": "exclude analysis of a specific function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--config",
                            "Abbreviation": "-C",
                            "Description": "pharos configuration file (can be specified multiple times)",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--dump-config",
                            "Abbreviation": "",
                            "Description": "display current active config parameters",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-user-file",
                            "Abbreviation": "",
                            "Description": "don't load the user's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-site-file",
                            "Abbreviation": "",
                            "Description": "don't load the site's configuration file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--apidb",
                            "Abbreviation": "",
                            "Description": "path to sqlite or JSON file containing API and type information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--library",
                            "Abbreviation": "-l",
                            "Description": "specify the path to the pharos library directory",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the entire analysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-timeout",
                            "Abbreviation": "",
                            "Description": "CPU limit (sec) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--partitioner-timeout",
                            "Abbreviation": "",
                            "Description": "time limit (sec) for the partitioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) for the entire anlaysis",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--per-function-maximum-memory",
                            "Abbreviation": "",
                            "Description": "maximum memory (Mib) per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-instructions-per-block",
                            "Abbreviation": "",
                            "Description": "limit the number of instructions per basic block",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-iterations-per-function",
                            "Abbreviation": "",
                            "Description": "limit the number of CFG iterations per function",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--maximum-nodes-per-condition",
                            "Abbreviation": "",
                            "Description": "limit the number of tree nodes per ITE condition",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--threads",
                            "Abbreviation": "",
                            "Description": "[=arg(=1)] Number of threads to use, if this program uses threads.  A value of zero means to use all available processors. A negative value means to use that many less than the number of available processors.",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--file",
                            "Abbreviation": "-f",
                            "Description": "executable to be analyzed",
                            "Is_Required": True,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        }
                    ]
                },
                {
                    "Name": "ROSE/Partitioner options:",
                    "Arguments": [
                        {
                            "Full_Name": "--partitioner",
                            "Abbreviation": "",
                            "Description": "specify the function parititioner",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--serialize",
                            "Abbreviation": "",
                            "Description": "file which caches function partitioning information",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_File_Args"
                        },
                        {
                            "Full_Name": "--ignore-serialize-version",
                            "Abbreviation": "",
                            "Description": "reject version mismatch errors when reading a serialized file",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-semantics",
                            "Abbreviation": "",
                            "Description": "disable semantic analysis during parititioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--pdebug",
                            "Abbreviation": "",
                            "Description": "enable partitioner debugging",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--no-executable-entry",
                            "Abbreviation": "",
                            "Description": "do not mark the entry point segment as executable",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--mark-executable",
                            "Abbreviation": "",
                            "Description": "mark all segments as executable during partitioning",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--log",
                            "Abbreviation": "",
                            "Description": "log facility control string",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Text_Args"
                        },
                        {
                            "Full_Name": "--stockpart",
                            "Abbreviation": "",
                            "Description": "deprecated, use --parititioner=rose",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        },
                        {
                            "Full_Name": "--rose-version",
                            "Abbreviation": "",
                            "Description": "output ROSE version information and exit immediately",
                            "Is_Required": False,
                            "Default_Value": "",
                            "Type": "Input_Flag_Args"
                        }
                    ]
                }
            ]
        }
    ]}

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
    ResourceManager(db_name).setup()
    ResourceManager(db_name).initialize_pharos_tools()
    # if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    #     ResourceManager(db_name).initialize_pharos_tools()
    #     tool_list = ResourceManager(db_name).get_all_tools()
    #     print(len(tool_list))
setup_pharos_tools(app)

def thread_test_new_execution(task_type, task_id):
    """this is the implementation for testing new execution manager

    """
    if task_type == "false":
        with open("/home/vagrant/new-felucca/tests/sample_output/input_wrong.json",'r') as f:
            json_data = json.load(f)
        job = Job.from_json(json_data)
        job.job_id = "job_id_false"
        task = job.tasks[0]
        task.task_id = task_id
    else:
        with open("/home/vagrant/new-felucca/tests/sample_output/input.json",'r') as f:
            json_data = json.load(f)
        job = Job.from_json(json_data)
        job.job_id = "job_id_for_true"
        task = job.tasks[0]
        task.task_id = task_id

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
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
