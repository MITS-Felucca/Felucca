class Job(object):
    """ Job object
    Job contain a bunch of tasks
    """

    def __init__(self, name, comments, create_time):
        self.__job_id = None
        self.__tasks = None
        self.__name = name
        self.__comments = comments
        self.__create_time = create_time
    
    @property
    def name(self):
        return self.__name
    
    @property
    def comments(self):
        return self.__comments

    @property
    def create_time(self):
        return self.__create_time

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
