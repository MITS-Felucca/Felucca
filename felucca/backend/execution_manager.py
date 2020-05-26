
import requests
import sys

from resource_manager import ResourceManager
from job_manager import JobManager
from common.singleton import Singleton


CONTAINER_PORT = '5000'
@Singleton
class ExecutionManager(object):

    def __init__(self):
        self.tasks = {}

    def sumbit_task(self, task_id, command_line_input):
        container_ip = self.tasks[task_id][1].ip
        requests.post("http://%s:%s/task" % (container_ip, CONTAINER_PORT), data={"task_id": task_id,
                                                                                  "command_line_input": command_line_input})

    def save_result(self, task_id, status, stderr, stdout):
        container = self.tasks[task_id][1]
        container.kill()
        output_path = self.tasks[task_id]["output_path"]
        log_path = self.tasks[task_id]["log_path"]
        ResourceManager().save_result(task_id, output_path, log_path, stdout, stderr, status)
        JobManager().finish_task(task_id)
        self.tasks.pop(task_id, None)

# submit_task
# save_result