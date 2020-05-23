import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca'))
import unittest
from common.task import Task

class TestTask(unittest.TestCase):
    def setUp(self):
        self.task = Task("task_file", "task_tool", "task_cmd")
    
    def test_set_job_id(self):
        self.task.job_id = 12345
        self.assertEqual(12345, self.task.job_id)

    def test_set_task_ids(self):
        self.task.task_ids = [123,124,125,126]
        self.assertEqual([123,124,125,126], self.task.task_ids)

    def test_set_result(self):
        self.task.set_result("output.json", "pharos.log", "pharos cmd complete")
        output_file = open(self.task.output)
        log_file = open(self.task.log)
        self.assertEqual(output_file.name, "output.json")
        self.assertEqual(log_file.name, "pharos.log")
        self.assertEqual(self.task.stdout, "pharos cmd complete")
        output_file.close()
        log_file.close()

if __name__ == '__main__':  
    unittest.main()