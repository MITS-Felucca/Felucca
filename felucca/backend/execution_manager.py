import os
import tarfile
import docker
import sys
from threading import Thread
from common.singleton import Singleton
from resource_manager import ResourceManager
from status import Status
from logger import Logger
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
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

    def save_result(self, task_id, status):
        """save the result from container to the database

        Args:
            task_id (str): the result under this task_id
            status (str): the task status (Status.Successful.name or Status.Failed.name)
            stderr (byte[]): the output in std error
            stdout (byte[]): the output in std out
        """
        from job_manager import JobManager
        logger = Logger().get()
        logger.debug(f"start save_result: task_id: {task_id} status: {status}")
        print(f"start save_result: task_id: {task_id} status: {status}")
        if status == Status.Successful.name:
            try:
                output_path = self.id_to_task_container[task_id][0].output
                container = self.id_to_task_container[task_id][1]
            except Exception as e:
                logger.info(f"exception for finding container correspoding to {task_id}, status:{status} maybe the container is forced killed before, {e}")
                ResourceManager().save_result(task_id, [])
                ResourceManager().update_task_status(task_id, Status.Killed)
            else:
                self.id_to_task_container.pop(task_id, None)
                try:
                    # get result from container
                    container.exec_run("tar -cvf {}.docker {}".format(task_id, " ".join(output_path)))
                    bits, stat = container.get_archive(f"{task_id}.docker")
                    path = f"/tmp/Felucca/result/{task_id}"
                    if not os.path.exists(path):
                        os.makedirs(path)
                    file = open(f"{path}/{task_id}.tar", "wb+")
                    for chunk in bits:
                        file.write(chunk)
                    file.close()
                    # extract result tar file
                    result_tar = tarfile.open(f"{path}/{task_id}.tar","r")
                    result_tar.extractall(path)
                    result_tar.close()
                    result_tar = tarfile.open(f"{path}/{task_id}.docker","r")
                    result_tar.extractall(path)
                    result_tar.close()
                    #delete temp tar file after extraction
                    os.remove(f"{path}/{task_id}.tar")
                    os.remove(f"{path}/{task_id}.docker")
                    logger.debug(f"for task:{task_id} execute and exit normally")
                except Exception as e:
                    logger.error(f"exception at copying result out of container and extrating the file for {task_id}, {e}")
                    ResourceManager().save_result(task_id, [])
                    ResourceManager().update_task_status(task_id, Status.Failed)
                    container.stop()
                    container.remove()
                else:
                    for index in range(len(output_path)):
                        output_path[index] = os.path.join(path, output_path[index])
                        print(output_path[index])
                    ResourceManager().save_result(task_id, output_path)
                    ResourceManager().mark_task_as_finished(task_id)
                    JobManager().finish_task(task_id)
                    container.stop()
                    container.remove()
        elif status == Status.Failed.name:
            ResourceManager().save_result(task_id, [])
            ResourceManager().update_task_status(task_id, Status.Failed)
            JobManager().finish_task(task_id)
            try:
                output_path = self.id_to_task_container[task_id][0].output
                container = self.id_to_task_container[task_id][1]
            except Exception as e:
                logger.info(f"exception for finding container correspoding to {task_id}, status:{status}, maybe the container is forced killed before, {e}")
            else:
                self.id_to_task_container.pop(task_id, None)
                container.stop()
                container.remove()
                logger.debug(f"for task:{task_id}, can't run cmd normally, exit normally")



    def set_attr(self,task):
        
        """change a task's arguments corresponding to the exe path inside tge container
        For input file, the absolute path is the same as input file outside the container, i.e. "/tmp/Felucca/{task.task_id}/{input_filename}"
        For output file path, the absolute path is "/tmp/Felucca/{task.task_id}/{output_filename}"
        
        Args:
            task (Task): The task object to be executed
        
        """
        #change the input file path
        logger = Logger().get()
        task.output = []
        
        task_file_path = os.path.join("/tmp/Felucca", f"{task.task_id}")
        if not os.path.exists(task_file_path):
            os.makedirs(task_file_path)
        
        for key, value in task.output_file_args.items():
            #task.output_file_args[key]  = os.path.join(task_file_path,task.output_file_args[key])
            task.output.append(task.output_file_args[key])
        
        for key in task.input_file_args:
            task.input_file_args[key]  = os.path.join(task_file_path,task.input_file_args[key])
        
        logger.debug(f"for task({task.task_id}),set_task_output: {task.output}")
        
    def copy_to_container(self,task,container):
        
        """copy executable_file into the container
            this method will copy the input file from "task.files[key]" at backend to "task.files[key]" ( i.e. the same dst becasue this path is unique for each task) inside the given conatiner
    
        Args:
            task (Task): task object which conatiner the absolute exe file path currently (i.e. each task.files[key])
            container (Container): the docker container created to run this task 
        
        """
        logger = Logger().get()

        print(task.task_id)
        
        for filename, path in task.files.items():
            print(f"src and dst: {path}")
            src = path
            dst = src

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
            _, r = container.exec_run("ls " + container_dir, stdout=True, stream=True)
            for line in r:
                print(line)

            
            #delete local tar and exe file
            if(os.path.exists(path)):
                os.remove(path)
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
        logger = Logger().get()
        task = self.id_to_task_container[task_id][0]

        task_file_path = os.path.join("/tmp/Felucca", f"{task.task_id}")
        if not os.path.exists(task_file_path):
            os.makedirs(task_file_path)
            
        cmd = task.program_name
        for key, value in task.input_file_args.items():
            cmd += " " + key + " " + value
            
        for key, value in task.input_text_args.items():
            cmd += " " + key + " " + value
            
        for key, value in task.output_file_args.items():
            cmd += " " + key + " " + value
            
        for value in task.input_flag_args:
            cmd += " " + value
        
        print(f"cmd: {cmd}")
            
        logger.debug(f"for task({task.task_id}),the command_line_input is {cmd}")
        return(cmd)
    def kill_task(self, task_id):
        """try to kill and remove the container correspoding to the given task_id, if succeed, update the status at RM
    
        Args:
            task_id (Task): The id of the task

        """
        logger = Logger().get()
        try:
            container = self.id_to_task_container[task_id][1]
            container.stop()
            container.remove()
            self.id_to_task_container.pop(task_id, None)
            ResourceManager().update_task_status(task_id, Status.Killed)
            from job_manager import JobManager
            JobManager().finish_task(task_id)
        except Exception as e:
            logger.error(f"try to kill {task_id}'s container fail, maybe the container is not existed or already killed, exception: {e}")
     
    
    def submit_task(self,task):
        """Job Manager call this method and submit a task. This method will launch the whole procedure (i.e. parse cmd, create container, run exe with phraos and insert result into Resource Manager) of the Execution Manager
    
        Args:
            task (Task): The task from Job Manager
        
        Returns:
            if successful, return true to Job Manager
        """
        logger = Logger().get()
        logger.debug(f"receive task: task_id = {task.task_id}, job_id = {task.job_id}")

        self.set_attr(task)#this will change task.arguments to the path corresponding to the path inside the container
        
        client = docker.from_env()
    
        container = client.containers.create("felucca/pharos",command="/bin/bash",environment = [f"TASK_ID={task.task_id}"],tty=True,stdin_open=True,auto_remove=False)
        logger.debug(f"successfully create a container : {container.name}")
        self.set_map(task,container)
        
        container.start()

        self.copy_to_container(task,container)
        logger.debug(f"successfully copy exe into container({container.name})")

        ResourceManager().update_task_status(task.task_id, Status.Running)

        t = Thread(target=self.run_container_flask, args=(container, ))
        t.start()


        #self.copy_to_container(task,task.executable_file,container)

        return(True)

    def update_kernel(self,BASE_IMAGE="seipharos/pharos:latest"):
        """
        Pull the latest seipharos/pharos from docker hub and build a new image using the latest pulled seipharos/pharos, Back-end will used latest tool hereafter
        
        WARNING: this method will kill all of the current running tasks
        Procedure:

            1. Pull image according to the BASE_IMAGE String
            2. update Stirng-digest to RM
            3. Tag pulled image to "felucca/temp:latest"
            4. Build felucca/pharos with "felucca/temp:latest" using "DockerFile_for_updating"
            5. Remove all images except : 1.felucca/temp:latest 2.felucca/pharos:latest
        
        this method should be called from Front-end when users want to update the Phraos tool the container used in the Back-end
        """
        logger = Logger().get()
        logger.debug(f"receive request to update kernel from fetching {BASE_IMAGE}")
        ResourceManager().set_updating_kernel(True)
        client = docker.from_env()
        print("updating kernel")
        
        #pull the BASE_IMAGE FROM docker hub
        
        #handle different possible forms of input image name
        try:
            repository, tag = BASE_IMAGE.split(":")
        except:
            repository = BASE_IMAGE
            tag = "latest"

        try:
            pull_image = client.images.pull(repository=repository,tag=tag)
        except:
            logger.error(f"cannot pull image: {repository}:{tag}")
        else:
            logger.debug(f"image: {repository}:{tag} successfully")
            
            #truncate the digest after the ":", here the list attrs['RepoDigests'] should only have one String element like BASE_IMAGE@sha256:xxxxxxx
            try:
                digest = pull_image.attrs['RepoDigests'][0].split(":")[1]
            except:
                digest = pull_image.attrs['RepoDigests'][0]
                
            #update Stirng-digest to RM
            logger.debug(f"send metadata repository: {BASE_IMAGE}, digest: {digest} to RM")
            ResourceManager().set_kernel_metadata(BASE_IMAGE,digest)
            
            pull_image.tag("felucca/temp", tag="latest")
            
            logger.debug(f"kill all current tes because of updating")
            #try killing all the tasks currently running
            
            # for task_id in list(self.id_to_task_container):
            #     self.kill_task(task_id)


            fname = os.path.join(os.path.dirname(__file__), '../../DockerFile_for_updating')
            abs_fname = os.path.abspath(fname)
            base_dir = os.path.dirname(abs_fname)

            logger.debug(f"build new image felucca/pharos:latest from {BASE_IMAGE}")
            try:
                logger.debug(f"abs_fname:{abs_fname}, base_dir: {base_dir}")
                built_image, build_output = client.images.build(path=base_dir, dockerfile=abs_fname, tag="felucca/pharos:latest", rm=True, buildargs={"BASE_IMAGE":BASE_IMAGE})
                
                for line in build_output:
                    print(line)
            except Exception as e:
                logger.error("update kernel fail, use previous kernel Error:" + str(e))
            else:    
                logger.debug(f"update kernel successfully, the new felucca/pharos:latest is based on {BASE_IMAGE}")
                '''
                keep_list = ["felucca/temp:latest","felucca/pharos:latest","sonarqube::latest"]
                for image in client.images.list():
                    for image_name in image.attrs['RepoTags']:
                        if image_name not in keep_list:
                            client.images.remove(image_name)
                '''
                client.images.remove(f"{repository}:{tag}")
            #remove all the image with <none> tag
            client.images.prune()

        ResourceManager().set_updating_kernel(False)

        
        
