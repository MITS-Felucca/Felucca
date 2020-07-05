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

class TestResourceManager(unittest.TestCase):
    def setUp(self):
        # Use "test" database for unit tests instead of "felucca"
        self.manager = ResourceManager("test")

    def test_insert_job_without_tasks(self):
        # Remove previous jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

        # Create a sample job
        job_name = "Test_job"
        job_comment = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comment, created_time)
        new_job.tasks = []
        job_id, tasks_id = self.manager.insert_new_job(new_job)

        # Check job_id & tasks_id
        self.assertTrue(isinstance(job_id, str))
        self.assertEqual(len(tasks_id), 0)

        # Remove the nanoseconds in created_time as the precision in MongoDB doesn't store nanoseconds
        ms_without_ns = int(created_time.microsecond / 1000) * 1000
        created_time = created_time.replace(microsecond=ms_without_ns)

        # Rebuild the job object and check the contents
        rebuilt_job = self.manager.db_manager.get_job_by_id_without_tasks(job_id)
        self.assertEqual(rebuilt_job.name, job_name)
        self.assertEqual(rebuilt_job.comment, job_comment)
        self.assertEqual(rebuilt_job.created_time, created_time)
        self.assertEqual(rebuilt_job.status, Status.Pending)

        # Remove the inserted job after test
        self.manager.remove_all_jobs_and_tasks()

    def test_insert_job_with_single_task(self):
        # Remove previous jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

        # Create a sample task
        program_name = "ooanalyzer"
        input_file_args = {
            "-f": "oo.exe"
        }
        input_text_args = {
                "--timeout": "300"
        }
        input_flag_args = [
            "-v",
        ]
        output_file_args = {
            "-j": "output.json",
            "-F": "facts",
            "-R": "results"
        }
        new_task = Task()
        new_task.program_name = program_name
        new_task.input_file_args = input_file_args
        new_task.input_text_args = input_text_args
        new_task.input_flag_args = input_flag_args
        new_task.output_file_args = output_file_args

        # Create a sample job
        job_name = "Test_job"
        job_comment = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comment, created_time)
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
        rebuilt_job = self.manager.db_manager.get_job_by_id_without_tasks(job_id)
        self.assertEqual(rebuilt_job.name, job_name)
        self.assertEqual(rebuilt_job.comment, job_comment)
        self.assertEqual(rebuilt_job.created_time, created_time)
        self.assertEqual(rebuilt_job.status, Status.Pending)

        # Rebuild the task object and check the contents of files
        task_id = tasks_id[0]
        rebuilt_task = self.manager.db_manager.get_task_by_id(task_id)
        self.assertEqual(rebuilt_task.input_file_args, input_file_args)
        self.assertEqual(rebuilt_task.input_text_args, input_text_args)
        self.assertEqual(rebuilt_task.input_flag_args, input_flag_args)
        self.assertEqual(rebuilt_task.output_file_args, output_file_args)
        self.assertEqual(rebuilt_task.status, Status.Pending)

        # Remove the inserted job & task after test
        self.manager.remove_all_jobs_and_tasks()

    def test_save_result(self):
        # Remove previous jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

        # Create a sample task
        program_name = "ooanalyzer"
        input_file_args = {
            "-f": "oo.exe"
        }
        input_text_args = {
                "--timeout": "300"
        }
        input_flag_args = [
            "-v",
        ]
        output_file_args = {
            "-j": "output.json",
            "-F": "facts",
            "-R": "results"
        }
        new_task = Task()
        new_task.program_name = program_name
        new_task.input_file_args = input_file_args
        new_task.input_text_args = input_text_args
        new_task.input_flag_args = input_flag_args
        new_task.output_file_args = output_file_args

        # Create a sample job
        job_name = "Test_job"
        job_comment = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comment, created_time)
        new_job.tasks = [new_task]

        # Insert the sample job with the sample task
        job_id, tasks_id = self.manager.insert_new_job(new_job)

        # Save the result of the task
        task_id = tasks_id[0]
        stdout = "sample stdout"
        stderr = "sample stderr"
        output_file_list = ["../../sample_output/output.json", "../../sample_output/facts", "../../sample_output/results"]
        log_file_list = ["../../sample_output/facts", "../../sample_output/results"]

        self.manager.save_result(task_id, output_file_list, stdout, stderr)
        self.manager.update_stdout(task_id, stdout)
        self.manager.update_stderr(task_id, stderr)

        # Rebuild the task object and check the contents of files
        rebuilt_task = self.manager.db_manager.get_task_by_id(task_id)

        with open("../../sample_output/output.json", "rb") as f:
            output_json_bytes = f.read().decode('utf-8')
        with open("../../sample_output/facts", "rb") as f:
            facts_bytes = f.read().decode('utf-8')
        with open("../../sample_output/results", "rb") as f:
            results_bytes = f.read().decode('utf-8')
        self.assertEqual(self.manager.get_output_file(task_id, "output.json"), output_json_bytes)
        self.assertEqual(self.manager.get_output_file(task_id, "facts"), facts_bytes)
        self.assertEqual(self.manager.get_output_file(task_id, "results"), results_bytes)

        self.assertEqual(self.manager.get_stdout(task_id), stdout)
        self.assertEqual(self.manager.get_stderr(task_id), stderr)

        self.assertEqual(rebuilt_task.output, ["output.json", "facts", "results"])
        self.assertEqual(rebuilt_task.status, Status.Pending)

        new_stdout = "New stdout"
        new_stderr = "New stderr"
        # self.manager.update_stdout_and_stderr(task_id, new_stdout, new_stderr)
        self.manager.update_stdout(task_id, new_stdout)
        self.manager.update_stderr(task_id, new_stderr)
        self.assertEqual(self.manager.get_stdout(task_id), stdout + new_stdout)
        self.assertEqual(self.manager.get_stderr(task_id), stderr + new_stderr)

        # Remove the inserted job & task after test
        self.manager.remove_all_jobs_and_tasks()

    def test_update_status(self):
        # Remove previous jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

        # Create a sample task
        program_name = "ooanalyzer"
        input_file_args = {
            "-f": "oo.exe"
        }
        input_text_args = {
                "--timeout": "300"
        }
        input_flag_args = [
            "-v",
        ]
        output_file_args = {
            "-j": "output.json",
            "-F": "facts",
            "-R": "results"
        }
        new_task = Task()
        new_task.program_name = program_name
        new_task.input_file_args = input_file_args
        new_task.input_text_args = input_text_args
        new_task.input_flag_args = input_flag_args
        new_task.output_file_args = output_file_args

        # Create a sample job
        job_name = "Test_job"
        job_comment = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comment, created_time)
        new_job.tasks = [new_task]

        # Insert the sample job with the sample task
        job_id, tasks_id = self.manager.insert_new_job(new_job)
        task_id = tasks_id[0]

        # Update the status
        self.manager.update_job_status(job_id, Status.Failed)
        self.manager.update_task_status(task_id, Status.Successful)

        # Rebuild the job object and check the status
        rebuilt_job = self.manager.db_manager.get_job_by_id_without_tasks(job_id)
        self.assertEqual(rebuilt_job.status, Status.Failed)

        # Rebuild the task object and check the status
        rebuilt_task = self.manager.db_manager.get_task_by_id(task_id)
        self.assertEqual(rebuilt_task.status, Status.Successful)

        # Remove the inserted job & task after test
        self.manager.remove_all_jobs_and_tasks()

    def test_get_all_jobs_without_tasks(self):
        # Remove previous jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

        # Create and insert three sample jobs
        job_list = []
        for i in range(3):
            job_name = "Test_job%d" % i
            job_comment = "Just for test%d" % i
            created_time = datetime.now()
            created_time = created_time.replace(microsecond=0)
            new_job = Job(job_name, job_comment, created_time)
            new_job.tasks = []
            job_list.append(new_job)
            self.manager.insert_new_job(new_job)

        rebuilt_jobs = self.manager.db_manager.get_all_jobs_without_tasks()
        for i in range(3):
            original_job = job_list[i]
            rebuilt_job = rebuilt_jobs[i]
            self.assertEqual(original_job.name, rebuilt_job.name)
            self.assertEqual(original_job.comment, rebuilt_job.comment)
            self.assertEqual(original_job.created_time, rebuilt_job.created_time)
            self.assertEqual(original_job.status, rebuilt_job.status)

        # Remove the inserted jobs
        self.manager.remove_all_jobs_and_tasks()

    def test_get_output_and_log_file(self):
        # Remove previous jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

        # Create a sample task
        program_name = "ooanalyzer"
        input_file_args = {
            "-f": "oo.exe"
        }
        input_text_args = {
                "--timeout": "300"
        }
        input_flag_args = [
            "-v",
        ]
        output_file_args = {
            "-j": "output.json",
            "-F": "facts",
            "-R": "results"
        }
        new_task = Task()
        new_task.program_name = program_name
        new_task.input_file_args = input_file_args
        new_task.input_text_args = input_text_args
        new_task.input_flag_args = input_flag_args
        new_task.output_file_args = output_file_args

        # Create a sample job
        job_name = "Test_job"
        job_comment = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comment, created_time)
        new_job.tasks = [new_task]

        # Insert the sample job with the sample task
        job_id, tasks_id = self.manager.insert_new_job(new_job)

        # Save the result of the task
        task_id = tasks_id[0]
        stdout = "sample stdout"
        stderr = "sample stderr"
        output_file_list = ["../../sample_output/output.json", "../../sample_output/facts", "../../sample_output/results"]

        self.manager.save_result(task_id, output_file_list, stdout, stderr)
        self.manager.update_stdout(task_id, stdout)
        self.manager.update_stderr(task_id, stderr)

        # Retrive the output file
        file = self.manager.get_output_file(task_id, "output.json")
        with open("../../sample_output/output.json", "rb") as f:
            output_json = f.read()
        self.assertEqual(file.encode('utf-8'), output_json)

        # Retrive the log files
        facts_file = self.manager.get_output_file(task_id, "facts")
        results_file = self.manager.get_output_file(task_id, "results")
        with open("../../sample_output/facts", "rb") as f:
            facts = f.read()
        with open("../../sample_output/results", "rb") as f:
            results = f.read()
        self.assertEqual(facts_file.encode('utf-8'), facts)
        self.assertEqual(results_file.encode('utf-8'), results)

        # Retrive stdout & stderr
        self.assertEqual(self.manager.get_stdout(task_id), stdout)
        self.assertEqual(self.manager.get_stderr(task_id), stderr)

        # Remove the inserted jobs
        self.manager.remove_all_jobs_and_tasks()

    def test_save_new_job_and_tasks(self):
        # Remove previous jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

        # Read the input json and store it
        with open("../../sample_output/input.json", "r") as f:
            input_json = json.loads(f.read())
        job = self.manager.save_new_job_and_tasks(input_json)

        # Check the job attributes
        self.assertEqual(job.name, input_json["Job_Name"])
        self.assertEqual(job.comment, input_json["Job_Comment"])

        # Check the task attributes
        task = job.tasks[0]
        task_json = input_json["Tasks"][0]
        self.assertEqual(task.input_file_args, task_json["Input_File_Args"])
        self.assertEqual(task.input_text_args, task_json["Input_Text_Args"])
        self.assertEqual(task.input_flag_args, task_json["Input_Flag_Args"])
        self.assertEqual(task.output_file_args, task_json["Output_File_Args"])

        # Check the stored file
        for param, path in task.files.items():
            with open(path, "rb") as f:
                saved_file = f.read()
            self.assertEqual(saved_file, base64.b64decode(task_json["Files"][param].encode('utf-8')))
            # self.assertEqual(saved_file, bytes.fromhex(task_json["Files"][filename]))
            os.remove(path)

        # Remove the directory
        os.rmdir(os.path.join("/tmp/Felucca", task.task_id))

    def test_job_list(self):
        # Remove previous jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

        # Read the input json and store it
        with open("../../sample_output/input.json", "r") as f:
            input_json = json.loads(f.read())
        job = self.manager.save_new_job_and_tasks(input_json)

        # Build the job json
        job_dict = {
            "Name": job.name,
            "Comment": job.comment,
            "Created_Time": time.mktime(job.created_time.timetuple()),
            "Finished_Time": 0,
            "Task_Number": 1,
            "Status": job.status.name,
            "ID": job.job_id,
            "Tasks": [],
        }

        job_list = self.manager.get_job_list()
        self.assertEqual(job_list, [job_dict])

        # Remove all jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

    def test_get_job_info(self):
        # Remove previous jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

        # Read the input json and store it
        with open("../../sample_output/input.json", "r") as f:
            input_json = json.loads(f.read())
        job = self.manager.save_new_job_and_tasks(input_json)

        # Save the result of the task
        task_id = job.tasks[0].task_id
        stdout = "sample stdout"
        stderr = ""
        output_file_list = ["../../sample_output/output.json", "../../sample_output/facts", "../../sample_output/results"]
        self.manager.save_result(task_id, output_file_list, stdout, stderr)
        self.manager.update_stdout(task_id, stdout)
        self.manager.update_stderr(task_id, stderr)

        # Mark task as finished
        self.manager.mark_task_as_finished(task_id)

        job_info = self.manager.get_job_info(job.job_id)

        # Build the task json
        task_dict = {
            "Program_Name": "ooanalyzer",
            "Arguments": {
                "-f": "oo.exe",
                "--timeout": "300",
                "-v": "",
                "-j": "output.json",
                "-F": "facts",
                "-R": "results"
            },
            'Output': ['output.json', 'facts', 'results'],
            'Stdout': True,
            'Stderr': False,
            'Finished_Time': job_info["Tasks"][0]["Finished_Time"],
            'Status': Status.Successful.name,
            'ID': job_info["Tasks"][0]["ID"],
        }

        # Build the job json
        job_dict = {
            "Name": job.name,
            "Comment": job.comment,
            "Created_Time": time.mktime(job.created_time.timetuple()),
            "Finished_Time": 0,
            "Task_Number": 1,
            "Status": job.status.name,
            "ID": job.job_id,
            "Tasks": [task_dict],
        }

        self.assertEqual(job_info, job_dict)

        # Remove all jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

    def test_tool(self):
        self.manager.remove_all_tools()

        # Insert a sample schema
        with open("/vagrant/felucca/backend/pharos_schema/ooanalyzer.json") as f:
            schema_json = json.loads(f.read())
        self.manager.db_manager.insert_new_tool(schema_json)

        tool_list = self.manager.get_all_tools()

        rebuild_schema = tool_list[0]
        self.assertIsNotNone(rebuild_schema['Tool_ID'])
        schema_json['Tool_ID'] = rebuild_schema['Tool_ID']
        self.assertEqual(rebuild_schema, schema_json)

        rebuild_schema_by_get = self.manager.get_tool_by_id(
            schema_json['Tool_ID'])
        self.assertEqual(rebuild_schema_by_get, schema_json)

        # Remove the inserted sample
        self.manager.remove_tool_by_id(schema_json['Tool_ID'])

        # Initialize Pharos tools
        self.manager.initialize_pharos_tools('/vagrant/felucca/backend/pharos_schema')

        tool_list = self.manager.get_all_tools()

        self.assertGreater(len(tool_list), 0)
        self.manager.remove_all_tools()

    def test_failure(self):
        # Remove previous jobs & tasks
        self.manager.remove_all_jobs_and_tasks()

        # Create a sample task
        program_name = "ooanalyzer"
        input_file_args = {
            "-f": "oo.exe"
        }
        input_text_args = {
                "--timeout": "300"
        }
        input_flag_args = [
            "-v",
        ]
        output_file_args = {
            "-j": "output.json",
            "-F": "facts",
            "-R": "results"
        }
        new_task = Task()
        new_task.program_name = program_name
        new_task.input_file_args = input_file_args
        new_task.input_text_args = input_text_args
        new_task.input_flag_args = input_flag_args
        new_task.output_file_args = output_file_args

        # Create a sample job
        job_name = "Test_job"
        job_comment = "Just for test"
        created_time = datetime.now()
        new_job = Job(job_name, job_comment, created_time)
        new_job.tasks = [new_task]

        # Insert the sample job with the sample task
        job_id, tasks_id = self.manager.insert_new_job(new_job)

        # Create a empty directory & Generate two of the files
        dir_path = "/tmp/Felucca/unit_test/test"
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path)
        output_file_path = os.path.join(dir_path, "output.json")
        results_file_path = os.path.join(dir_path, "results")
        facts_file_path = os.path.join(dir_path, "facts")
        output_content = "{}"
        results_content = "test result content"
        with open(output_file_path, 'w+') as f:
            f.write(output_content)
        with open(results_file_path, 'w+') as f:
            f.write(results_content)

        # Save the result of the task
        task_id = tasks_id[0]
        stdout = None
        stderr = "sample stderr"
        output_file_list = [output_file_path, results_file_path, facts_file_path]

        self.manager.save_result(task_id, output_file_list, stdout, stderr)
        self.manager.update_stdout(task_id, stdout)
        self.manager.update_stderr(task_id, stderr)

        # Rebuild the task object and check the contents of files
        rebuilt_task = self.manager.db_manager.get_task_by_id(task_id)
        self.assertEqual(rebuilt_task.output, ["output.json", "results"])

        retrieved_stdout = self.manager.get_stdout(task_id)
        retrieved_stderr = self.manager.get_stderr(task_id)
        self.assertEqual(retrieved_stdout, stdout)
        self.assertEqual(retrieved_stderr, stderr)

        # Remove the directory & inserted tasks
        shutil.rmtree(dir_path)
        self.manager.remove_all_jobs_and_tasks()
if __name__ == '__main__':
    unittest.main()
