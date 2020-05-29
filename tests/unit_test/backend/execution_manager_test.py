import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend'))
import unittest
from execution_manager import ExecutionManager

class TestTask(unittest.TestCase):
    def setUp(self):
        self.execution_manager = ExecutionManager()


if __name__ == '__main__':  
    unittest.main()