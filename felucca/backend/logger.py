import logging
import os
from common.singleton import Singleton

@Singleton
class Logger:
    """the logger class for all backend program

    """
    def __init__(self,log_level = "d", stdout = False, name=__name__):
        
        """constructor for establish a logger, the default log_level is "DEBUG"
    
        Args:
            log_level (str): "d" or other str stands for "DEBUG", "e" for "ERROR" and "i" for "INFO"  
            name : the name of the backend program use this class (execution_manager, job_manager, resource_manager, server) 
        
        """
        
        self.__name = name
        self.logger = logging.getLogger(self.__name)
        self.logger.setLevel(logging.DEBUG)
        self.log_level = log_level
        
        #set up the log file handler(fh) and log stream handler(sh)
        if not self.logger.handlers:
            #Can't use absolute path here, logging is fixed to append the address based on current path
            #therefore, this code should be ran at backend folder
            folder_path = "../../../../../tmp/Felucca/"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            fh = logging.FileHandler(os.path.join(folder_path,"log.txt"), mode='a', encoding='utf-8')    
            
            if stdout:
                sh = logging.StreamHandler()

            if self.log_level == "e":
                fh.setLevel(logging.ERROR)
                if stdout:
                    sh.setLevel(logging.ERROR)
                self.logger.setLevel(logging.ERROR)
            elif self.log_level == "i":
                fh.setLevel(logging.INFO)
                if stdout:
                    sh.setLevel(logging.INFO)
                self.logger.setLevel(logging.INFO)
            else:
                fh.setLevel(logging.DEBUG)
                if stdout:
                    sh.setLevel(logging.DEBUG)
                self.logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter("%(levelname) -10s %(asctime)s %(module)s:%(lineno) -7s %(message)s")
            if stdout:
                sh.setFormatter(formatter)
            fh.setFormatter(formatter)            
            self.logger.addHandler(fh)
            if stdout:
                self.logger.addHandler(sh)
            
    def get(self):
        return self.logger
