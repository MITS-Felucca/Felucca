# Felucca
A system providing Pharos tools as a web service

[Automated static analysis tools for binary programs](https://github.com/cmu-sei/pharos.git)

# Felucca Quickstart

## Concept
- `task` : A task is the minimum execution unit in Felucca. It means a single execution using a specific `tool` .
- `job` : A job is a collections of `task` . It may consist of a single task or multiple tasks.
- `tool` : A tool is command line tool that is installed in kernel. It may takes some arguments and input files, then generate output files and text output.
- `schema` : A schema is the metadata of a `tool` , it is made of `argument classes` .
- `argument Class` : An argument class is a collection of `argument` .
- `argument` : An argument consists of the basic information of `argument` . 
   - `Full Name` : The full name of this `argument` , e.g. `--output` 
   - `Abbreviation` : The abbreviation of this `argument` , e.g. `-o` 
   - `Description` : The text description of this `argument` .
   - `isRequired` : A boolean flag to tell if this `argument`  is required when using this tool.
   - `Argument Type` : The type of this argument:
      - `Output file` : If this argument is set, it would output a file to target filename. The default file name of the output file should be given in `Default Value` field, e.g. `--json output.json` 
      - `Input file` : If this argument is set, it means this tool would take a file as input. You need to upload this file.  `-f oo.exe` 
      - `Input flag` : If this argument is set, it means a flag argument, e.g. `--address-only` 
      - `Input Text` : If this argument is set, it means a flag argument followed by its input string, e.g. `--verbose 5` 
   - `Default Value` : When this argument's type is output file, it has a default filename which should be given in this field.



## Job Management
### Job Submission
#### 1. Submit a job with a single task

1. Click `Submit job` button in header.
2. Type the name and comment of your job, job name is required for each job.

![image.png](https://cdn.nlark.com/yuque/0/2020/png/1766657/1594851137018-84e44bb2-97e2-4647-995c-489720372254.png#align=left&display=inline&height=538&margin=%5Bobject%20Object%5D&name=image.png&originHeight=538&originWidth=1903&size=45551&status=done&style=none&width=1903)

3. Choose a tool in the tool list, after you choose a tool, its argument form would appear below.
4. Then, you need to specify the argument of this execution. The save would be disabled until you finish all the required arguments. Note that for different types of argument, its input meaning is different. 
   1. For output file type argument, the checkbox means if you want to see this output file after the execution. 
   2. For input file type argument, you need to upload a file.
   3. For input flag type argument, the checkbox means if you want to include this flag in this execution.
   4. For input text type argument, if you type something in the input text area, it would be given to the tool in this execution. 

![image.png](https://cdn.nlark.com/yuque/0/2020/png/1766657/1594851313584-2fe8771b-b537-4f49-bf3c-345b59686237.png#align=left&display=inline&height=854&margin=%5Bobject%20Object%5D&name=image.png&originHeight=854&originWidth=1884&size=106938&status=done&style=none&width=1884)

5. After you finish specifying the arguments, click `Save` . Then you could view and confirm your task argument in the list below.

![image.png](https://cdn.nlark.com/yuque/0/2020/png/1766657/1594851649867-80955cf6-e301-4800-bc1d-c52983c82420.png#align=left&display=inline&height=543&margin=%5Bobject%20Object%5D&name=image.png&originHeight=543&originWidth=1893&size=54514&status=done&style=none&width=1893)

6. If everything is ok, click `Submit` . Then a popup would show and tells you if your submission is successful or not.
7. Back to the Dashboard, you could find your job in the job list.

![image.png](https://cdn.nlark.com/yuque/0/2020/png/1766657/1594851681547-138f3b8a-07bd-4221-aad1-9bd861d4756c.png#align=left&display=inline&height=119&margin=%5Bobject%20Object%5D&name=image.png&originHeight=119&originWidth=1891&size=20359&status=done&style=none&width=1891)


#### 2. submit a job with multiple tasks

1. You could also add more than one task inside a single job. All you need to do is to choose tool again after you save your first task.

![image.png](https://cdn.nlark.com/yuque/0/2020/png/1766657/1594853364246-6a2d1a35-6215-4e21-8085-b8568bf2eddd.png#align=left&display=inline&height=730&margin=%5Bobject%20Object%5D&name=image.png&originHeight=730&originWidth=1903&size=66443&status=done&style=none&width=1903)
### Job Information
#### 1. Check the status of job and tasks

- The job status are shown in dashboard.
- The task status are shown inside job information page.
- Job Status are defined as below:
   - `Pending` : This job is waiting to be executed.
   - `Running` : This job is running. A job is running if one of its tasks is running.
   - `Finished` : This job is finished. A job is finished if all of its tasks if not pending or running.
- Task Status are defined as below:
   - `Pending` : This task is waiting to be executed.
   - `Running` : This task is running. 
   - `Successful` : A task is successful only if its execution return value is 0.
   - `Failed` : A task is failed if its execution return value is not 0.
   - `Error` : A task is error if some internal error happen inside Felucca, which means this task cannot be executed.
   - `Killed` : A task is killed if user manually kills this task or kills the job it belong.

![image.png](https://cdn.nlark.com/yuque/0/2020/png/1766657/1594854466348-2fdd7c0d-d912-4a0a-892a-2ee74350e847.png#align=left&display=inline&height=843&margin=%5Bobject%20Object%5D&name=image.png&originHeight=843&originWidth=1908&size=95252&status=done&style=none&width=1908)

#### 2. Check the standard output and error message in realtime.

- After a task starts to run, you could check its output in realtime instead of waiting for it to finish. It may help you have a better understanding on what's going on inside this execution.
- Just click `stdout` or `stderr` inside job information page of some task. Then, you could see the realtime output in the output display page. You could also download this output for further use.

![image.png](https://cdn.nlark.com/yuque/0/2020/png/1766657/1594854632490-e5bb401f-9e84-4a69-b862-0d51c09c8356.png#align=left&display=inline&height=718&margin=%5Bobject%20Object%5D&name=image.png&originHeight=718&originWidth=1889&size=62285&status=done&style=none&width=1889)
![image.png](https://cdn.nlark.com/yuque/0/2020/png/1766657/1594854723091-f05843b7-09cd-45fb-b7bb-d898b87a58d3.png#align=left&display=inline&height=934&margin=%5Bobject%20Object%5D&name=image.png&originHeight=934&originWidth=1884&size=213905&status=done&style=none&width=1884)


#### 3. Check the output file of task

- After a task is finished, you could check the output file in the job information page. Click the filename inside the "Arguments" column in that task, you could view the output file in text format.
- You could also download the file in text format using the download button.



### Kill job
#### 1. kill a task

- If you found a task behave unexpectedly, you could kill that task inside the job information page. Felucca would terminate the task and recycle all its resource, but its standard output and error message are reserved. Note that if a task is already finished (succeed or failed) by the time Felucca kills it, it will remain as its current status.
#### 2. kill a job and all tasks inside

- If you found a job behave unexpectedly, you also could kill that job. Killing a job is identical to killing all the tasks inside that job.

![image.png](https://cdn.nlark.com/yuque/0/2020/png/1766657/1594858930535-4e6a3567-247d-48e7-8085-241e670862ac.png#align=left&display=inline&height=764&margin=%5Bobject%20Object%5D&name=image.png&originHeight=764&originWidth=1907&size=61580&status=done&style=none&width=1907)

