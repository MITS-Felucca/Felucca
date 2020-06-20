import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../felucca/backend'))

from common.status import Status


class Task(object):
    """Task Object
    Task object represent a pharos executable task 
    """

    def __init__(self, status=Status.Pending):
        self.__files = None
        self.__program_name = None
        self.__input_file_args = None
        self.__input_text_args = None
        self.__input_flag_args = None
        self.__output_file_args = None
        self.__job_id = None
        self.__task_id = None
        self.__output = None
        self.__stdout = None
        self.__stderr = None
        self.__status = status
        self.__start_time = None
        self.__finished_time = None

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
    def program_name(self):
        return self.__program_name
    
    @program_name.setter
    def program_name(self,val):
        self.__program_name = val        
        
    @property
    def input_file_args(self):
        return self.__input_file_args

    @input_file_args.setter
    def input_file_args(self,val):
        self.__input_file_args = val
        
    @property
    def input_text_args(self):
        return self.__input_text_args

    @input_text_args.setter
    def input_text_args(self,val):
        self.__input_text_args = val
    @property
    def input_flag_args(self):
        return self.__input_flag_args

    @input_flag_args.setter
    def input_flag_args(self,val):
        self.__input_flag_args = val
        
    @property
    def output_file_args(self):
        return self.__output_file_args

    @output_file_args.setter
    def output_file_args(self,val):
        self.__output_file_args = val

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

    def set_result(self, output = None, stdout = None, stderr = None):
        """Set the result for finished task
        The execution manager will get three types of result

        Args:
            output: the output file in json format
            stdout: the stdout in string format
            stderr: the stderr in string format
        """
        self.__output = output
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

        task = Task()
        task.files = task_dict["Files"]
        task.program_name = task_dict["Program_Name"]
        task.input_file_args = task_dict["Input_File_Args"]
        task.input_text_args = task_dict["Input_Text_Args"]
        task.input_flag_args = task_dict["Input_Flag_Args"]
        task.output_file_args = task_dict["Output_File_Args"]
        
        return task
    
    @classmethod
    def to_json(cls,task):
        
        """form a json output from a task instance

        Args:
            task (Task): a job instance
        
        Returns:
            task_dict (dict): dict format of task correspoding to the predefined format, the format is as follow:
            
            
        Tasks :{Program_Name:string | Argument(no path, dict) | Output[] | Stdout : String | Stderr | Finished_Time : long(seconds since epoch) | Status: String | ID : String }

        """
        
        task_dict = {}
        task_dict["Program_Name"] = task.program_name
        
        argument = {}
        for key, value in task.input_file_args.items():
            argument[key] = value
        for key, value in task.input_text_args.items():
            argument[key] = value
        for key in task.input_flag_args:
            argument[key] = ""
        for key, value in task.output_file_args.items():
            argument[key] = value

        task_dict["Arguments"] = argument
        task_dict["Output"] = task.output
        task_dict["Stdout"] = task.stdout
        task_dict["Stderr"] = task.stderr
        if task.finished_time is None:
            task_dict["Finished_Time"] = 0
        else:
            task_dict["Finished_Time"] = time.mktime(task.finished_time.timetuple())
        task_dict["Status"] = task.status.name
        task_dict["ID"] = task.task_id

        return task_dict