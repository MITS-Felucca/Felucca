import os
import sys
import json
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '/vagrant/felucca/backend'))
from datetime import datetime
from flask import request
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
    1: "ooanalyzer -j output.json -f /vagrant/tests/sample_output/oo.exe",
    2: "ooanalyzer -F facts -f /vagrant/tests/sample_output/oo.exe",
    3: "ooanalyzer -F facts -R results -f /vagrant/tests/sample_output/oo.exe",
    4: "ooanalyzer -j output.json -F facts -R results -f /vagrant/tests/sample_output/oo.exe",
    5: "ooanalyzer -j output.json -F facts -n 000 -R results -f /vagrant/tests/sample_output/oo.exe",
    6: "ooanalyzer -f /vagrant/tests/sample_output/oo.exe -j output.json -R results -n 000 -F facts",
    7: "ooanalyzer -R results -j output.json -n 000 -f /vagrant/tests/sample_output/oo.exe -F facts",
    8: "ooanalyzer -F facts -j output.json -n address -f /vagrant/tests/sample_output/oo.exe -R results",

    # extra space
    9: "ooanalyzer -j output.json -F facts -R results      -f /vagrant/tests/sample_output/oo.exe",
    10: "ooanalyzer -j output.json -F     facts -R results      -f /vagrant/tests/sample_output/oo.exe",
    11: "  ooanalyzer -j output.json -F     facts -R results      -f /vagrant/tests/sample_output/oo.exe",

    # parent directory
    12: "ooanalyzer -j output.json -F facts -R results -f /vagrant/../vagrant/tests/sample_output/oo.exe",
    13: "ooanalyzer -j output.json -F facts -R results -f /vagrant/../vagrant/tests/../tests/sample_output/oo.exe"
}

class BackEndTest(unittest.TestCase):
    def __init__(self, test_name, location, tool_type, command_line_input, index):
        super(BackEndTest, self).__init__(test_name)
        self.location = location
        self.tool_type = tool_type
        self.command_line_input = command_line_input
        self.job_name = "Test Job"
        self.comments = "OOanalyer Job"
        self.index = index


    def setUp(self):

        print("Test with command\n%s\n" % self.command_line_input)
        print("Submitting job...")
        now = datetime.now()
        dummy_job = Job(self.job_name, self.comments, now)
        test_task = Task(self.location, self.tool_type, self.command_line_input)
        dummy_job.tasks = [test_task]
        job_id, tasks_id = JobManager().submit_job(dummy_job)

        self.job_id = job_id
        self.tasks_id = tasks_id

        ms_without_ns = int(now.microsecond / 1000) * 1000
        self.now = now.replace(microsecond=ms_without_ns)

    def test_basic_arguments(self):

        print("Checking job metadata...")
        job_metadata = ResourceManager().get_job_by_id(self.job_id)
        self.assertEqual(self.job_name, job_metadata.name)
        self.assertEqual(self.comments, job_metadata.comments)
        self.assertEqual(self.now, job_metadata.created_time)
        self.assertEqual(Status.Pending, job_metadata.status)

        print("Checking task metadata...")
        fetched_tasks = ResourceManager().get_tasks_by_job_id(self.job_id)
        self.assertEqual(len(fetched_tasks), 1)
        self.assertEqual(fetched_tasks[0].command_line_input, self.command_line_input)
        # self.assertEqual(fetched_tasks[0].tool_type, self.tool_type)
        self.assertEqual(fetched_tasks[0].status, Status.Pending)

        task_metadata = ResourceManager().get_task_by_id(self.tasks_id[0])
        self.assertEqual(task_metadata.command_line_input, self.command_line_input)
        # self.assertEqual(task_metadata.tool_type, self.tool_type)
        self.assertEqual(task_metadata.status, Status.Pending)

        print("Waiting for task to finish...")
        # magic sleep number
        sleep(60.0)

        # TODO: job status check

        print("Checking output...")

        fetched_tasks = ResourceManager().get_tasks_by_job_id(self.job_id)
        self.assertEqual(len(fetched_tasks), 1)
        self.assertEqual(fetched_tasks[0].command_line_input, self.command_line_input)
        # self.assertEqual(fetched_tasks[0].tool_type, self.tool_type)
        self.assertEqual(fetched_tasks[0].status, Status.Successful)

        if self.index not in [2, 3, 4]:
            json.loads(fetched_tasks[0].output["output.json"])
        if self.index not in [1, 3]:
            self.assertTrue('facts' in fetched_tasks[0].log)
        if self.index not in [1, 2]:
            self.assertTrue('results' in fetched_tasks[0].log)

        # test after finish

        task_metadata = ResourceManager().get_task_by_id(self.tasks_id[0])
        self.assertEqual(task_metadata.command_line_input, self.command_line_input)
        # self.assertEqual(task_metadata.tool_type, self.tool_type)
        self.assertEqual(task_metadata.status, Status.Successful)

        if self.index not in [2, 3, 4]:
            json.loads(task_metadata.output["output.json"])
        if self.index not in [1, 3]:
            self.assertTrue('facts' in task_metadata.log)
        if self.index not in [1, 2]:
            self.assertTrue('results' in task_metadata.log)

        print(task_metadata.stdout)
        print(task_metadata.stderr)
        print('Test passed')

    def tearDown(self):
        if self.job_id:
            ResourceManager().remove_job_by_id(self.job_id)
            ResourceManager().remove_tasks_by_job_id(self.job_id)


def start_flask():
    app.run(host='0.0.0.0', debug=False)


if __name__ == '__main__':
    thread = Thread(target=start_flask, args=())
    thread.start()

    print("Server started...")
    sleep(2.0)

    suite = unittest.TestSuite()
    for i in range(1, 14):
        suite.addTest(BackEndTest('test_basic_arguments', '/vagrant/tests/sample_output/oo.exe', 'ooanalyzer', TASK_DICT[i], i))

    runner = unittest.TextTestRunner()
    runner.run(suite)

