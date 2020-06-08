import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../felucca'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../sample_output'))
import unittest
from datetime import datetime
from backend.common.job import Job
from backend.common.task import Task


class TestJob(unittest.TestCase):
    def setUp(self):
        with open("../../../sample_output/input.json",'r') as fp:
            self.json_data = json.load(fp)
               
        self.job = Job.from_json(self.json_data)
        
    def test_job(self):
        
        self.assertEqual(self.job.name, self.json_data["Job_Name"])
        self.assertEqual(self.job.comments, self.json_data["Job_Comment"])
        self.assertEqual(self.job.created_time, self.json_data["Created_Time"])

    def test_tasks(self):
        test_task = []
        for task_dict in self.json_data["Tasks"]:
            task = Task.from_json(task_dict)
            test_task.append(task)
        for i in range(len(test_task)):
            self.assertEqual(self.job.tasks[i].arguments, test_task[i].arguments)
            self.assertEqual(self.job.tasks[i].files, test_task[i].files)
            self.assertEqual(self.job.tasks[i].tool_type, test_task[i].tool_type)

if __name__ == '__main__':  
    unittest.main()