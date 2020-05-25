import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../felucca'))
import unittest
from backend.common.task import Task

class TestTask(unittest.TestCase):
    def setUp(self):
        self.task = Task("task_file", "task_tool", "task_cmd")
    
    def test_set_job_id(self):
        self.task.job_id = 12345
        self.assertEqual(12345, self.task.job_id)

    def test_set_task_id(self):
        self.task.task_id = 123
        self.assertEqual(123, self.task.task_id)

    def test_set_result(self):
        self.task.set_result("output.json", "pharos.log", "pharos cmd complete", "no error")
        output_file = open(self.task.output)
        log_file = open(self.task.log)
        self.assertEqual(output_file.name, "output.json")
        self.assertEqual(log_file.name, "pharos.log")
        self.assertEqual(self.task.stdout, "pharos cmd complete")
        self.assertEqual(self.task.stderr, "no error")
        output_file.close()
        log_file.close()

if __name__ == '__main__':  
    unittest.main()