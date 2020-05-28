from status import Status

class Job(object):
    """ Job object
    Job contain a bunch of tasks
    """

    def __init__(self, name, comments, created_time, finished_time=None, status=Status.Pending):
        self.__job_id = None
        self.__tasks = None
        self.__name = name
        self.__comments = comments
        self.__created_time = created_time
        self.__finished_time = finished_time
        self.__status = status
    
    @property
    def name(self):
        return self.__name
    
    @property
    def comments(self):
        return self.__comments

    @property
    def created_time(self):
        return self.__created_time
    
    @property
    def finished_time(self):
        return self.__finished_time

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
