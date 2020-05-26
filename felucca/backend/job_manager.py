import sys
sys.path.append(r'../common')
import os

class JobManager(object):
    
    #def __init__(self):
    def get_task(self):    
        #exe_path = "/../../tests/ApiGraphTestProgram1.exe"
        exe_path = "/../../tests/foo.txt"
        abs_exe_path = os.getcwd() + exe_path
        command_line_input = "ooanalyzer -j output.json -F facts -R results -f oo.exe"
        #todo: send metadata to database
        return(abs_exe_path,command_line_input)