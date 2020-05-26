import sys
sys.path.append(r'../common')
import os
import argparse
import shlex
import tarfile



class ExecutionManager(object):
    
    def command_line_input_parser(self,command_line_input):
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
        #print(vars(a))
        dict = vars(a)
        #j F R should be replaced to a defined path
        if 'j' in dict:
            dict['j'] = "/tmp"+'/'+dict['j']
        if 'F' in dict:
            dict['F'] = "/tmp"+'/'+dict['F']
        if 'R' in dict:
            dict['R'] = "/tmp"+'/'+dict['R']
        
        new_command_line_input = ""
        for key in dict:
            if type(dict[key])==bool:
                new_command_line_input = new_command_line_input+key+" "
            elif dict[key] is not None:
                new_command_line_input = new_command_line_input+"-"+key+" "+dict[key]+" "
                
        
        #print(new_command_line_input)
        return(new_command_line_input)
        
    def copy_to_container(self,src,dst,container):
        #name, dst = dst.split(':')
        #print(f"src:{src}")
        os.chdir(os.path.dirname(src))
        srcname = os.path.basename(src)
        #print(f"srcname:{srcname}")
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