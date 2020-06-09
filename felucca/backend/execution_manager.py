import os
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
        path = "/vagrant/result/%s" % (task_id)
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
        
        #delete local exe file and folder
        logger.debug(f"delete every file in /tmp/Felucca")
        for root, dirs, files in os.walk("/tmp/Felucca", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        
        

    def commandline_path_parser(self,task):
        
        """change a task's arguments corresponding to the exe path inside tge container
        For input file, the absolute path is the same as input file outside the container, i.e. "/tmp/Felucca/{task.task_id}/{input_filename}"
        For output file path, the absolute path is "/tmp/Felucca/{task.task_id}/{output_filename}"
    
        Args:
            task (Task): The task object to be executed
        
        """
        #change the input file path
        logger = Logger().get()
        task.output = []
        task.log = []
        for task_key in task.arguments:
            if task_key in ["-f","-s"]:
                for file_key in task.files:
                    if file_key == task.arguments[task_key]:
                        task.arguments[task_key] = task.files[file_key]
                        break
           
            elif task_key in ["-R","-F"]:
                task.arguments[task_key] = os.path.join(f"/tmp/Felucca/{task.task_id}/",task.arguments[task_key])

                task.log.append(task.arguments[task_key])
                
            elif task_key in ["-j"]:
                task.arguments[task_key] = os.path.join(f"/tmp/Felucca/{task.task_id}/",task.arguments[task_key])

                task.output.append(task.arguments[task_key])
        logger.debug(f"for task({task.task_id}),the task.arguments is {task.arguments}")
    
    def copy_to_container(self,task,container):
        
        """copy executable_file into the container
            this method will copy the input file from "task.files[key]" at backend to "task.files[key]" ( i.e. the same dst becasue this path is unique for each task) inside the given conatiner
    
        Args:
            task (Task): task object which conatiner the absolute exe file path currently (i.e. each task.files[key])
            container (Container): the docker container created to run this task 
        
        """
        logger = Logger().get()
        
        for key in task.files:
            src = task.files[key]
            dst = src
            #dst = os.path.join(f"/tmp/Felucca/{task.task_id}/",key)
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
            container.exec_run("mkdir -p "+container_dir)
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
        self.id_to_task_container[str(task.task_id)] = (task,container)
        
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
        logger = Logger().get()
        task = self.id_to_task_container[task_id][0]
        command_line_input = ""
        
        if task.tool_type == 1:
            command_line_input = command_line_input +"ooanalyzer"
        for key in task.arguments:
            command_line_input = command_line_input + " " + key + " " + task.arguments[key]
        logger.debug(f"for task({task.task_id}),the command_line_input is {command_line_input}")
        return(command_line_input)
        
    def submit_task(self,task):
        """Job Manager call this method and submit a task. This method will launch the whole procedure (i.e. parse cmd, create container, run exe with phraos and insert result into Resource Manager) of the Execution Manager
    
        Args:
            task (Task): The task from Job Manager
        
        Returns:
            if successful, return true to Job Manager
        """
        logger = Logger().get()
        logger.debug(f"receive task: task_id = {task.task_id}, job_id = {task.job_id}")

        self.commandline_path_parser(task)#this will change task.arguments to the path corresponding to the path inside the container
        
        client = docker.from_env()
    
        container = client.containers.create("felucca/pharos",command="/bin/bash",environment = [f"TASK_ID={task.task_id}"],tty=True,stdin_open=True,auto_remove=False)
        logger.debug(f"successfully create a container : {container.name}")
        self.set_map(task,container)
        
        container.start()

        t = Thread(target=self.run_container_flask, args=(container, ))
        t.start()
        
        #self.copy_to_container(task,task.executable_file,container)
        self.copy_to_container(task,container)
        logger.debug(f"successfully copy exe into container({container.name})")
        
        return(True);
