import os
import sys
import json
import requests
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


class BackEndTest(unittest.TestCase):
    def __init__(self, test_name, input_json_path):
        super(BackEndTest, self).__init__(test_name)
        self.input_json_path = input_json_path
    
    def test_backend_pipeline(self):
        url = "http://localhost:5000/job"
        # r = request.post
        pass

def start_flask():
    app.run(host='0.0.0.0', debug=False)

if __name__ == '__main__':
    thread = Thread(target=start_flask, args=())
    thread.start()

    print("Server started...")
    sleep(2.0)

    suite = unittest.TestSuite()
    suite.addTest(BackEndTest('test_backend_pipeline', '../../tests/sample_output/input.json'))

    runner = unittest.TextTestRunner()
    runner.run(suite)