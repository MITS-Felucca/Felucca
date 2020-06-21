import os
import sys
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend'))
import unittest
from execution_manager import ExecutionManager
from time import sleep

SERVER_IP = '0.0.0.0'
SERVER_PORT = '5000'

class TestTask(unittest.TestCase):
    def setUp(self):
        self.execution_manager = ExecutionManager()
        
    def test_output(self):
        task_id = "test"
        requests.get('http://%s:%s/test_new_execution/%s' % (SERVER_IP, SERVER_PORT, task_id))
        sleep(10)
        self.assertTrue(os.path.exists("/tmp/Felucca/result/%s/facts"  % (task_id)))
        self.assertTrue(os.path.exists("/tmp/Felucca/result/%s/output.json"% (task_id) ))
        self.assertTrue(os.path.exists("/tmp/Felucca/result/%s/results"% (task_id) ))
        

if __name__ == '__main__':  
    unittest.main()