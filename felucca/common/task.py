class Task(object):
    """Task Object
    Task object represent a pharos executable task 
    """

    def __init__(self, task_executable_file, tool_type, command_line_input):
        self.task_executable_file = task_executable_file
        self.tool_type = tool_type
        self.command_line_input = command_line_input
        self.__job_id = None
        self.__task_ids = None
        self.__output = None
        self.__log = None
        self.__stdout = None

    @property
    def job_id(self):
        return self.__job_id

    @job_id.setter
    def job_id(self, val):
        self.__job_id = val

    @property
    def task_ids(self):
        return self.__task_ids
    
    @task_ids.setter
    def task_ids(self, val):
        self.__task_ids = val

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

    def set_result(self, output = None, log = None, stdout = None):
        """Set the result for finished task
        The execution manager will get three types of result

        Args:
            output: the output file in json format
            log: the log file in txt format
            stdout: the stdout in string format
        """
        self.output = output
        self.log = log
        self.stdout = stdout
