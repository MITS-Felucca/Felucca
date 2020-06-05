import os
import sys
import unittest
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend/common'))
from common.job import Job
from common.status import Status
from common.task import Task
from resource_manager import ResourceManager

class TestResourceManager(unittest.TestCase):
    def setUp(self):
        self.manager = ResourceManager()
    
    def test_insert_job_without_tasks(self):
        # Create a sample job
        job_name = "Test_job"
        job_comments = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comments, created_time)
        new_job.tasks = []
        job_id, tasks_id = self.manager.insert_new_job(new_job)

        # Check job_id & tasks_id
        self.assertTrue(isinstance(job_id, str))
        self.assertEqual(len(tasks_id), 0)

        # Remove the nanoseconds in created_time as the precision in MongoDB doesn't store nanoseconds
        ms_without_ns = int(created_time.microsecond / 1000) * 1000
        created_time = created_time.replace(microsecond=ms_without_ns)

        # Rebuild the job object and check the contents
        rebuilt_job = self.manager.get_job_by_id_without_tasks(job_id)
        self.assertEqual(rebuilt_job.name, job_name)
        self.assertEqual(rebuilt_job.comments, job_comments)
        self.assertEqual(rebuilt_job.created_time, created_time)
        self.assertEqual(rebuilt_job.status, Status.Pending)

        # Remove the inserted job after test
        self.manager.remove_job_by_id(job_id)
    
    def test_insert_job_with_single_task(self):
        # Create a sample task
        task_arguments = {
            "-j": "output.json",
            "-F": "facts",
            "-R": "results",
            "-f": "oo.exe",
        }
        task_tool_type = 0
        new_task = Task({}, task_tool_type, task_arguments)

        # Create a sample job
        job_name = "Test_job"
        job_comments = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comments, created_time)
        new_job.tasks = [new_task]
        job_id, tasks_id = self.manager.insert_new_job(new_job)

        # Check job_id & tasks_id
        self.assertTrue(isinstance(job_id, str))
        self.assertEqual(len(tasks_id), 1)
        self.assertTrue(isinstance(tasks_id[0], str))

        # Remove the nanoseconds in created_time as the precision in MongoDB doesn't store nanoseconds
        ms_without_ns = int(created_time.microsecond / 1000) * 1000
        created_time = created_time.replace(microsecond=ms_without_ns)

        # Rebuild the job object and check the contents
        rebuilt_job = self.manager.get_job_by_id_without_tasks(job_id)
        self.assertEqual(rebuilt_job.name, job_name)
        self.assertEqual(rebuilt_job.comments, job_comments)
        self.assertEqual(rebuilt_job.created_time, created_time)
        self.assertEqual(rebuilt_job.status, Status.Pending)

        # Rebuild the task object and check the contents of files
        task_id = tasks_id[0]
        rebuilt_task = self.manager.get_task_by_id(task_id)
        self.assertEqual(rebuilt_task.arguments, task_arguments)
        self.assertEqual(rebuilt_task.tool_type, task_tool_type)
        self.assertEqual(rebuilt_task.status, Status.Pending)

        # Remove the inserted job & task after test
        self.manager.remove_job_by_id(job_id)
        self.manager.remove_tasks_by_job_id(job_id)
    
    def test_save_result(self):
        # Create a sample task
        task_arguments = {
            "-j": "output.json",
            "-F": "facts",
            "-R": "results",
            "-f": "oo.exe",
        }
        task_tool_type = 0
        new_task = Task({}, task_tool_type, task_arguments)

        # Create a sample job
        job_name = "Test_job"
        job_comments = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comments, created_time)
        new_job.tasks = [new_task]

        # Insert the sample job with the sample task
        job_id, tasks_id = self.manager.insert_new_job(new_job)

        # Save the result of the task
        task_id = tasks_id[0]
        stdout = b"sample stdout"
        stderr = b"sample stderr"
        output_file_list = ["../../sample_output/output.json"]
        log_file_list = ["../../sample_output/facts", "../../sample_output/results"]

        self.manager.save_result(task_id, output_file_list, log_file_list, stdout, stderr)

        # Rebuild the task object and check the contents of files
        rebuilt_task = self.manager.get_task_by_id(task_id)
        self.assertEqual(rebuilt_task.arguments, task_arguments)
        self.assertEqual(rebuilt_task.tool_type, task_tool_type)
        with open("../../sample_output/output.json", "rb") as f:
            output_json_bytes = f.read()
        with open("../../sample_output/facts", "rb") as f:
            facts_bytes = f.read()
        with open("../../sample_output/results", "rb") as f:
            results_bytes = f.read()
        self.assertEqual(rebuilt_task.output["output.json"], output_json_bytes)
        self.assertEqual(rebuilt_task.log["facts"], facts_bytes)
        self.assertEqual(rebuilt_task.log["results"], results_bytes)
        self.assertEqual(rebuilt_task.stdout, stdout)
        self.assertEqual(rebuilt_task.stderr, stderr)
        self.assertEqual(rebuilt_task.status, Status.Pending)

        # Remove the inserted job & task after test
        self.manager.remove_job_by_id(job_id)
        self.manager.remove_tasks_by_job_id(job_id)
    
    def test_update_task_status(self):
        # Create a sample task
        task_arguments = {
            "-j": "output.json",
            "-F": "facts",
            "-R": "results",
            "-f": "oo.exe",
        }
        task_tool_type = 0
        new_task = Task({}, task_tool_type, task_arguments)

        # Create a sample job
        job_name = "Test_job"
        job_comments = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comments, created_time)
        new_job.tasks = [new_task]

        # Insert the sample job with the sample task
        job_id, tasks_id = self.manager.insert_new_job(new_job)
        task_id = tasks_id[0]

        # Update the status
        self.manager.update_job_status(job_id, Status.Failed)
        self.manager.update_task_status(task_id, Status.Successful)

        # Rebuild the job object and check the status
        rebuilt_job = self.manager.get_job_by_id_without_tasks(job_id)
        self.assertEqual(rebuilt_job.status, Status.Failed)

        # Rebuild the task object and check the status
        rebuilt_task = self.manager.get_task_by_id(task_id)
        self.assertEqual(rebuilt_task.status, Status.Successful)

        # Remove the inserted job & task after test
        self.manager.remove_job_by_id(job_id)
        self.manager.remove_tasks_by_job_id(job_id)

if __name__ == '__main__':
    unittest.main()
