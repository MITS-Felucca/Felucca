import base64
import filecmp
import json
import os
import shutil
import sys
import time
import unittest
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend/common'))
from common.job import Job
from common.status import Status
from common.task import Task
from resource_manager import ResourceManager
from job_manager import JobManager

class TestJobManager(unittest.TestCase):
    def setUp(self):
        # Use "test" database for unit tests instead of "felucca"
        self.resource_manager = ResourceManager("test")
        self.job_manager = JobManager()
    
    def test_job_status(self):
        self.resource_manager.remove_all_jobs_and_tasks()

        # Create a job with two tasks
        task_json = {
                "Files": {},
                "Program_Name": "ooanalyzer",
                "Input_File_Args": {
                    "-f": "oo.exe"
                },
                "Input_Text_Args": {
                    "--timeout": "300"
                },
                "Input_Flag_Args": [
                    "-v"],
                "Output_File_Args": {
                    "-j": "output.json",
                    "-F": "facts",
                    "-R": "results"
                }
        }
        input_json = {
            "Job_Name": "dump_job",
            "Job_Comment": "this is the test json input for job manager",
            "Tasks": [task_json, task_json, task_json]
        }
        job = self.resource_manager.save_new_job_and_tasks(input_json)
        print(Job.to_json(job))
        job_id = job.job_id

        # Initialize the metadata in JM
        self.job_manager.initialize_job(job)
        job = self.resource_manager.get_job_by_id(job_id)
        self.assertEqual(job.status, Status.Running)

        # Finish all tasks
        for task in job.tasks:
            task_id = task.task_id
            self.resource_manager.update_task_status(task_id, Status.Successful)
            self.job_manager.finish_task(task_id)

        job = self.resource_manager.get_job_by_id(job_id)
        self.assertEqual(job.status, Status.Finished)

if __name__ == '__main__':
    # Not finished yet, don't run
    unittest.main()
