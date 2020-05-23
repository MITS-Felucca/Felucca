import unittest
import requests


class TestTask(unittest.TestCase):
    def setUp(self):
        pass

    def test_success_request(self):
        r = requests.post('http://172.17.0.2:5000/task',
                          data={'task_id': 1,
                                'command_line_input': 'ooanalyzer -j output.json -F facts -R results -f /test/oo.exe'})

        self.assertTrue(r.content)

    def test_failure_request(self):
        r = requests.post('http://172.17.0.2:5000/task',
                          data={'task_id': 2,
                                'command_line_input': 'ooanalyzer -j output.json -F facts -R results -f /backend/oo.exe'})

        self.assertTrue(r.content)

    def test_error_request(self):
        r = requests.post('http://172.17.0.2:5000/task',
                          data={'task_id': 3,
                                'command_line_input': 'oanalyzer -j output.json -F facts -R results -f /test/oo.exe'})

        self.assertTrue(r.content)

if __name__ == '__main__':
    unittest.main()