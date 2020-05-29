import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '../../felucca/backend'))

from datetime import datetime
from threading import Thread

from time import sleep
from common.job import Job
from common.status import Status
from common.task import Task
from job_manager import JobManager
from resource_manager import ResourceManager
from server import app


TASK_DICT = {
    # basic argument testing ooanalyer
    1: "ooanalyzer -j output.json -f /vagrant/docker/oo.exe",
    2: "ooanalyzer -F facts -f /vagrant/docker/oo.exe",
    3: "ooanalyzer -R results -f /vagrant/docker/oo.exe",
    4: "ooanalyzer -F facts -R results -f /vagrant/docker/oo.exe",
    5: "ooanalyzer -j output.json -F facts -R results -f /vagrant/docker/oo.exe",
    6: "ooanalyzer -j output.json -F facts -n 000 -R results -f /vagrant/docker/oo.exe",
    7: "ooanalyzer -f /vagrant/docker/oo.exe -j output.json -R facts -n 000 -F results",
    8: "ooanalyzer -R output.json -j facts -n 000 -f /vagrant/docker/oo.exe -R results",
    9: "ooanalyzer -R output.json -j facts -n address -f /vagrant/docker/oo.exe -R results",

    # extra space
    10: "ooanalyzer -j output.json -F facts -R results      -f /vagrant/docker/oo.exe",
    11: "ooanalyzer -j output.json -F     facts -R results      -f /vagrant/docker/oo.exe",
    12: "  ooanalyzer -j output.json -F     facts -R results      -f /vagrant/docker/oo.exe",

    # parent directory
    13: "ooanalyzer -j output.json -F facts -R results -f /vagrant/../vagrant/docker/oo.exe",
    14: "ooanalyzer -j output.json -F facts -R results -f /vagrant/../vagrant/docker/../docker/oo.exe"
}


class BackEndTest(unittest.TestCase):
    def __init__(self, test_name, location, tool_type, command_line_input):
        super(BackEndTest, self).__init__(test_name)
        self.location = location
        self.tool_type = tool_type
        self.command_line_input = command_line_input

    def test_basic_arguments(self):
        now = datetime.now()
        dummy_job = Job("Test Job", "OOanalyer Job", now)
        test_task = Task(self.location, self.tool_type, self.command_line_input)
        dummy_job.tasks = [test_task]
        job_id, tasks_id = JobManager().submit_job(dummy_job)
        job_metadata = ResourceManager().get_job_by_id(job_id)

        ms_without_ns = int(now.microsecond / 1000) * 1000
        now = now.replace(microsecond=ms_without_ns)

        self.assertEqual(dummy_job.name, job_metadata.name)
        self.assertEqual(dummy_job.comments, job_metadata.comments)
        self.assertEqual(now, job_metadata.created_time)
        self.assertEqual(Status.Pending, job_metadata.status)

        fetched_tasks_id = ResourceManager().get_tasks_by_job_id(job_id)
        self.assertEqual(tasks_id, fetched_tasks_id)

        task_metadata = ResourceManager().get_task_by_id(tasks_id[0])
        self.assertEqual(task_metadata.command_line_input, self.command_line_input)
        self.assertEqual(task_metadata.tool_type, self.tool_type)
        self.assertEqual(task_metadata.status, Status.Pending)

        # magic sleep number
        sleep(30.0)

        # TODO: job status check

        fetched_tasks_id = ResourceManager().get_tasks_by_job_id(job_id)
        self.assertEqual(tasks_id, fetched_tasks_id)

        # test after finish

        with open("../sample_output/output.json", "rb") as f:
            output_json_bytes = f.read()
        with open("../sample_output/facts", "rb") as f:
            facts_bytes = f.read()
        with open("../sample_output/results", "rb") as f:
            results_bytes = f.read()

        task_metadata = ResourceManager().get_task_by_id(tasks_id[0])
        self.assertEqual(task_metadata.command_line_input, self.command_line_input)
        self.assertEqual(task_metadata.tool_type, self.tool_type)
        self.assertEqual(task_metadata.status, Status.Successful)
        self.assertEqual(task_metadata.output["output.json"], output_json_bytes)
        self.assertEqual(task_metadata.log["facts"], facts_bytes)
        self.assertEqual(task_metadata.log["results"], results_bytes)

        # TODO: check stdout and stderr
        print(task_metadata.stdout)
        print(task_metadata.stderr)

        ResourceManager().remove_job_by_id(job_id)
        ResourceManager().remove_tasks_by_job_id(job_id)


def start_flask():
    app.run(host='0.0.0.0', debug=True)


if __name__ == '__main__':
    thread = Thread(target=start_flask(), args=())
    thread.start()

    suite = unittest.TestSuite()
    for i in range(1, 15):
        suite.addTest(BackEndTest('test_basic_arguments', '/vagrant/docker/oo.exe', 'ooanalyzer', TASK_DICT[i]))

    runner = unittest.TextTestRunner()
    runner.run(suite)








