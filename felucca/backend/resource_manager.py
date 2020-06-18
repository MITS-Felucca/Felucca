import base64
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

    def __init__(self, db_name="felucca"):
        self.db_name = "test"
        # self.db_name = db_name
        self.db_manager = self.DatabaseManager(self.db_name)

    def generate_sample_jobs(self):
        """Generate three sample jobs without tasks for job list test.
        """
        job_list = []
        for i in range(3):
            job_name = "Test_job%d" % i
            job_comment = "Just for test%d" % i
            created_time = datetime.now().replace(microsecond=0)
            new_job = Job(job_name, job_comment, created_time)
            new_job.tasks = []
            job_list.append(new_job)


        # Create two sample tasks for the first job
        task_arguments = {
            "-j": "output.json",
            "-F": "facts",
            "-R": "results",
            "-f": "oo.exe",
        }
        task_tool_type = 0
        task1 = Task({}, task_tool_type, task_arguments)
        task2 = Task({}, task_tool_type, task_arguments)
        job_list[0].tasks = [task1, task2]

        # Insert three jobs
        job_id, tasks_id = self.insert_new_job(job_list[0])
        self.insert_new_job(job_list[1])
        self.insert_new_job(job_list[2])

        # Save result to the 1st task of the 1st job
        stdout = "sample stdout"
        stderr = "sample stderr"
        output_file_list = ["/vagrant/tests/sample_output/output.json"]
        log_file_list = ["/vagrant/tests/sample_output/facts",
                         "/vagrant/tests/sample_output/results"]
        self.save_result(tasks_id[0], output_file_list, log_file_list,
                         stdout, stderr)

        # Update the status
        self.update_job_status(job_id, Status.Failed)
        self.update_task_status(tasks_id[1], Status.Failed)
        self.mark_task_as_finished(tasks_id[0])

    def get_all_jobs_without_tasks(self):
        """Return all jobs as Job objects without their tasks
        Return:
            job_list (List of Job): the Job objects
        """
        return self.db_manager.get_all_jobs_without_tasks()

    def get_all_jobs_with_tasks(self):
        """Return all jobs as Job objects with their tasks
        Return:
            job_list (List of Job): the Job objects
        """
        logger = Logger().get()
        logger.debug(f"start get_all_jobs_with_tasks")

        job_list = self.db_manager.get_all_jobs_without_tasks()
        for job in job_list:
            job.tasks = self.db_manager.get_tasks_by_job_id(job.job_id)
        return job_list

    def get_job_by_id(self, job_id):
        """Return a Job object of the specific job with all its tasks

        Arg:
            job_id (String): the id of the specific job

        Return:
            job (Job): the Job object of the specific id
        """
        logger = Logger().get()
        logger.debug(f"start get_job_by_id, job_id:{job_id}")
        try:
            job = self.db_manager.get_job_by_id_without_tasks(job_id)
            job.tasks = self.db_manager.get_tasks_by_job_id(job_id)

            return job
        except Exception as e:
            logger.error(f"something wrong in get_job_by_id, Exception: {e}")

    def get_job_info(self, job_id):
        """Return a json-dict of the specific job.

        Args:
            job_id (String): id of the job
        Return:
            job_dict (dict): the info of job
        """
        job = self.db_manager.get_job_by_id(job_id)
        job_dict = Job.to_json(job, True)
        return job_dict

    def get_job_list(self):
        """Return a list of job objects in json format.

        Return:
            job_list (list of dict): info of all jobs in database
        """
        logger = Logger().get()
        logger.debug("start get_job_list")

        job_object_list = self.get_all_jobs_with_tasks()

        job_list = []
        for job in job_object_list:
            job_list.append(Job.to_json(job))

        return job_list

    def get_log_file(self, task_id, filename):
        """Return an log file of a task

        Arg:
            task_id (String): the id of the task
            filename (String): the name of the file
        Return:
            file (String): the content of the file encoded by base64
                           & decoded by utf-8
        """
        return self.db_manager.get_log_file(task_id, filename)

    def get_output_file(self, task_id, filename):
        """Return an output file of a task

        Arg:
            task_id (String): the id of the task
            filename (String): the name of the file
        Return:
            file (String): the content of the file encoded by base64
                           & decoded by utf-8
        """
        return self.db_manager.get_output_file(task_id, filename)

    def insert_new_job(self, new_job):
        """Insert a job with its tasks into the database

        Args:
            new_job (Job): The job which will be inserted

        Returns:
            job_id (String): The id of the newly inserted job
            tasks_id (List of String): A list of ids according to the
                    tasks of the job, where the order remains the same
        """
        return self.db_manager.insert_new_job(new_job)

    def mark_job_as_finished(self, job_id):
        """Mark a job as "Successful" and update its "finished_time"
        Args:
            job_id (String): the id of the job
        """
        self.db_manager.mark_job_as_finished(job_id)
        return

    def mark_task_as_finished(self, task_id):
        """Mark a task as "Successful" and update its "finished_time"

        Args:
            task_id (String): the id of the task
        """
        self.db_manager.mark_task_as_finished(task_id)
        return

    def remove_all_jobs_and_tasks(self):
        """Remove all the jobs and tasks (Only used in unit tests)
        """
        self.db_manager.remove_all_jobs_and_tasks()
        return

    def save_new_job_and_tasks(self, new_job_dict):
        """Turn the newly submitted job with its tasks from dict to objects
        and save them
        The input files will be saved to a temporary directory named by task_id

        Args:
            new_job_dict (dict): the json file from Front-end
        Return:
            job (Job): built job instance with its tasks
        """
        logger = Logger().get()
        logger.debug("start save_new_job_and_tasks")

        # Build the job & task from json
        job = Job.from_json(new_job_dict)
        job.created_time = datetime.now().replace(microsecond=0)

        # Save the job & tasks
        # job_id, tasks_id = self.insert_new_job(job)
        job_id, tasks_id = self.db_manager.insert_new_job(job)
        job.job_id = job_id
        for i in range(len(job.tasks)):
            job.tasks[i].job_id = job_id
            job.tasks[i].task_id = tasks_id[i]

        # Save the input files of tasks
        for i in range(len(new_job_dict["Tasks"])):
            task = job.tasks[i]
            file_dict = {}

            # Create the unique directory for each task
            task_file_path = os.path.join("/tmp/Felucca", f"{task.task_id}")
            if not os.path.exists(task_file_path):
                try:
                    os.makedirs(task_file_path)
                except OSError as e:
                    logger.error(f"Failed to create directory {task_file_path}"
                                 f" with exception {e}")

            for filename, content in new_job_dict["Tasks"][i]["Files"].items():
                file_path = os.path.join("/tmp/Felucca", f"{task.task_id}"
                                         f"/{filename}")
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(content.encode('utf-8')))
                file_dict[filename] = file_path
            task.files = file_dict

        return job

    def save_result(self, task_id, output, log, stdout, stderr):
        """Save the result of the task specified by task_id

        Args:
            task_id (String): The id of the specific task
            output (List of String): Each entry is a path of an output file
            log (List of String): Each entry in log is the path of an log file
            stdout (String): The stdout of the task
            stderr (String): The stderr of the task
        """
        self.db_manager.save_result(task_id, output, log, stdout, stderr)
        return

    def update_job_status(self, job_id, new_status):
        """Update the status of a job

        Arg:
            job_id (String): the id of the job
            new_status (Status): the new status of the job
        """
        self.db_manager.update_job_status(job_id, new_status)
        return

    def update_task_status(self, task_id, new_status):
        """Update the status of a task

        Arg:
            task_id (String): the id of the task
            new_status (Status): the new status of the task
        """
        self.db_manager.update_task_status(task_id, new_status)
        return

    class DatabaseManager(object):
        def __init__(self, db_name="felucca"):
            super().__init__()
            self.db_name = db_name
            self.__client = pymongo.MongoClient()
            self.__db = self.__client[self.db_name]
            self.__jobs_collection = self.__db.jobs
            self.__tasks_collection = self.__db.tasks
            self.__fs = gridfs.GridFS(self.__db)

        def insert_new_task(self, job_id, new_task):
            """Insert a task into the database

            Args:
                job_id (ObjectId): The id of the parent job
                new_task (Task): The task which will be inserted

            Returns:
                task_id (String): The id of the newly inserted task
            """

            # Build the new task
            logger = Logger().get()

            new_task_dict = {
                "tool_type": 0,
                # "command_line_input": new_task.command_line_input,
                "arguments": new_task.arguments,
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
                tasks_id (List of String): A list of ids according to the
                        tasks of the job, where the order remains the same
            """

            # Build the new job
            new_job_dict = {
                "name": new_job.name,
                "comment": new_job.comment,
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
                task_id = self.insert_new_task(job_id, task)
                tasks_id.append(str(task_id))

            logger = Logger().get()
            logger.debug(f"insert new job{new_job} of id {str(job_id)}"
                          " in insert_new_job")

            return str(job_id), tasks_id

        def mark_job_as_finished(self, job_id):
            """Mark a job as "Successful" and update its "finished_time"
            Args:
                job_id (String): the id of the job
            """
            logger = Logger().get()
            logger.debug(f"start mark_job_as_finished for job {job_id}")

            try:
                condition = {"_id": ObjectId(job_id)}
                job = self.__jobs_collection.find_one(condition)
                job["status"] = Status.Successful.value
                job["finished_time"] = datetime.now().replace(microsecond=0)
                update_result = self.__jobs_collection.update_one(condition,
                                                                  {"$set": job})
                if update_result.modified_count != 1:
                    raise Exception("update_result.modified_count != 1")
                pass
            except Exception as e:
                logger.error(f"something wrong in mark_job_as_finished, "
                             f"Exception: {e}")

        def mark_task_as_finished(self, task_id):
            """Mark a task as "Successful" and update its "finished_time"

            Args:
                task_id (String): the id of the task
            """
            logger = Logger().get()
            logger.debug(f"start mark_task_as_finished for task {task_id}")

            try:
                # Find the target task
                condition = {"_id": ObjectId(task_id)}
                task = self.__tasks_collection.find_one(condition)

                # Update its status & finished time
                task["status"] = Status.Successful.value
                finished_time = datetime.now().replace(microsecond=0)
                task["finished_time"] = finished_time
                update_result = self.__tasks_collection.update_one(condition,
                                {"$set": task})
                if update_result.modified_count != 1:
                    raise Exception("update_result.modified_count != 1")
            except Exception as e:
                logger.error(f"something wrong in mark_task_as_finished, "
                             f"Exception: {e}")

        def save_result(self, task_id, output, log, stdout, stderr):
            """Save the result of the task specified by task_id

            Args:
                task_id (String): The id of the specific task
                output (List of String): Each entry is a path of an output file
                log (List of String): Each entry in log is the path of an log file
                stdout (String): The stdout of the task
                stderr (String): The stderr of the task
            """
            logger = Logger().get()
            logger.debug(f"start save_result task_id:{task_id}, output:{output}, "
                         f"log:{log}, stdout:{stdout}, stderr:{stderr}")

            try:
                # Cast task_id from String to ObjectId first
                task_id = ObjectId(task_id)

                # Insert all files into gridfs
                output_dict = {}
                for output_file_path in output:
                    with open(output_file_path, "r") as f:
                        file_id = self.__fs.put(f.read().encode("utf-8"))
                    filename = os.path.basename(os.path.normpath(output_file_path))
                    output_dict[filename] = file_id

                log_dict = {}
                for log_file_path in log:
                    with open(log_file_path, "r") as f:
                        file_id = self.__fs.put(f.read().encode("utf-8"))
                    filename = os.path.basename(os.path.normpath(log_file_path))
                    log_dict[filename] = file_id

                condition = {"_id": task_id}
                task = self.__tasks_collection.find_one(condition)
                task["output_files"] = output_dict
                task["log_files"] = log_dict
                task["stdout"] = stdout
                task["stderr"] = stderr
                task["is_finished"] = True
                update_result = self.__tasks_collection.update_one(condition,
                                                                   {"$set": task})
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
            logger = Logger().get()
            logger.debug(f"start update_job_status")

            try:
                condition = {"_id": ObjectId(job_id)}
                job = self.__jobs_collection.find_one(condition)
                job["status"] = new_status.value
                update_result = self.__jobs_collection.update_one(condition,
                                                                  {"$set": job})
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
            logger = Logger().get()
            logger.debug(f"start update_task_status, task_id:{task_id}, "
                         f"new_status:{new_status}")

            try:
                condition = {"_id": ObjectId(task_id)}
                task = self.__tasks_collection.find_one(condition)
                task["status"] = new_status.value
                update_result = self.__tasks_collection.update_one(condition,
                                                                   {"$set": task})
                if update_result.modified_count != 1:
                    raise Exception("update_result.modified_count != 1")
                pass
            except Exception as e:
                logger.error(f"something wrong in update_task_status,"
                             f" Exception: {e}")

        def get_job_by_id(self, job_id):
            """Return a Job object of the specific job with all its tasks

            Arg:
                job_id (String): the id of the specific job

            Return:
                job (Job): the Job object of the specific id
            """
            logger = Logger().get()
            logger.debug(f"start get_job_by_id, job_id:{job_id}")
            try:
                job = self.get_job_by_id_without_tasks(job_id)
                job.tasks = self.get_tasks_by_job_id(job_id)

                return job
            except Exception as e:
                logger.error(f"something wrong in get_job_by_id, Exception: {e}")

        def get_task_by_id(self, task_id):
            """Return a Task object of the specific task

            Arg:
                task_id (String): the id of the specific task

            Return:
                task: the Task object of the specific id
            """
            logger = Logger().get()
            logger.debug(f"start get_task_by_id, task_id:{task_id}")
            try:
                # Find the task using id
                condition = {"_id": ObjectId(task_id)}
                task_doc = self.__tasks_collection.find_one(condition)

                # Retrieve the output files and log files
                # Transform the dict into list of filenames
                output_list = []
                for filename in task_doc["output_files"].keys():
                    output_list.append(filename)
                log_list = []
                for filename in task_doc["log_files"].keys():
                    log_list.append(filename)

                # Rebuild the Task object from the query result
                task = Task({}, task_doc["tool_type"], task_doc["arguments"])
                task.job_id = str(task_doc["job_id"])
                task.task_id = task_id
                task.output = output_list
                task.log = log_list
                task.stdout = task_doc["stdout"]
                task.stderr = task_doc["stderr"]
                task.status = Status(task_doc["status"])
                task.finished_time = task_doc["finished_time"]
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
            logger = Logger().get()
            logger.debug(f"start get_job_by_id_without_tasks, job_id:{job_id}")
            try:
                # Find the job using id
                condition = {"_id": ObjectId(job_id)}
                job_doc = self.__jobs_collection.find_one(condition)

                # Rebuild the Job object from the query result
                job = Job(job_doc["name"], job_doc["comment"],
                          job_doc["created_time"], status=Status(job_doc["status"]))
                job.job_id = job_id

                return job
            except Exception as e:
                logger.error(f"something wrong in get_job_by_id_without_tasks,"
                             f" Exception: {e}")

        def get_tasks_by_job_id(self, job_id):
            """Return all the tasks belonging to the specific job

            Arg:
                job_id (String): the id of the specific job

            Return:
                tasks: a list of Task objects
            """
            logger = Logger().get()
            logger.debug(f"start get_tasks_by_job_id, job_id:{job_id}")
            try:
                # Get ids of all tasks using job_id
                condition = {"job_id": ObjectId(job_id)}
                field = {"_id": 1}
                tasks_doc_list = self.__tasks_collection.find(condition, field)

                # Rebuild all tasks into Task objects
                tasks_list = []
                tasks_id_list = []
                for task_doc in tasks_doc_list:
                    task = self.get_task_by_id(str(task_doc["_id"]))
                    tasks_list.append(task)
                    tasks_id_list.append(task.task_id)
                logger.debug(f"Get all tasks using job_id successfully,"
                             f" tasks_list:{tasks_id_list}")
                return tasks_list
            except Exception as e:
                logger.error(f"something wrong in get_tasks_by_job_id,"
                             f" Exception: {e}")

        def get_all_jobs_without_tasks(self):
            """Return all jobs as Job objects without their tasks

            Return:
                job_list (List of Job): the Job objects
            """
            logger = Logger().get()
            logger.debug(f"start get_all_jobs_without_tasks")

            # Get ids of all jobs
            field = {"_id": 1}
            all_job_ids = self.__jobs_collection.find(projection=field)

            # Rebuild all jobs
            job_list = []
            for job_doc in all_job_ids:
                # print(job_doc["_id"])
                job = self.get_job_by_id_without_tasks(str(job_doc["_id"]))
                job_list.append(job)

            return job_list

        def get_output_file(self, task_id, filename):
            """Return an output file of a task

            Arg:
                task_id (String): the id of the task
                filename (String): the name of the file
            Return:
                file (String): the content of the file encoded by base64
                               & decoded by utf-8
            """

            logger = Logger().get()
            logger.debug(f"start get_output_file {filename} from {task_id}")

            try:
                # Find the task using id
                condition = {"_id": ObjectId(task_id)}
                field = {"output_files": 1}
                task_doc = self.__tasks_collection.find_one(condition, field)
                if task_doc is None:
                    raise Exception(f"The task of {task_id} does not exist.")

                # Find the file in the task
                if filename not in task_doc["output_files"]:
                    raise Exception(f"The file named {filename} of task {task_id}"
                                     " does not exist.")
                file_id = task_doc["output_files"][filename]
                return self.__fs.get(file_id).read().decode('utf-8')
            except Exception as e:
                logger.error(e)
                return None

        def get_log_file(self, task_id, filename):
            """Return an log file of a task

            Arg:
                task_id (String): the id of the task
                filename (String): the name of the file
            Return:
                file (String): the content of the file encoded by base64
                               & decoded by utf-8
            """

            logger = Logger().get()
            logger.debug(f"start get_log_file {filename} from {task_id}")

            try:
                # Find the task using id
                condition = {"_id": ObjectId(task_id)}
                field = {"log_files": 1}
                task_doc = self.__tasks_collection.find_one(condition, field)
                if task_doc is None:
                    raise Exception(f"The task of {task_id} does not exist.")

                # Find the file in the task
                if filename not in task_doc["log_files"]:
                    raise Exception(f"The file named {filename} of task {task_id}"
                                     " does not exist.")
                file_id = task_doc["log_files"][filename]
                return self.__fs.get(file_id).read().decode('utf-8')
            except Exception as e:
                logger.error(e)
                return None

        def remove_job_by_id(self, job_id):
            """Remove the specific job (Used in unit tests)

            Arg:
                job_id (String): the id of the specific job
            """
            logger = Logger().get()
            logger.debug(f"remove job by id, job_id:{job_id}")
            if self.db_name != "test":
                logger.error("Cannot remove job unless current db is \"test\"!")
                return

            try:
                delete_result = self.__jobs_collection.delete_one(
                                     {"_id": ObjectId(job_id)})
                return delete_result.deleted_count
            except Exception as e:
                logger.error(f"something wrong in remove_job_by_id, Exception: {e}")

        def remove_tasks_by_job_id(self, job_id):
            """Remove the tasks related to the specific job (Used in unit tests)

            Arg:
                task_id (String): the id of the specific task
            """
            logger = Logger().get()
            logger.debug(f"remove tasks by id, job_id:{job_id}")
            if self.db_name != "test":
                logger.error("Cannot remove tasks unless current db is \"test\"!")
                return

            try:
                delete_result = self.__tasks_collection.delete_many(
                                     {"job_id": ObjectId(job_id)})

                return delete_result.deleted_count
            except Exception as e:
                logger.error(f"something wrong in remove_tasks_by_job_id,"
                             f" Exception: {e}")

        def remove_all_jobs_and_tasks(self):
            """Remove all the jobs and tasks (Only used in unit tests)
            """
            logger = Logger().get()
            logger.debug("remove all jobs and tasks")
            if self.db_name != "test":
                logger.error("Cannot remove all jobs and tasks unless current db"
                             " is \"test\"!")
                return

            try:
                # Get ids of all jobs
                field = {"_id": 1}
                all_job_ids = self.__jobs_collection.find(projection=field)

                # Remove all jobs & tasks
                for job_doc in all_job_ids:
                    self.remove_job_by_id(str(job_doc["_id"]))
                    self.remove_tasks_by_job_id(str(job_doc["_id"]))
            except Exception as e:
                logger.error(f"something wrong in remove_all_jobs, Exception: {e}")


