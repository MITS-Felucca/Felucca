# -*- coding: utf-8 -*-
"""
Created on Wed May 27 00:42:29 2020

@author: Jack
"""
from common.task import Task
from execution_manager import ExecutionManager


#task = Task("/home/vagrant/Felucca/tests/oo.exe", "meaningless", "ooanalyzer -j output.json -F facts -R results -f foo.txt")
task = Task("/vagrant/Felucca/tests/oo.exe", "meaningless", "ooanalyzer -j output.json -R results -f /vagrant/Felucca/tests/oo.exe")
task.task_ids = '5ed166559fde8c0531988a64'
ExecutionManager().submit_task(task)




