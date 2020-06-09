import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend/common'))
from task import Task
from common.status import Status

class Job(object):
    """ Job object
    Job contain a bunch of tasks
    """

    def __init__(self, name, comment, created_time=None, finished_time=None, status=Status.Pending):
        self.__job_id = None
        self.__tasks = None
        self.__name = name
        self.__comment = comment
        self.__created_time = created_time
        self.__finished_time = finished_time
        self.__status = status
    
    @property
    def name(self):
        return self.__name
    
    @property
    def comment(self):
        return self.__comment

    @property
    def created_time(self):
        return self.__created_time
    
    @created_time.setter
    def created_time(self, val):
        self.__created_time = val
    
    @property
    def finished_time(self):
        return self.__finished_time
    
    @finished_time.setter
    def finished_time(self, val):
        self.__finished_time = val

    @property
    def job_id(self):
        return self.__job_id

    @job_id.setter
    def job_id(self, val):
        self.__job_id = val

    @property
    def tasks(self):
        return self.__tasks
    
    @tasks.setter
    def tasks(self, val):
        self.__tasks = val

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, val):
        self.__status = val
    
    @classmethod
    def from_json(cls,json):
        
        """Construct a job instance from an input json with predefined format

        Args:
            json (dict): json from frontend
        
        Returns:
            job (Job): Job object
        """
    
        job_name = json["Job_Name"]
        job_comment = json["Job_Comment"]
        # created_time = json["Created_Time"]
        job = Job(job_name, job_comment)
        job.tasks = []
        
        for task_dict in json["Tasks"]:
            task = Task.from_json(task_dict)
            job.tasks.append(task)
            
        return(job)
    
    @classmethod
    def to_json(cls,job,need_task = False):
        
        """form a json-like dict output from a job instance, the predifined dict format is as follow:
        {Name | Comment | Created_Time | Task_Number | Status | ID | Tasks(list of task dict) }  

        Args:
            job (Job): a job instance
        
        Returns:
            job_json (dict): a json-like dict of job object

        """
        job_json = {}
        job_json["Name"] = job.name
        job_json["Comment"] = job.comment
        
        if job.finished_time is None:
            job_json["Created_Time"] = 0
        else:
            job_json["Created_Time"] = time.mktime(job.created_time.timetuple())
        
        
        job_json["Task_Number"] = len(job.tasks)
        job_json["Status"] = job.status
        job_json["ID"] = job.job_id
        job_json["Tasks"] = []
        if need_task:
            for task in job.tasks:
                task_dict = Task.to_json(task)
                job_json["Tasks"].append(task_dict)
            
        return(job_json)
