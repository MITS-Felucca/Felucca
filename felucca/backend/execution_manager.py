import sys
sys.path.append(r'./common')
import os
import argparse
import shlex
import tarfile
import docker
from common.singleton import Singleton
from threading import Thread

@Singleton
class ExecutionManager(object):
    
    def __init__(self):
        self.map_id2Task_container = {}
        
    def commandline_path_parser(self,task):
        command_line_input = task.command_line_input
        parser = argparse.ArgumentParser()
         
        parser.add_argument('-ooanalyzer', dest="ooanalyzer",action = "store_true",default=False)
        parser.add_argument('-j','--json', dest="j", type = str)
        parser.add_argument('-R','--prolog-results ', dest="R", type = str)
        parser.add_argument('-n','--new-method', dest="n", type = str)
        parser.add_argument('-F','--prolog-facts', dest="F", type = str)
        parser.add_argument('-f','--file', dest="f", type = str)
        #command_line_input = "ooanalyzer --json output.json -F facts -R results --file oo.exe"
        #print(command_line_input)
        if(command_line_input[0]!='-'):
            command_line_input = '-'+command_line_input
                
        a = parser.parse_args(shlex.split(command_line_input))

        dict = vars(a)
        #j F R should be replaced to a defined path
        #f should be the path exe file will be copied into docker
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


        os.chdir(os.path.dirname(src))
        srcname = os.path.basename(src)

        tar = tarfile.open(src + '.tar', mode='w')
        try:
            tar.add(srcname)
        finally:
            tar.close()
    
        data = open(src + '.tar', 'rb').read()
        container_dir = os.path.dirname(dst)
        print(f"container_dir:    {container_dir}")
        container.exec_run("mkdir "+container_dir)
        container.put_archive(container_dir, data)
        
    def set_map(self,task,container):
        #self.map_id_container[task.task_ids] = container
        #self.map_id_Task[task.task_ids] = task
        
        self.map_id2Task_container[task.task_ids] = (task,container)
        return(True);
        
    def run_container_flask(self,container):
        print(f"running: 'flask run --host=0.0.0.0' inside container shell")

        #exec_log = container.exec_run("flask run --host=0.0.0.0" ,stdout=True,stderr=True,stream=True)
        exec_log = container.exec_run("echo \" 666  \" " ,stdout=True,stderr=True,stream=True)

        for line in exec_log[1]:
            print(line)
            
        return(True);    
        
    def get_command_line_input(self, task_id):
        task = self.map_id2Task_container[task_id][0]
        return(task.command_line_input)
        
    def submit_task(self,task):

        #url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=mykeyhere"
    
        exe_path_outside = task.executable_file
        
        
        #print(f"\nexe_path_outside:\n{exe_path_outside}")
        #print(f"\ntask.command_line_input:\n{task.command_line_input}")
        
        
        self.commandline_path_parser(task)#this will change task two attr: task.executable_file & task.command_line_input   to conatiner path version
        
        #print(f"\nadjusted_command_line_input:\n{task.command_line_input}")
        #print(f"\nexe_path_inside:\n{task.executable_file}")
        
        client = docker.from_env()
    
        container = client.containers.create("felucca/pharos",command="/bin/bash",tty=True,stdin_open=True,auto_remove=False)
        
        self.set_map(task,container)
        
        container.start()
        #time.sleep(1) 
        t = Thread(target=self.run_container_flask, args=(container, ))
        t.start()
        
        self.copy_to_container(exe_path_outside,task.executable_file,container)
        
        exec_log = container.exec_run("cat "+task.executable_file,stdout=True,stderr=True,stream=True)
        
        
        for line in exec_log[1]:
            print(line)
        
        print('Container Status : {}'.format(container.status))
        return(True);