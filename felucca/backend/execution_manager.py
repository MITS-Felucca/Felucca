import os
import argparse
import shlex
import tarfile
import docker
from common.singleton import Singleton
from threading import Thread



@Singleton
class ExecutionManager(object):
    
    """Resource Manager is responsible for: 
        
        1. receive a task from Job Manager 
        2. create a predifined conatiner and copy exe into container
        3. parse the original cmd and change it to the cmd correspooding to the path inside the conatiner
        4. execute the exe with phraos inside container
        
    """
    def __init__(self):
        self.map_id_to_task_container = {}
        
    def commandline_path_parser(self,task):
        
        """change a task's field: 1)command_line_input 2) executable_file, to the cmd and path used inside the conatiner
    
        Args:
            task (Task): The task object to be executed
        
        """
        command_line_input = task.command_line_input
        
        parser = argparse.ArgumentParser()
         
        parser.add_argument('-ooanalyzer', dest="ooanalyzer",action = "store_true",default=False)
        parser.add_argument('-j','--json', dest="j", type = str)
        parser.add_argument('-R','--prolog-results ', dest="R", type = str)
        parser.add_argument('-n','--new-method', dest="n", type = str)
        parser.add_argument('-F','--prolog-facts', dest="F", type = str)
        parser.add_argument('-f','--file', dest="f", type = str)

        if(command_line_input[0]!='-'):
            command_line_input = '-'+command_line_input
                
        a = parser.parse_args(shlex.split(command_line_input))

        dict = vars(a)
        
        #j F R should be replaced to a defined path
        #f should be the path of executable file will be copied into the container
        
        if 'j' in dict:

            dict['j'] = os.path.join("/tmp",dict['j'])
        if 'F' in dict:

            dict['F'] = os.path.join("/tmp",dict['F'])
        if 'R' in dict:

            dict['R'] = os.path.join("/tmp",dict['R'])
        if 'f' in dict:

            dict['f'] = os.path.join("/tmp",dict['f'])
            
        exe_path_in_container = dict['f']
        
        new_command_line_input = ""
        
        for key in dict:
            if type(dict[key])==bool:
                new_command_line_input = new_command_line_input+key+" "
            elif dict[key] is not None:
                new_command_line_input = new_command_line_input+"-"+key+" "+dict[key]+" "
                
        
        
        task.command_line_input = new_command_line_input
        task.executable_file = exe_path_in_container
        

        
    def copy_to_container(self,src,dst,container):
        
        """copy executable_file into the conatiner from src to dst
    
        Args:
            src (str): The absolute path of executable file in the backend 
            dst (str): The absolute path of executable file in the container 
            container (Container): the docker container created to run this task 
        
        """

        os.chdir(os.path.dirname(src))
        srcname = os.path.basename(src)

        tar = tarfile.open(src + '.tar', mode='w')
        try:
            tar.add(srcname)
        except Exception as e:
            print(e)
        finally:
            tar.close()
    
        data = open(src + '.tar', 'rb').read()
        container_dir = os.path.dirname(dst)
        container.exec_run("mkdir "+container_dir)
        container.put_archive(container_dir, data)
        
    def set_map(self,task,container):
        
        """set the map kept in ExecutionManager with format: task_id -> tuple:( task(Task), container(Container) )
    
        Args:
            task (Task): The task object to be executed
            container (Container): the docker container created to run this task 
        
        """
        
        self.map_id_to_task_container[task.task_ids] = (task,container)
        
    def run_container_flask(self,container):
        
        """set the map kept in ExecutionManager with the format: task_id -> tuple:( task(Task), container(Container) )
    
        Args:
            task (Task): The task object to be executed
            container (Container): the docker container created to run this task 
        
        """
        
        exec_log = container.exec_run("flask run --host=0.0.0.0" ,stdout=True,stderr=True,stream=True)

        for line in exec_log[1]:
            print(line)
             
        
    def get_command_line_input(self, task_id):
        
        """return the command_line_input correspoding to the given task_id
    
        Args:
            task_id (Task): The id of the task
        
        Returns:
            command_line_input (str): The command_line used inside the container to run the executable file with phraos
        """
        
        task = self.map_id2Task_container[task_id][0]
        return(task.command_line_input)
        
    def submit_task(self,task):
        """Job Manager call this method and submit a task. This method will launch the whole procedure (i.e. parse cmd, create conatiner, run exe with phraos and insert result into Resource Manager) of the Execution Manager
    
        Args:
            task (Task): The task from Job Manager
        
        Returns:
            if successful, return true to Job Manager
        """
    
        exe_path_outside = task.executable_file

        self.commandline_path_parser(task)#this will change task two attr: task.executable_file & task.command_line_input   to conatiner path version
        
        client = docker.from_env()
    
        container = client.containers.create("felucca/pharos",command="/bin/bash",tty=True,stdin_open=True,auto_remove=False)
        
        self.set_map(task,container)
        
        container.start()

        t = Thread(target=self.run_container_flask, args=(container, ))
        t.start()
        
        self.copy_to_container(exe_path_outside,task.executable_file,container)
 
        exec_log = container.exec_run("cat "+task.executable_file,stdout=True,stderr=True,stream=True)
                
        for line in exec_log[1]:
            print(line)
  
        return(True);