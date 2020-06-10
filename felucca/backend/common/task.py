import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend'))

from common.status import Status


class Task(object):
    """Task Object
    Task object represent a pharos executable task 
    """

    def __init__(self, files={}, tool_type=0, arguments={}, finished_time=None, status=Status.Pending):
        # self.__executable_file = executable_file
        self.__files = files
        self.__tool_type = tool_type
        # self.__command_line_input = command_line_input
        self.__arguments = arguments
        self.__job_id = None
        self.__task_id = None
        self.__output = None
        self.__log = None
        self.__stdout = None
        self.__stderr = None
        self.__status = status
        self.__start_time = None
        self.__finished_time = finished_time

    @property
    def job_id(self):
        return self.__job_id

    @job_id.setter
    def job_id(self, val):
        self.__job_id = val

    @property
    def task_id(self):
        return self.__task_id
    
    @task_id.setter
    def task_id(self, val):
        self.__task_id = val

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self, val):
        self.__output = val

    @property
    def log(self):
        return self.__log
    
    @log.setter
    def log(self, val):
        self.__log = val

    @property
    def stdout(self):
        return self.__stdout
    
    @stdout.setter
    def stdout(self, val):
        self.__stdout = val

    @property
    def stderr(self):
        return self.__stderr
    
    @stderr.setter
    def stderr(self, val):
        self.__stderr = val
    
    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, val):
        self.__status = val

    @property
    def files(self):
        return self.__files

    @files.setter
    def files(self,val):
        self.__files = val

    @property
    def tool_type(self):
        return self.__tool_type

    @property
    def arguments(self):
        return self.__arguments

    @arguments.setter
    def arguments(self,val):
        self.__arguments = val
    
    @property
    def start_time(self):
        return self.__start_time
    
    @start_time.setter
    def start_time(self,val):
        self.__start_time = val

    @property
    def finished_time(self):
        return self.__finished_time
    
    @finished_time.setter
    def finished_time(self,val):
        self.__finished_time = val

    def set_result(self, output = None, log = None, stdout = None, stderr = None):
        """Set the result for finished task
        The execution manager will get three types of result

        Args:
            output: the output file in json format
            log: the log file in txt format
            stdout: the stdout in string format
        """
        self.__output = output
        self.__log = log
        self.__stdout = stdout
        self.__stderr = stderr
    
    @classmethod
    def from_json(cls,task_dict):
        """construct a task instance from a task_dict
        This class method will be invoked by Job.form_json()

        Args:
            task_dict (dict): element in input json's list: input json["Tasks"]
        
        Returns:
            task (Task): Task object
        """
        
        # Files = task_dict["Files"]
        tool_type = task_dict["Tool_ID"]
        argument = task_dict["Arguments"]
        task = Task({},tool_type,argument)
        
        return task
    
    @classmethod
    def to_json(cls,task):
        
        """form a json output from a task instance

        Args:
            task (Task): a job instance
        
        Returns:
            task_dict (dict): dict format of task correspoding to the predefined format, the format is as follow:
            
            
        Tasks :{Argument(no path, dict) | Output[] | Log[] | Stdout : String | Stderr | Finished_Time : long(seconds since epoch) | Status: String | ID : String }

        """
        task_dict = {}

        task_dict["Arguments"] = task.arguments
        task_dict["Output"] = task.output
        task_dict["Log"] = task.log
        task_dict["Stdout"] = task.stdout
        task_dict["Stderr"] = task.stderr
        if task.finished_time is None:
            task_dict["Finished_Time"] = 0
        else:
            task_dict["Finished_Time"] = time.mktime(task.finished_time.timetuple())
        task_dict["Status"] = task.status.name
        task_dict["ID"] = task.task_id

        
        return task_dict
