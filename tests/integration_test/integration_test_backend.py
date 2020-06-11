import base64
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
        url = "http://localhost:5000/clean-all"
        response = requests.get(url=url)

        url = "http://localhost:5000/job"
        with open(self.input_json_path, "r") as f:
            data = json.load(f)
        response = requests.post(url=url, json=data)
        print(response.json())
        self.assertEqual(response.json(), {"status": "ok"})

        url = "http://localhost:5000/job-list/json"
        response = requests.get(url=url)
        print(response.json())

        sleep(20)

        job_id = response.json()["Job_List"][0]["ID"]
        url = f"http://localhost:5000/job-info/{job_id}/json"
        response = requests.get(url=url)
        print(response.json())

        with open("/vagrant/tests/sample_output/output.json", "rb") as f:
            output_json = base64.b64encode(f.read()).decode('utf-8')
        with open("/vagrant/tests/sample_output/facts", "rb") as f:
            facts_json = base64.b64encode(f.read()).decode('utf-8')
        with open("/vagrant/tests/sample_output/results.json", "rb") as f:
            results_json = base64.b64encode(f.read()).decode('utf-8')

        task_id = response.json()["Tasks"][0]["ID"]
        url = f"http://localhost:5000//task/{task_id}/output/output.json/json"
        response = requests.get(url=url)
        # self.assertEqual(response.json()["Content"], output_json)
        # print(response.json())

        url = f"http://localhost:5000//task/{task_id}/log/facts/json"
        response = requests.get(url=url)
        # self.assertEqual(response.json()["Content"], facts_json)
        # print(response.json())

        url = f"http://localhost:5000//task/{task_id}/log/results.json/json"
        response = requests.get(url=url)
        # self.assertEqual(response.json()["Content"], results_json)
        # print(response.json())
        
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