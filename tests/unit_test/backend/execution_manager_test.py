import os
import sys
import requests
import docker
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend'))
import unittest
from execution_manager import ExecutionManager
from time import sleep

SERVER_IP = '0.0.0.0'
SERVER_PORT = '5000'

class TestTask(unittest.TestCase):
    def setUp(self):
        self.execution_manager = ExecutionManager()
        
    def test_running_output(self):
        #test execution manager to run a right command
        requests.get('http://%s:%s/test_EM_running' % (SERVER_IP, SERVER_PORT))
        sleep(30)
        self.assertTrue(os.path.exists("/tmp/Felucca/result/thisisatrueinputcmd_task/facts"))
        self.assertTrue(os.path.exists("/tmp/Felucca/result/thisisatrueinputcmd_task/output.json"))
        self.assertTrue(os.path.exists("/tmp/Felucca/result/thisisatrueinputcmd_task/results"))
        self.assertFalse(os.path.exists("/tmp/Felucca/result/thisisafalseinputcmdtask/facts"))
        self.assertFalse(os.path.exists("/tmp/Felucca/result/thisisafalseinputcmdtask/output.json"))
        self.assertFalse(os.path.exists("/tmp/Felucca/result/thisisafalseinputcmdtask/results"))
    def test_updating_kernal(self):
        pass

if __name__ == '__main__':  
    unittest.main()