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
        #test execution manager to run a right command
        task_true_id = "test_true"
        requests.get('http://%s:%s/test_new_execution/true/%s' % (SERVER_IP, SERVER_PORT, task_true_id))
        #test execution manager to run a wrong command
        task_false_id = "test_false"
        requests.get('http://%s:%s/test_new_execution/false/%s' % (SERVER_IP, SERVER_PORT, task_false_id))
        sleep(30)
        self.assertTrue(os.path.exists("/tmp/Felucca/result/%s/facts"  % (task_true_id)))
        self.assertTrue(os.path.exists("/tmp/Felucca/result/%s/output.json"% (task_true_id) ))
        self.assertTrue(os.path.exists("/tmp/Felucca/result/%s/results"% (task_true_id) ))
        self.assertFalse(os.path.exists("/tmp/Felucca/result/%s/facts"  % (task_false_id)))
        self.assertFalse(os.path.exists("/tmp/Felucca/result/%s/output.json"% (task_false_id) ))
        self.assertFalse(os.path.exists("/tmp/Felucca/result/%s/results"% (task_false_id) ))
        

if __name__ == '__main__':  
    unittest.main()