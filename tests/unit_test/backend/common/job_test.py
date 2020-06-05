import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../felucca'))
import unittest
from datetime import datetime
from backend.common.job import Job
from backend.common.task import Task


class TestJob(unittest.TestCase):
    def setUp(self):
        self.task1 = Task("task1_file", "task1_tool_type", "task1_cmd")
        self.task2 = Task("task1_file", "task1_tool_type", "task1_cmd")
        self.now = datetime.now()
        self.job = Job("MyJob","pharos job",self.now)

    def test_create_time(self):
        self.assertEqual(self.job.created_time, self.now)

    def test_tasks(self):
        self.job.tasks = [self.task1, self.task2]
        self.assertEqual(self.job.tasks, [self.task1, self.task2])

if __name__ == '__main__':  
    unittest.main()