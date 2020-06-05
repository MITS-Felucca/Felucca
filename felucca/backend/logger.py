import logging
import os
from common.singleton import Singleton

@Singleton
class Logger:
    """the logger class for all backend program

    """
    def __init__(self,log_level = "d", name=__name__):
        
        """constructor for establish a logger, the default log_level is "DEBUG"
    
        Args:
            log_level (str): "d" or other str stands for "DEBUG", "e" for "ERROR" and "i" for "INFO"  
            name : the name of the backend program use this class (execution_manager, job_manager, resource_manager, server) 
        
        """
        
        self.__name = name
        self.logger = logging.getLogger(self.__name)
        self.logger.setLevel(logging.DEBUG)
        self.log_level = log_level
        
        #log file will be recorded at backend folder
        log_path = os.path.dirname(os.path.abspath(__file__))
        log_name = log_path + '/' + 'log.txt'  
        
        #set up the log file handler(fh) and log stream handler(sh)
        if not self.logger.handlers:
            
            fh = logging.FileHandler(log_name, mode='w', encoding='utf-8')    
            sh = logging.StreamHandler()

            if self.log_level == "e":
                fh.setLevel(logging.ERROR)
                sh.setLevel(logging.ERROR)
                self.logger.setLevel(logging.ERROR)
            elif self.log_level == "i":
                fh.setLevel(logging.INFO)
                sh.setLevel(logging.INFO)
                self.logger.setLevel(logging.INFO)
            else:
                fh.setLevel(logging.DEBUG)
                sh.setLevel(logging.DEBUG)
                self.logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter("%(levelname) -10s %(asctime)s %(module)s:%(lineno) -7s %(message)s")
            sh.setFormatter(formatter)
            fh.setFormatter(formatter)
            
            self.logger.addHandler(fh)
            self.logger.addHandler(sh)
            
    @property
    def get(self):
        return self.logger
