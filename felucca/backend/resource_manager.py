import datetime
import gridfs
import pymongo
from common.job import Job
from common.task import Task
from datetime import datetime

class ResourceManager(object):
    """ResourceManager is responsible for accessing data in database.
    """
    def setup(self):
        """Initialize the connections to the MongoDB server
        """

        self.client = pymongo.MongoClient()
        self.db = self.client.felucca
        self.jobs_collection = self.db.jobs
        self.tasks_collection = self.db.tasks
        self.fs = gridfs.GridFS(self.db)

    def __insert_new_task(self, job_id, new_task):
        """Insert a task into the database

        Args:
            job_id (ObjectId): The id of the parent job
            new_task (Task): The task which will be inserted
        
        Returns:
            task_id (ObjectId): The id of the newly inserted task
        """

        # TODO: Add executable_filename in task (TBD)
        # TODO: Use string for tool_type? So that we can easily display it to user (TBD)

        # Build the new task
        new_task_dict = {
            "tool_type": 0,
            "command_line_input": new_task.command_line_input,
            "job_id": job_id,
            "output_files": {},
            "log_files": {},
            "stdout": "",
            "stderr": "",
            "is_finished": False,
            "finished_time": None,
        }

        # Insert the new task
        result = self.tasks_collection.insert_one(new_task_dict)
        task_id = result.inserted_id

        return task_id

    def insert_new_job(self, new_job):
        """Insert a job with its tasks into the database

        Args:
            new_job (Job): The job which will be inserted

        Returns:
            job_id: The ObjectId of the newly inserted job
            tasks_id: A list of ids according to the tasks of the job, where the order remains the same
        """

        self.setup()

        # Build the new job
        new_job_dict = {
            "name": new_job.name,
            "comments": new_job.comments,
            "created_time": new_job.create_time,
            "finished_time": None,
            "is_finished": False,
        }

        # Insert the new job
        result = self.jobs_collection.insert_one(new_job_dict)
        job_id = result.inserted_id

        # Insert the related tasks
        tasks_id = []
        for task in new_job.tasks:
            task_id = self.__insert_new_task(job_id, task)
            tasks_id.append(task_id)
        
        return job_id, tasks_id

    def save_result(self, task_id, output, log, stdout, stderr):
        """Save the result of the task specified by task_id

        Args:
            task_id (ObjectId): The id of the specific task
            output (dict of mapping from string to bytes): Each entry in output is an output file with its name as the key
            log (dict of mapping from string to bytes): Each entry in log is an log file with its name as the key
            stdout (string): The stdout of the task
            stderr (string): The stderr of the task
        """
        
        self.setup()

        # Insert all files into gridfs
        output_dict = {}
        for filename, output_file in output.items():
            file_id = self.fs.put(output_file)
            output_dict[filename] = file_id
        log_dict = {}
        for filename, log_file in log.items():
            file_id = self.fs.put(log_file)
            log_dict[filename] = file_id

        condition = {"_id": task_id}
        task = self.tasks_collection.find_one(condition)
        task["output_files"] = output_dict
        task["log_files"] = log_dict
        task["stdout"] = stdout
        task["stderr"] = stderr
        task["is_finished"] = True
        update_result = self.tasks_collection.update_one(condition, {"$set": task})

        if update_result.modified_count is not 1:
            # TODO: Throw an exception when updating failed
            pass

    def get_task_by_id(self, task_id):
        """Return a Task object of the specific task

        Arg:
            task_id (ObjectId): the id of the specific task
        
        Return:
            task: the Task object of the specific id
        """

        self.setup()

        # Find the task using id
        condition = {"_id": task_id}
        task_doc = self.tasks_collection.find_one(condition)

        # Retrieve the output files and log files
        output_dict = {}
        for filename, file_id in task_doc["output_files"].items():
            output_file = self.fs.get(file_id).read()
            output_dict[filename] = output_file
        log_dict = {}
        for filename, file_id in task_doc["log_files"].items():
            log_file = self.fs.get(file_id).read()
            log_dict[filename] = log_file
        
        # Rebuild the task object from the query result
        task = Task(None, task_doc["tool_type"], task_doc["command_line_input"])
        task.job_id = task_doc["job_id"]
        task.task_id = task_id
        task.output = output_dict
        task.log = log_dict
        task.stdout = task_doc["stdout"]
        task.stderr = task_doc["stderr"]

        return task

    
    def remove_job_by_id(self, job_id):
        """Remove the specific job (Used in unit tests)
        """

        self.setup()
        
        delete_result = self.jobs_collection.delete_one({"_id": job_id})
        return delete_result.deleted_count
    
    def remove_tasks_by_job_id(self, job_id):
        """Remove the tasks related to the specific job (Used in unit tests)
        """

        self.setup()
        
        delete_result = self.tasks_collection.delete_many({"job_id": job_id})
        return delete_result.deleted_count
