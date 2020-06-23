import base64
import datetime
import gridfs
import json
import os
import pymongo
import re
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

    def setup(self):
        self.db_manager.setup()

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

    def get_all_tools(self):
        """Return the schemas of all tools with id

        Returns:
            schema_list (List of dict): schemas of all tools with id
        """
        return self.db_manager.get_all_tools()

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

    def get_stderr(self, task_id):
        """Return the stderr of a task

        Args:
            task_id (String): the id of the task

        Return:
            stderr (String): the stderr
        """
        return self.db_manager.get_stderr(task_id)

    def get_stdout(self, task_id):
        """Return the stdout of a task

        Args:
            task_id (String): the id of the task

        Return:
            stdout (String): the stdout
        """
        return self.db_manager.get_stdout(task_id)

    def get_tool_by_id(self, tool_id):
        """Get the schema of the specific tool.

        Args:
            tool_id (String): The id of the tool

        Return:
            tool_dict (dict): The schema of the tool with id
        """
        return self.db_manager.get_tool_by_id(tool_id)

    def initialize_pharos_tools(self, schema_path='pharos_schema'):
        """Read and store the schemas of Pharos tools

        Args:
            schema_path (String): the directory of the schema files (Only for test)
        """
        logger = Logger().get()
        logger.debug("start initialize_pharos_tools")

        if self.db_manager.get_metadata_field("has_initialized_pharos") is True:
            tool_list = self.get_all_tools()
            print(f"{len(tool_list)} Pharos tools have been initialized. Skip this initialization.")
            logger.debug(f"{len(tool_list)} Pharos tools have been initialized. Skip this initialization.")
            return

        pharos_schema_path = schema_path

        schema_list = []
        for root, dirs, files in os.walk(pharos_schema_path):
            for filename in files:
                if not filename.endswith('.json'):
                    continue
                print(filename)
                path = os.path.join(root, filename)
                with open(path, 'r') as f:
                    schema_json = json.loads(f.read())
                schema_list.append(schema_json)

        for schema in schema_list:
            self.db_manager.insert_new_tool(schema)

        self.db_manager.set_metadata_field("has_initialized_pharos", True)

        print(f"{len(schema_list)} Pharos tools have been initialized.")
        logger.debug(f"{len(schema_list)} Pharos tools have been initialized.")

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

    def remove_all_tools(self):
        """Remove all tools (Only for collection "test")
        """
        self.db_manager.remove_all_tools()

    def remove_tool_by_id(self, tool_id):
        """Remove the tool with the specified id.

        Args:
            tool_id (String)): the id of the tool
        """
        self.db_manager.remove_tool_by_id(tool_id)

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

            for param, content in new_job_dict["Tasks"][i]["Files"].items():
                filename = new_job_dict["Tasks"][i]["Input_File_Args"][param]
                file_path = os.path.join("/tmp/Felucca", f"{task.task_id}"
                                         f"/{filename}")
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(content.encode('utf-8')))
                file_dict[param] = file_path
            task.files = file_dict

        return job

    def save_result(self, task_id, output, stdout, stderr):
        """Save the result of the task specified by task_id

        Args:
            task_id (String): The id of the specific task
            output (List of String): Each entry is a path of an output file
            stdout (String): The stdout of the task
            stderr (String): The stderr of the task
        """
        self.db_manager.save_result(task_id, output, stdout, stderr)
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
            self.__tools_collection = self.__db.tools
            self.__metadata_collection = self.__db.metadata
            self.__fs = gridfs.GridFS(self.__db)

        def setup(self):
            if "metadata" not in self.__db.list_collection_names() or self.__metadata_collection.count_documents({}) == 0:
                # Not initialized
                self.__metadata_collection.insert_one({"has_initialized_pharos": False})
                print("DatabaseManager is initialized.")

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
                job = self.get_job_by_id_without_tasks(str(job_doc["_id"]))
                job_list.append(job)

            return job_list

        def get_all_tools(self):
            """Return the schemas of all tools with id

            Returns:
                schema_list (List of dict): schemas of all tools with id
            """
            logger = Logger().get()
            logger.debug(f"start get_all_tools")

            try:
                schema_docs = self.__tools_collection.find()

                schema_list = []
                for schema_doc in schema_docs:
                    schema_dict = schema_doc['schema']
                    schema_dict['Tool_ID'] = str(schema_doc['_id'])
                    schema_list.append(schema_dict)

                logger.debug(f"Get {len(schema_list)} tools")
                return schema_list
            except Exception as e:
                logger.error(f"Failed when getting tools. Exception: {e}")

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

        def get_metadata_field(self, field_name):
            """Get the value of single field in metadata.

            Args:
                field_name (String): The key of the field

            Returns:
                value: The value of the field (Undefined type)
            """
            logger = Logger().get()
            logger.debug(f"start get_metadata_field for field:{field_name}")

            if "metadata" not in self.__db.list_collection_names() or self.__metadata_collection.count_documents({}) == 0:
                logger.error("Metadata has not been initialized.")
                return None

            try:
                metadata = self.__metadata_collection.find()[0]
                if field_name not in metadata.keys():
                    logger.error("Metadata doesn't have this field.")
                    return None
                return metadata[field_name]
            except Exception as e:
                logger.error(f"Error when getting metadata. Exception: {e}")
                return None

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

        def get_stderr(self, task_id):
            """Return the stderr of a task

            Args:
                task_id (String): the id of the task

            Return:
                stderr (String): the stderr
            """
            logger = Logger().get()
            logger.debug(f"Start get_stderr from {task_id}")

            try:
                # Find the task using id
                condition = {"_id": ObjectId(task_id)}
                field = {"stderr": 1}
                task_doc = self.__tasks_collection.find_one(condition, field)
                if task_doc is None:
                    raise Exception(f"The task of {task_id} does not exist.")

                return task_doc['stderr']
            except Exception as e:
                logger.error(f"Failed getting stderr from task {task_id}."
                             f"Exception: {e}")
                return None

        def get_stdout(self, task_id):
            """Return the stdout of a task

            Args:
                task_id (String): the id of the task

            Return:
                stdout (String): the stdout
            """
            logger = Logger().get()
            logger.debug(f"Start get_stdout from {task_id}")

            try:
                # Find the task using id
                condition = {"_id": ObjectId(task_id)}
                field = {"stdout": 1}
                task_doc = self.__tasks_collection.find_one(condition, field)
                if task_doc is None:
                    raise Exception(f"The task of {task_id} does not exist.")

                return task_doc['stdout']
            except Exception as e:
                logger.error(f"Failed getting stdout from task {task_id}."
                             f"Exception: {e}")
                return None

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

                # Rebuild the Task object from the query result
                task = Task()
                task.job_id = str(task_doc["job_id"])
                task.task_id = task_id
                task.program_name = task_doc['program_name']
                task.input_file_args = task_doc['input_file_args']
                task.input_text_args = task_doc['input_text_args']
                task.input_flag_args = task_doc['input_flag_args']
                task.output_file_args = task_doc['output_file_args']
                task.output = output_list
                task.stdout = task_doc["stdout"]
                task.stderr = task_doc["stderr"]
                task.status = Status(task_doc["status"])
                task.finished_time = task_doc["finished_time"]
                logger.debug(f"get_task_by_id successfully, task_id:{task_id}")
                return task
            except Exception as e:
                logger.error(f"something wrong in get_task_by_id, Exception: {e}")

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
                return []

        def get_tool_by_id(self, tool_id):
            """Get the schema of the specific tool.

            Args:
                tool_id (String): The id of the tool

            Return:
                tool_dict (dict): The schema of the tool with id
            """
            logger = Logger().get()
            logger.debug(f"start get_tool_by_id, tool_id:{tool_id}")

            try:
                # Get the schema of tool using tool_id
                condition = {"_id": ObjectId(tool_id)}
                tool_doc = self.__tools_collection.find_one(condition)

                # Rebuild the tool with id
                tool_dict = tool_doc['schema']
                tool_dict["Tool_ID"] = str(tool_doc['_id'])

                return tool_dict
            except Exception as e:
                logger.error(f"something wrong in get_tool_by_id,"
                             f" Exception: {e}")

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

        def insert_new_task(self, job_id, new_task):
            """Insert a task into the database

            Args:
                job_id (ObjectId): The id of the parent job
                new_task (Task): The task which will be inserted

            Returns:
                task_id (String): The id of the newly inserted task
            """

            try:
                logger = Logger().get()
                logger.debug(f"start insertion of new task(id: {new_task.task_id}, which is of job(id: {job_id}")

                # Build the new task
                new_task_dict = {
                    "program_name": new_task.program_name,
                    "input_file_args": new_task.input_file_args,
                    "input_text_args": new_task.input_text_args,
                    "input_flag_args": new_task.input_flag_args,
                    "output_file_args": new_task.output_file_args,
                    "job_id": job_id,
                    "output_files": {},
                    "stdout": "",
                    "stderr": "",
                    "status": new_task.status.value,
                    "finished_time": new_task.finished_time,
                }

                # Insert the new task
                result = self.__tasks_collection.insert_one (new_task_dict)
                task_id = result.inserted_id
                logger.debug(f"insert the new task:{task_id}")
                # Don't cast id to String for internal use
                return task_id
            except Exception as e:
                logger.error(f"Insertion of task failed. Exception: {e}")
                return None

        def insert_new_tool(self, schema_json):
            """Insert a new tool.

            Args:
                schema_json (dict): The schema of the new tool.
            """
            logger = Logger().get()
            logger.debug("insert_new_tool starts.")

            new_tool_dict = {
                "schema": schema_json
            }

            try:
                # Insert the new tool
                result = self.__tools_collection.insert_one(new_tool_dict)
            except Exception as e:
                logger.error(f"Failed when inserting a new tool. Exception: {e}")


        def mark_job_as_finished(self, job_id):
            """Mark a job as "Successful" and update its "finished_time"
            Args:
                job_id (String): the id of the job
            """

            try:
                logger = Logger().get()
                logger.debug(f"start mark_job_as_finished for job {job_id}")

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

            try:
                logger = Logger().get()
                logger.debug(f"start mark_task_as_finished for task {task_id}")

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

        def remove_all_tools(self):
            """Remove all tools (Only for collection "test")
            """
            logger = Logger().get()
            logger.debug("remove all tools")
            if self.db_name != "test":
                logger.error("Cannot remove all tools unless current db"
                             " is \"test\"!")
                return

            try:
                # Get ids of all jobs
                field = {"_id": 1}
                delete_result = self.__tools_collection.delete_many({})

                # Set the flag of initialization to False
                metadata = self.__metadata_collection.find()[0]
                metadata['has_initialized_pharos'] = False

                condition = {"_id": metadata['_id']}
                self.__metadata_collection.update_one(condition, {"$set": metadata})

                logger.debug(f"Remove {delete_result.deleted_count} tools.")
            except Exception as e:
                logger.error(f"something wrong in remove_all_tools, Exception: {e}")

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

        def remove_tool_by_id(self, tool_id):
            """Remove the tool with the specified id.

            Args:
                tool_id (String)): the id of the tool
            """
            logger = Logger().get()
            logger.debug(f"remove tool by id, tool_id:{tool_id}")

            try:
                delete_result = self.__tools_collection.delete_one(
                                     {"_id": ObjectId(tool_id)})

                if delete_result.deleted_count is not 1:
                    raise Exception("Delete failed")
            except Exception as e:
                logger.error(f"Something wrong in remove_tasks_by_job_id,"
                             f" Exception: {e}")

        def save_result(self, task_id, output, stdout, stderr):
            """Save the result of the task specified by task_id

            Args:
                task_id (String): The id of the specific task
                output (List of String): Each entry is a path of an output file
                log (List of String): Each entry in log is the path of an log file
                stdout (String): The stdout of the task
                stderr (String): The stderr of the task
            """

            try:
                logger = Logger().get()
                logger.debug(f"start save_result task_id:{task_id}, "
                             f"output:{output}, stdout:{stdout}, stderr:{stderr}")

                # Cast task_id from String to ObjectId first
                task_id = ObjectId(task_id)
            except Exception as e:
                logger.error(f"Problem with the parameters: {e}")

            # Insert all files into gridfs
            # Build the output_dict(filename->id)
            output_dict = {}
            for output_file_path in output:
                try:
                    with open(output_file_path, "r") as f:
                        file_id = self.__fs.put(f.read().encode("utf-8"))
                    filename = os.path.basename(os.path.normpath(output_file_path))
                    output_dict[filename] = file_id
                except Exception as e:
                    logger.error(f"Problem when storing file {output_file_path}. Exception{e}")

            try:
                # Update the output fields of the task
                condition = {"_id": task_id}
                task = self.__tasks_collection.find_one(condition)
                task["output_files"] = output_dict
                task["stdout"] = stdout
                task["stderr"] = stderr

                update_result = self.__tasks_collection.update_one(condition,
                                                                   {"$set": task})
                if update_result.modified_count != 1:
                    logger.error(f"save result failed")
            except Exception as e:
                logger.error(f"something wrong in save_result, Exception: {e}")


        def set_metadata_field(self, field_name, new_value):
            """Set the value of single field in metadata.

            Args:
                field_name (String): The key of the field
                new_value (Undefined): The new value of the field

            Returns:
                is_success: True for successful update, vice versa
            """
            logger = Logger().get()
            logger.debug(f"start set_metadata_field for field:{field_name} "
                         f"new_value:{new_value}")

            if "metadata" not in self.__db.list_collection_names() or self.__metadata_collection.count_documents({}) == 0:
                logger.error("Metadata has not been initialized.")
                return False

            try:
                metadata = self.__metadata_collection.find()[0]
                metadata[field_name] = new_value

                condition = {"_id": metadata["_id"]}
                self.__metadata_collection.update_one(condition, {"$set": metadata})
                return True
            except Exception as e:
                logger.error(f"Error when setting metadata. Exception: {e}")
                return False

        def update_job_status(self, job_id, new_status):
            """Update the status of a job

            Arg:
                job_id (String): the id of the job
                new_status (Status): the new status of the job
            """
            logger = Logger().get()

            try:
                logger.debug(f"Start update job({job_id}) to {new_status.name}")
                condition = {"_id": ObjectId(job_id)}
                job = self.__jobs_collection.find_one(condition)
                job["status"] = new_status.value

                update_result = self.__jobs_collection.update_one(condition,
                                                                  {"$set": job})
                if update_result.modified_count != 1:
                    raise Exception("update_result.modified_count != 1")
            except Exception as e:
                logger.error(f"Failed when updating job status. Exception: {e}")


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
