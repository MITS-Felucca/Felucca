from common.singleton import Singleton
from common.status import Status
from resource_manager import ResourceManager
from execution_manager import ExecutionManager
from logger import Logger

db_name = 'test'
# db_name = 'felucca'

@Singleton
class JobManager(object):
    """Job Manager is responsible for:
        1. receive a Job from front-end
        2. figure out the dependency
        3. submit task to execution manager
        4. receive callback from execution manager
    """

    def __init__(self):
        self.job_metadata = {}
        self.task_id_to_job_id = {}

    def submit_job(self, new_job):
        """Submit a job to Resource manager to get job_id and task_ids, then submit first task.

        :param new_job: a new job instance submitted by front_end
        :return: Returned Nothing.
        """
        logger = Logger().get()
        logger.debug(f"receive job in submit_job")

        # logger.debug(f"insert new job to ResourceManager finished, get job_id:{job_id}, tasks_id:{tasks_id}")

        self.initialize_job(new_job)

        logger.debug(f"submit task to ExecutionManager, task_id={new_job.tasks[0].task_id}")
        for task in new_job.tasks:
            ExecutionManager().submit_task(task)


    def finish_task(self, task_id):
        """Set the task status to finished and update the finished count of its job.

        Args:
            task_id (String): The id of the specific task
        """
        logger = Logger().get()

        try:
            job_id = self.task_id_to_job_id[task_id]
            job = self.job_metadata[job_id]
            if job.finished_map[task_id] is True:
                return
            job.finished_map[task_id] = True
            job.finished_count += 1

            # Check if all tasks of the job have finished
            if job.finished_count == len(job.tasks):
                ResourceManager(db_name).update_job_status(job_id, Status.Finished)
        except Exception as e:
            logger.error(f"something wrong in finish_task, Exception: {e}")

    def initialize_job(self, new_job):
        """Initialize additional metadata of the new job.

        Args:
            new_job (Job): The job object
        """
        new_job.finished_count = 0
        new_job.finished_map = {}
        for task in new_job.tasks:
            new_job.finished_map[task.task_id] = False
        self.job_metadata[new_job.job_id] = new_job
        for task in new_job.tasks:
            self.task_id_to_job_id[task.task_id] = new_job.job_id
        ResourceManager(db_name).update_job_status(new_job.job_id, Status.Running)