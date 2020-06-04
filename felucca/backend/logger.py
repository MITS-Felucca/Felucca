from common.singleton import Singleton
import logging
import os

@Singleton
class Logger:
    def __init__(self, name=__name__):
        
        self.__name = name
        self.logger = logging.getLogger(self.__name)
        self.logger.setLevel(logging.DEBUG)

        log_path = os.path.dirname(os.path.abspath(__file__))
        logname = log_path + '/' + 'log.txt'  # 指定输出的日志文件名
        fh = logging.FileHandler(logname, mode='w', encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)



        formatter = logging.Formatter("%(levelname) -10s %(asctime)s %(module)s:%(lineno) -7s %(message)s",datefmt="%m/%d/%Y %I:%M:%S %p %Z")
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    @property
    def get_log(self):
        return self.logger


