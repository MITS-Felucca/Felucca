import os
import sys
import unittest
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend'))
from common.job import Job
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

        # Remove the nanoseconds in created_time as the precision in MongoDB doesn't store nanoseconds
        ms_without_ns = int(created_time.microsecond / 1000) * 1000
        created_time = created_time.replace(microsecond=ms_without_ns)

        # Query the sample job using id
        query_job = self.manager.jobs_collection.find_one({"_id": job_id})
        self.assertEqual(query_job["name"], job_name)
        self.assertEqual(query_job["comments"], job_comments)
        self.assertEqual(query_job["created_time"], created_time)

        # Remove the inserted job & task after test
        self.manager.remove_job_by_id(job_id)
        self.manager.remove_tasks_by_job_id(job_id)
    
    def test_insert_job_with_single_task(self):
        # Create a sample task
        task_command_line_input = "ooanalyzer -j output.json -F facts -R results -f oo.exe"
        task_tool_type = 0
        new_task = Task(None, task_tool_type, task_command_line_input)

        # Create a sample job
        job_name = "Test_job"
        job_comments = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comments, created_time)
        new_job.tasks = [new_task]
        job_id, tasks_id = self.manager.insert_new_job(new_job)

        # Remove the nanoseconds in created_time as the precision in MongoDB doesn't store nanoseconds
        ms_without_ns = int(created_time.microsecond / 1000) * 1000
        created_time = created_time.replace(microsecond=ms_without_ns)

        # Query the sample job using id
        query_job = self.manager.jobs_collection.find_one({"_id": job_id})
        self.assertEqual(query_job["name"], job_name)
        self.assertEqual(query_job["comments"], job_comments)
        self.assertEqual(query_job["created_time"], created_time)

        # Query the sample task using job_id
        query_task = self.manager.tasks_collection.find_one({"job_id": job_id})
        self.assertEqual(query_task["command_line_input"], task_command_line_input)
        self.assertEqual(query_task["tool_type"], task_tool_type)

        # Remove the inserted job & task after test
        self.manager.remove_job_by_id(job_id)
        self.manager.remove_tasks_by_job_id(job_id)
    
    def test_insert_job_with_single_task_and_save_result(self):
        # Create a sample task
        task_command_line_input = "ooanalyzer -j output.json -F facts -R results -f oo.exe"
        task_tool_type = 0
        new_task = Task(None, task_tool_type, task_command_line_input)

        # Create a sample job
        job_name = "Test_job"
        job_comments = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comments, created_time)
        new_job.tasks = [new_task]
        job_id, tasks_id = self.manager.insert_new_job(new_job)

        # Save the result of the task
        task_id = tasks_id[0]
        with open("../../sample_output/output.json", "rb") as f:
            output_json = f.read()
        with open("../../sample_output/facts", "rb") as f:
            facts = f.read()
        with open("../../sample_output/results", "rb") as f:
            results = f.read()
        stdout = b"sample stdout"
        stderr = b"sample stderr"
        output_file_dict = {
            "output.json": output_json,
        }
        log_file_dict = {
            "facts": facts,
            "results": results,
        }
        self.manager.save_result(task_id, output_file_dict, log_file_dict, stdout, stderr)

        # Remove the nanoseconds in created_time as the precision in MongoDB doesn't store nanoseconds
        ms_without_ns = int(created_time.microsecond / 1000) * 1000
        created_time = created_time.replace(microsecond=ms_without_ns)

        # Query the sample job using id
        query_job = self.manager.jobs_collection.find_one({"_id": job_id})
        self.assertEqual(query_job["name"], job_name)
        self.assertEqual(query_job["comments"], job_comments)
        self.assertEqual(query_job["created_time"], created_time)

        # Query the sample task using job_id
        query_task = self.manager.tasks_collection.find_one({"job_id": job_id})
        self.assertEqual(query_task["command_line_input"], task_command_line_input)
        self.assertEqual(query_task["tool_type"], task_tool_type)

        # Rebuild the task object and check the contents of files
        rebuilt_task = self.manager.get_task_by_id(task_id)
        self.assertEqual(rebuilt_task.output["output.json"], output_json)
        self.assertEqual(rebuilt_task.log["facts"], facts)
        self.assertEqual(rebuilt_task.log["results"], results)
        self.assertEqual(rebuilt_task.stdout, stdout)
        self.assertEqual(rebuilt_task.stderr, stderr)

        # Remove the inserted job & task after test
        self.manager.remove_job_by_id(job_id)
        self.manager.remove_tasks_by_job_id(job_id)

if __name__ == '__main__':
    unittest.main() 