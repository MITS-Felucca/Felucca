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

## Tool Management
### Browse all available tools
By clicking on the `Tool List` button in the upper left corner, all available tools will be shown. Initially there are 10 tools from the current version of Pharos, which are manually added by us. 

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594947316602-3f5734dd-1542-4cf6-a6e2-509d9b8168c7.png#align=left&display=inline&height=829&margin=%5Bobject%20Object%5D&name=image.png&originHeight=829&originWidth=1353&size=66146&status=done&style=none&width=1353">
</p>

### Edit the schema of existing tools
For each tool, we use `schema` to store its metadata, including `Tool Name`, `Program Name`, `Parameters` etc. To edit a schema, just click the yellow `Edit` button under `Operation` column. Then we can modify the schema of the tool in the page like the figure below.

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594947087452-311841e5-0ec3-484e-9574-89032cf063b5.png#align=left&display=inline&height=902&margin=%5Bobject%20Object%5D&name=image.png&originHeight=902&originWidth=1341&size=85373&status=done&style=none&width=1341">
</p>

To make the schema more clear, **parameters **can be organized into **classes**. Each class contains a list of parameters. Besides, each parameter contains its `Full Name`, `Abbreviation`, `Description`, `IsRequired` flag and its `Argument Type`. For the `Full Name` and `Abbreviation`, the parameter should have at least one of them to make it valid. They will be used during the construction of the command.
There are **four types** of parameters: 

- **Input_File_Args**: This represents a file as input. We need to specify a file for parameters of this type.
- **Input_Flag_Args**: Parameters of this type contain nothing else but themselves. 
- **Input_Text_Args**: In CLI, this type of parameters are followed by its value. For example, parameter "--verbose" requires a number as its value, which stands for the logging level.
- **Output_File_Args**: Parameters of this type mean that they will produce some result as files. And they will have another input box for the name of the output file. (_The file name is required_)

The explanation of these four types will be shown in the hover as below.

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1595040812635-28437f92-9b40-4a17-9948-089aa10e57bc.png#align=left&display=inline&height=252&margin=%5Bobject%20Object%5D&name=image.png&originHeight=252&originWidth=344&size=13740&status=done&style=none&width=344">
</p>

After all modification, click the `Save` button in the bottom to save your work.

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594946578879-7c775b4f-bf44-408b-aad1-6818c9e3fb18.png#align=left&display=inline&height=320&margin=%5Bobject%20Object%5D&name=image.png&originHeight=320&originWidth=696&size=15265&status=done&style=none&width=696">
</p>

### Creating a new schema for new tools
To create a new schema, just click the create the `Create` button in the upper right corner of the `Tool List` page. By default, it will **create a brand new one**("Start from scratch"). Then you can fill in the `Tool Name`, `Program Name`, `Parameters`.

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594946623847-c5434f3a-0ae3-47f0-8e9d-c7b6acb83fb5.png#align=left&display=inline&height=352&margin=%5Bobject%20Object%5D&name=image.png&originHeight=352&originWidth=572&size=18896&status=done&style=none&width=572">
</p>
<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594945536873-0f814e71-7536-4f2f-8424-ded6c72310ff.png#align=left&display=inline&height=466&margin=%5Bobject%20Object%5D&name=image.png&originHeight=466&originWidth=1364&size=33821&status=done&style=none&width=1364">
</p>

Other than that, you can click and **choose an existing tool as your starting point**. Under such a situation, it will automatically import all parameters of the chosen tool, leaving only the `Tool Name` and `Program Name` fields empty.

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594945624841-3b2ce66c-8992-4cb0-b38a-60f21f0ad382.png#align=left&display=inline&height=339&margin=%5Bobject%20Object%5D&name=image.png&originHeight=339&originWidth=327&size=16391&status=done&style=none&width=327">
</p>

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594945690262-1dc247d9-84b9-4f64-b023-a5658cb130a6.png#align=left&display=inline&height=905&margin=%5Bobject%20Object%5D&name=image.png&originHeight=905&originWidth=1346&size=74266&status=done&style=none&width=1346">
</p>

### Export & Import Schemas
In case that the service needs to be migrated, we provide a convenient way to **export **and **import **the schemas. By clicking the blue "Download" button, the schema will be **downloaded as a json file**. 

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594946159847-f4fea44a-a031-425d-aa86-dd20f8ef22ea.png#align=left&display=inline&height=194&margin=%5Bobject%20Object%5D&name=image.png&originHeight=194&originWidth=721&size=11095&status=done&style=none&width=721">
</p>

To **import a schema** from the exported files, create a new tool first. Then click the upper right `Browse` button to choose an exported json file. Seconds after that, all metadata of the exported tool will be loaded. Don't forget to click "`Save`" in the bottom to finish the import.

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594946627869-d47094db-94c4-4deb-b2c8-787576b8094e.png#align=left&display=inline&height=352&margin=%5Bobject%20Object%5D&name=image.png&originHeight=352&originWidth=572&size=18896&status=done&style=none&width=572">
</p>

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594946473991-0cdd6a50-95b9-410c-b719-8391efab31b3.png#align=left&display=inline&height=241&margin=%5Bobject%20Object%5D&name=image.png&originHeight=241&originWidth=572&size=13980&status=done&style=none&width=572">
</p>

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594946798204-79c251b3-9fd3-4e49-88e4-f70b3d10469f.png#align=left&display=inline&height=877&margin=%5Bobject%20Object%5D&name=image.png&originHeight=877&originWidth=1330&size=79107&status=done&style=none&width=1330">
</p>

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594946578879-7c775b4f-bf44-408b-aad1-6818c9e3fb18.png#align=left&display=inline&height=320&margin=%5Bobject%20Object%5D&name=image.png&originHeight=320&originWidth=696&size=15265&status=done&style=none&width=696">
</p>

### Remove tools
To remove a tool, just click the `Remove` button in the tool list. After that, the tool will still exist until you confirm the deletion in the dialog.

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594946950388-c4fd7347-d234-4afd-b06e-5a09445010d0.png#align=left&display=inline&height=188&margin=%5Bobject%20Object%5D&name=image.png&originHeight=188&originWidth=704&size=10337&status=done&style=none&width=704">
</p>

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594946997112-cfb0b07b-19f1-44a6-b0b7-7d094fb815d1.png#align=left&display=inline&height=181&margin=%5Bobject%20Object%5D&name=image.png&originHeight=181&originWidth=515&size=9797&status=done&style=none&width=515">
</p>

## Updating Pharos Docker Image
Considering that _Pharos _keeps evolving, we provide a function to retrieve the latest _Pharos _docker image from _Docker Hub_. Normally, the registry and digest value of current docker image is shown in the top. You can click the `Update Pharos` button to update the docker image. 

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594948133693-bc3f7079-433d-4d72-b102-a8c1333a1d3e.png#align=left&display=inline&height=147&margin=%5Bobject%20Object%5D&name=image.png&originHeight=147&originWidth=588&size=13617&status=done&style=none&width=588">
</p>

After that, a dialog will be shown and the registry of the new image is required. You can leave it empty, and it will use _seipharos/pharos:latest _as the default value. Remember that all running jobs will get killed once the update process begins.

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594948221269-6f121e92-7c89-4572-8323-0fbf140ea595.png#align=left&display=inline&height=275&margin=%5Bobject%20Object%5D&name=image.png&originHeight=275&originWidth=518&size=14607&status=done&style=none&width=518">
</p>

During update process, submitting new jobs is not allowed. And the `Update Pharos` button is replaced by "Pharos Updating". When it finishes, the `Update Pharos` button will be back, and the digest value will be the one of the latest image.

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594948457199-b906fa41-35a3-49d7-bfd2-09c8a0b40dcd.png#align=left&display=inline&height=146&margin=%5Bobject%20Object%5D&name=image.png&originHeight=146&originWidth=622&size=9649&status=done&style=none&width=622">
</p>

<p align="center">
<img src="https://cdn.nlark.com/yuque/0/2020/png/350676/1594948690651-c0fc6fd0-4669-4398-8069-23d819b45b47.png#align=left&display=inline&height=152&margin=%5Bobject%20Object%5D&name=image.png&originHeight=152&originWidth=562&size=9111&status=done&style=none&width=562">
</p>


