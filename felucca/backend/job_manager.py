from common.singleton import Singleton
from resource_manager import ResourceManager
from execution_manager import ExecutionManager
from logger import Logger

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
        logger = Logger().get
        logger.debug(f"receive job in submit_job")

        job_id, tasks_id = ResourceManager().insert_new_job(new_job)
        logger.debug(f"insert new job to ResourceManager finished, get job_id:{job_id}, tasks_id:{tasks_id}")
        new_job.job_id = job_id

        for task, task_id in zip(new_job.tasks, tasks_id):
            task.task_id = task_id
        self.job_metadata[job_id] = new_job
        self.task_id_to_job_id[new_job.tasks[0].task_id] = new_job.job_id

        # only submit first task in this dummy implementation
        logger.debug(f"submit task to ExecutionManager, task_id={new_job.tasks[0].task_id}")
        ExecutionManager().submit_task(new_job.tasks[0])

        return job_id, tasks_id

    def finish_task(self, task_id):
        """Finish task report

        :param task_id: task_id of finished task
        :return: Returned Nothing.
        """
        logger = Logger().get
        
        try:
            job_id = self.task_id_to_job_id[task_id]
            print('received task: %s belongs to %s\n' % (task_id, job_id))
            del self.job_metadata[job_id]
            del self.task_id_to_job_id[task_id]
            logger.debug(f"finish_task{task_id}")
        except Exception as e:
            logger.error(f"something wrong in finish_task, Exception: {e}")

        
    pass