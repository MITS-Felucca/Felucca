import os
import argparse
import shlex
import tarfile
import docker
from threading import Thread

from common.singleton import Singleton
from resource_manager import ResourceManager
from common.status import Status
from logger import Logger
CONTAINER_PORT = '5000'

@Singleton
class ExecutionManager(object):
    """Execution Manager is responsible for: 
        
        1. receive a task from Job Manager 
        2. create a predefined container and copy exe into container
        3. parse the original cmd and change it to the cmd correspooding to the path inside the container
        4. execute the exe with pharos inside container
        
    """

    def __init__(self):
        self.id_to_task_container = {}

    def save_result(self, task_id, status, stderr, stdout):
        """save the result from container to the database

        Args:
            task_id (int): the result under this task_id
            status (STATUS): the task status
            stderr (byte[]): the output in std error
            stdout (byte[]): the output in std out
        """
        logger = Logger().get()
        logger.debug(f"start save_result: task_id: {task_id} status: {status}")
        output_path = self.id_to_task_container[task_id][0].output
        log_path = self.id_to_task_container[task_id][0].log
        container = self.id_to_task_container[task_id][1]

        # get result from container
        container.exec_run("tar -cvf result.tar %s %s" % (" ".join(output_path), " ".join(log_path)))
        bits, stat = container.get_archive("result.tar")
        path = "/vagrant/result/%s" % (str(task_id))
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
        file = open(os.path.join(path,"result.tar"), "wb") 
        for chunk in bits:
            file.write(chunk)
        file.close()

        # extract result tar file
        result_tar = tarfile.open("%s/result.tar" % (path))
        result_tar.extractall(path)
        result_tar.close()
        
        result_tar1 = tarfile.open("%s/result.tar" % (path))
        result_tar1.extractall(path)
        result_tar1.close()

        container.stop()
        container.remove()

        for index in range(len(output_path)):
            output_path[index] = os.path.join(path, output_path[index][1:])
        for index in range(len(log_path)):
            log_path[index] = os.path.join(path, log_path[index][1:])
            
        ResourceManager().save_result(task_id, output_path, log_path, stdout, stderr)
        ResourceManager().update_task_status(task_id, Status[status])
        self.id_to_task_container.pop(task_id, None)

    def commandline_path_parser(self,task):
        
        """change a task's field: 1)command_line_input 2) executable_file, to the cmd and path used inside the container
    
        Args:
            task (Task): The task object to be executed
        
        """
        command_line_input =task.command_line_input.lstrip()
        
        parser = argparse.ArgumentParser()
         
        parser.add_argument('-ooanalyzer', dest="ooanalyzer",action = "store_true",default=False)
        parser.add_argument('-j','--json', dest="j", type = str)
        parser.add_argument('-R','--prolog-results ', dest="R", type = str)
        parser.add_argument('-n','--new-method', dest="n", type = str)
        parser.add_argument('-F','--prolog-facts', dest="F", type = str)
        parser.add_argument('-f','--file', dest="f", type = str)

        if command_line_input[0] != '-' :
            command_line_input = '-' + command_line_input
                
        a = parser.parse_args(shlex.split(command_line_input))

        dict = vars(a)
        
        #j F R should be replaced to a defined path
        #f should be the path of executable file will be copied into the container
        output = []
        log = []
        if dict['j'] is not None :
            dict['j'] = os.path.join("/tmp",dict['j'])
            output.append(dict['j'])

        if dict['F'] is not None :
            dict['F'] = os.path.join("/tmp",dict['F'])
            log.append(dict['F'])

        # result
        if dict['R'] is not None :
            dict['R'] = os.path.join("/tmp",dict['R'])
            log.append(dict['R'])

        if dict['f'] is not None :
            dict['f'] = os.path.basename(dict['f'])
            dict['f'] = os.path.join("/tmp",dict['f'])
            task.executable_file = dict['f']
        else:
            task.executable_file = os.path.join("/tmp", os.path.basename(task.executable_file))

        new_command_line_input = ""
        
        for key in dict:
            if type(dict[key])==bool:
                new_command_line_input = new_command_line_input+key+" "
            elif dict[key] is not None:
                new_command_line_input = new_command_line_input+"-"+key+" "+dict[key]+" "
                
        if 'f' not in dict:
            new_command_line_input = new_command_line_input+" task.executable_file"
        
        task.command_line_input = new_command_line_input

        task.set_result(output=output,log=log)
        
        
    def copy_to_container(self,src,dst,container):
        
        """copy executable_file into the container from src to dst
    
        Args:
            src (str): The absolute path of executable file in the backend 
            dst (str): The absolute path of executable file in the container 
            container (Container): the docker container created to run this task 
        
        """
        logger = Logger().get()
        os.chdir(os.path.dirname(src))
        srcname = os.path.basename(src)

        tar = tarfile.open(src + '.tar', mode='w')
        try:
            tar.add(srcname)
        except Exception as e:
            logger.error(f"copy_to_container fails, container:{container.name}, Exception: {e}")
        finally:
            tar.close()
    
        data = open(src + '.tar', 'rb').read()
        container_dir = os.path.dirname(dst)
        container.exec_run("mkdir "+container_dir)
        container.put_archive(container_dir, data)
        
        path = src + '.tar'
        if(os.path.exists(path)):
            os.remove(path)
        
    def set_map(self,task,container):
        
        """set the map kept in ExecutionManager with format: task_id -> tuple:( task(Task), container(Container) )
    
        Args:
            task (Task): The task object to be executed
            container (Container): the docker container created to run this task 
        
        """
        
        self.id_to_task_container[task.task_id] = (task,container)
        
    def run_container_flask(self,container):
        
        """run the flask server inside the container, this server is responsible for the following network communication
    
        Args:
            container (Container): the docker container created to run this task 
        
        """
        logger = Logger().get()
        logger.debug(f"start run container_server{container.name}")
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
        task = self.id_to_task_container[task_id][0]
        
        return(task.command_line_input)
        
    def submit_task(self,task):
        """Job Manager call this method and submit a task. This method will launch the whole procedure (i.e. parse cmd, create container, run exe with phraos and insert result into Resource Manager) of the Execution Manager
    
        Args:
            task (Task): The task from Job Manager
        
        Returns:
            if successful, return true to Job Manager
        """
        logger = Logger().get()
        logger.debug(f"receive task: task_id = {task.task_id}, job_id = {task.job_id}")
        exe_path_outside = task.executable_file

        self.commandline_path_parser(task)#this will change task two attr: task.executable_file & task.command_line_input   to container path version
        
        client = docker.from_env()
    
        container = client.containers.create("felucca/pharos",command="/bin/bash",environment = [f"TASK_ID={task.task_id}"],tty=True,stdin_open=True,auto_remove=False)
        logger.debug(f"successfully create a container : {container.name}")
        self.set_map(task,container)
        
        container.start()

        t = Thread(target=self.run_container_flask, args=(container, ))
        t.start()
        
        self.copy_to_container(exe_path_outside,task.executable_file,container)
        logger.debug(f"successfully copy exe into container({container.name})")
        return(True);
