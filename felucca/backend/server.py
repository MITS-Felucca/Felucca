#! /usr/bin/env python3
import docker
import sys
sys.path.append(r'../common')
import threading
from flask import Flask
from job_manager import JobManager
from execution_manager import ExecutionManager

app = Flask(__name__)

def start_execution():
    abs_exe_path,command_line_input = JobManager().get_task()
    #print(f"\nabs_exe_path:\n {abs_exe_path}")
    #print(command_line_input)
    #print(f"\ncommand_line_input: \n{command_line_input}")
    adjusted_command_line_input = ExecutionManager().command_line_input_parser(command_line_input)
    #print(f"\nadjusted_command_line_input:\n{adjusted_command_line_input}")
    #print(abs_exe_path)
    
    client = docker.from_env()

    container = client.containers.create("felucca/pharos",command="/bin/bash",tty=True,stdin_open=True,auto_remove=False)
    
    container.start()

    ExecutionManager().copy_to_container(abs_exe_path,"/tmp/foo.txt",container)
    
    exec_log = container.exec_run("cat /tmp/foo.txt",stdout=True,stderr=True,stream=True)

    for line in exec_log[1]:
        print(line)
    
    print('Container Status : {}'.format(container.status))


@app.route("/")
def hello():
    thread = threading.Thread(target=start_execution)
    thread.start()
    return "Hello World!"




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
    
    

