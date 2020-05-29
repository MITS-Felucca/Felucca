from common.status import Status

class Task(object):
    """Task Object
    Task object represent a pharos executable task 
    """

    def __init__(self, executable_file, tool_type, command_line_input, finished_time=None, status=Status.Pending):
        self.__executable_file = executable_file
        self.__tool_type = tool_type
        self.__command_line_input = command_line_input
        self.__job_id = None
        self.__task_id = None
        self.__output = None
        self.__log = None
        self.__stdout = None
        self.__stderr = None
        self.__status = status
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
    def executable_file(self):
        return self.__executable_file

    @executable_file.setter
    def executable_file(self,val):
        self.__executable_file = val

    @property
    def tool_type(self):
        return self.__tool_type

    @property
    def command_line_input(self):
        return self.__command_line_input
    
    @property
    def finished_time(self):
        return self.__finished_time

    @command_line_input.setter
    def command_line_input(self,val):
        self.__command_line_input = val

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
