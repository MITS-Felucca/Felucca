import datetime
import gridfs
import os
import pymongo
from bson import ObjectId
from datetime import datetime
from common.job import Job
from common.status import Status
from common.task import Task
from logger import Logger

class ResourceManager(object):
    """ResourceManager is responsible for accessing data in database.
    """
    
    def __setup(self):
        """Initialize the connections to the MongoDB server
        """

        self.__client = pymongo.MongoClient()
        self.__db = self.__client.felucca
        self.__jobs_collection = self.__db.jobs
        self.__tasks_collection = self.__db.tasks
        self.__fs = gridfs.GridFS(self.__db)

    def __insert_new_task(self, job_id, new_task):
        """Insert a task into the database

        Args:
            job_id (ObjectId): The id of the parent job
            new_task (Task): The task which will be inserted
        
        Returns:
            task_id (String): The id of the newly inserted task
        """

        # Build the new task
        logger = Logger().get
        
        new_task_dict = {
            "tool_type": 0,
            "command_line_input": new_task.command_line_input,
            "job_id": job_id,
            "output_files": {},
            "log_files": {},
            "stdout": "",
            "stderr": "",
            "status": new_task.status.value,
            "finished_time": new_task.finished_time,
        }

        # Insert the new task
        result = self.__tasks_collection.insert_one(new_task_dict)
        task_id = result.inserted_id
        logger.debug(f"insert the new task:{task_id}")
        # Don't cast id to String for internal use
        return task_id

    def insert_new_job(self, new_job):
        """Insert a job with its tasks into the database

        Args:
            new_job (Job): The job which will be inserted

        Returns:
            job_id (String): The id of the newly inserted job
            tasks_id (List of String): A list of ids according to the tasks of the job, where the order remains the same
        """
        logger = Logger().get
        logger.debug(f"receive new job{new_job} in insert_new_job")
        self.__setup()
        
        # Build the new job
        new_job_dict = {
            "name": new_job.name,
            "comments": new_job.comments,
            "created_time": new_job.created_time,
            "finished_time": new_job.finished_time,
            "status": new_job.status.value,
        }

        # Insert the new job
        result = self.__jobs_collection.insert_one(new_job_dict)
        job_id = result.inserted_id

        # Insert the related tasks
        tasks_id = []
        for task in new_job.tasks:
            task_id = self.__insert_new_task(job_id, task)
            tasks_id.append(str(task_id))
        
        return str(job_id), tasks_id

    def save_result(self, task_id, output, log, stdout, stderr):
        """Save the result of the task specified by task_id

        Args:
            task_id (String): The id of the specific task
            output (List of String): Each entry in output is the path of an output file
            log (List of String): Each entry in log is the path of an log file
            stdout (String): The stdout of the task
            stderr (String): The stderr of the task
        """
        logger = Logger().get
        logger.debug(f"start save_result task_id:{task_id}, output:{output}, log:{log}, stdout:{stdout}, stderr:{stderr}")
        
        
        self.__setup()
        try:
            # Cast task_id from String to ObjectId first
            task_id = ObjectId(task_id)
    
            # Insert all files into gridfs
            output_dict = {}
            for output_file_path in output:
                with open(output_file_path, "rb") as f:
                    file_id = self.__fs.put(f)
                filename = os.path.basename(os.path.normpath(output_file_path))
                output_dict[filename] = file_id
    
            log_dict = {}
            for log_file_path in log:
                with open(log_file_path, "rb") as f:
                    file_id = self.__fs.put(f)
                filename = os.path.basename(os.path.normpath(log_file_path))
                log_dict[filename] = file_id
    
            condition = {"_id": task_id}
            task = self.__tasks_collection.find_one(condition)
            task["output_files"] = output_dict
            task["log_files"] = log_dict
            task["stdout"] = stdout
            task["stderr"] = stderr
            task["is_finished"] = True
            update_result = self.__tasks_collection.update_one(condition, {"$set": task})
            if update_result.modified_count != 1:
                logger.error(f"save result failed")
            pass
        except Exception as e:
            logger.error(f"something wrong in save_result, Exception: {e}")

    
    def update_job_status(self, job_id, new_status):
        """Update the status of a job

        Arg:
            job_id (String): the id of the job
            new_status (Status): the new status of the job
        """
        logger = Logger().get
        logger.debug(f"start update_job_status")
        self.__setup()
        try:
            condition = {"_id": ObjectId(job_id)}
            job = self.__jobs_collection.find_one(condition)
            job["status"] = new_status.value
            update_result = self.__jobs_collection.update_one(condition, {"$set": job})
            if update_result.modified_count != 1:
                raise Exception("update_result.modified_count != 1")
            pass
        except Exception as e:
            logger.error(f"something wrong in update_job_status, Exception: {e}")
            
    
    def update_task_status(self, task_id, new_status):
        """Update the status of a task

        Arg:
            task_id (String): the id of the task
            new_status (Status): the new status of the task
        """
        logger = Logger().get
        logger.debug(f"start update_task_status, task_id:{task_id}, new_status:{new_status}")
        self.__setup()
        try:
            condition = {"_id": ObjectId(task_id)}
            task = self.__tasks_collection.find_one(condition)
            task["status"] = new_status.value
            update_result = self.__tasks_collection.update_one(condition, {"$set": task})
            if update_result.modified_count != 1:
                raise Exception("update_result.modified_count != 1")
            pass
        except Exception as e:
            logger.error(f"something wrong in update_task_status, Exception: {e}")

    def get_task_by_id(self, task_id):
        """Return a Task object of the specific task

        Arg:
            task_id (String): the id of the specific task
        
        Return:
            task: the Task object of the specific id
        """
        logger = Logger().get
        logger.debug(f"start get_task_by_id, task_id:{task_id}")
        self.__setup()
        try:
            # Find the task using id
            condition = {"_id": ObjectId(task_id)}
            task_doc = self.__tasks_collection.find_one(condition)
    
            # Retrieve the output files and log files
            output_dict = {}
            for filename, file_id in task_doc["output_files"].items():
                output_file = self.__fs.get(file_id).read()
                output_dict[filename] = output_file
            log_dict = {}
            for filename, file_id in task_doc["log_files"].items():
                log_file = self.__fs.get(file_id).read()
                log_dict[filename] = log_file
            
            # Rebuild the Task object from the query result
            task = Task(None, task_doc["tool_type"], task_doc["command_line_input"])
            task.job_id = task_doc["job_id"]
            task.task_id = task_id
            task.output = output_dict
            task.log = log_dict
            task.stdout = task_doc["stdout"]
            task.stderr = task_doc["stderr"]
            task.status = Status(task_doc["status"])
            logger.debug(f"get_task_by_id successfully, task_id:{task_id}")
            return task
        except Exception as e:
            logger.error(f"something wrong in get_task_by_id, Exception: {e}")
        
    
    def get_job_by_id_without_tasks(self, job_id):
        """Return a Job object of the specific job

        The member tasks of the job will be empty to simplify the process.
        Use get_tasks_by_job_id instead to get the related tasks.

        Arg:
            job_id (String): the id of the specific job
        
        Return:
            job (Job): the Job object of the specific id
        """
        logger = Logger().get
        logger.debug(f"start get_job_by_id_without_tasks, job_id:{job_id}")
        self.__setup()
        try:
            # Find the job using id
            condition = {"_id": ObjectId(job_id)}
            job_doc = self.__jobs_collection.find_one(condition)
    
            # Rebuild the Job object from the query result
            job = Job(job_doc["name"], job_doc["comments"], job_doc["created_time"], status=Status(job_doc["status"]))
    
            return job
        except Exception as e:
            logger.error(f"something wrong in get_job_by_id_without_tasks, Exception: {e}")
    
    def get_tasks_by_job_id(self, job_id):
        """Return all the tasks belonging to the specific job

        Arg:
            job_id (String): the id of the specific job
        
        Return:
            tasks: a list of Task objects
        """
        logger = Logger().get
        logger.debug(f"start get_tasks_by_job_id, job_id:{job_id}")
        self.__setup()
        try:
            # Get ids of all tasks using job_id
            condition = {"job_id": ObjectId(job_id)}
            field = {"_id": 1}
            tasks_doc_list = self.__tasks_collection.find(condition, field)
    
            # Rebuild all tasks into Task objects
            tasks_list = []
            for task_doc in tasks_doc_list:
                task = self.get_task_by_id(task_doc["_id"])
                tasks_list.append(task)
            logger.debug(f"Get ids of all tasks using job_id successfully, tasks_list:{tasks_list}")
            return tasks_list
        except Exception as e:
            logger.error(f"something wrong in get_tasks_by_job_id, Exception: {e}")
    
    def get_job_by_id(self, job_id):
        """Return a Job object of the specific job with all its tasks

        Arg:
            job_id (String): the id of the specific job
        
        Return:
            job (Job): the Job object of the specific id
        """
        logger = Logger().get
        logger.debug(f"start get_job_by_id, job_id:{job_id}")
        try:
            job = self.get_job_by_id_without_tasks(job_id)
            job.tasks = self.get_tasks_by_job_id(job_id)
    
            return job
        except Exception as e:
            logger.error(f"something wrong in get_job_by_id, Exception: {e}")
    
    def remove_job_by_id(self, job_id):
        """Remove the specific job (Used in unit tests)

        Arg:
            job_id (String): the id of the specific job
        """
        logger = Logger().get
        logger.debug(f"remove job by id, job_id:{job_id}")
        self.__setup()
        try:
            delete_result = self.__jobs_collection.delete_one({"_id": ObjectId(job_id)})
            return delete_result.deleted_count
        except Exception as e:
            logger.error(f"something wrong in remove_job_by_id, Exception: {e}")
            
    def remove_tasks_by_job_id(self, job_id):
        """Remove the tasks related to the specific job (Used in unit tests)

        Arg:
            task_id (String): the id of the specific task
        """
        logger = Logger().get
        logger.debug(f"remove tasks by id, job_id:{job_id}")
        self.__setup()
        try:
            delete_result = self.__tasks_collection.delete_many({"job_id": ObjectId(job_id)})
    
            return delete_result.deleted_count
        except Exception as e:
            logger.error(f"something wrong in remove_tasks_by_job_id, Exception: {e}")
