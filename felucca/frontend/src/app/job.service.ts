import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { map } from 'rxjs/operators';

import { Job } from './job'
import { Task } from './task'
import { Status } from './status.enum'
import { TaskInfo } from './task-info';

@Injectable()
export class JobService {

  private backEndURL = 'http://localhost:5000';

  httpOptions = {
    headers: new HttpHeaders({ 'Content-Type': 'application/json' })
  };

  constructor(private http: HttpClient) { }

  getJobList(): Observable<Job[]> {
    const url = `${this.backEndURL}/job-list/json`;
    return this.http.get(url).pipe(map(data => {
      let jobs = [];
      for (let job of (data as any).Job_List) {
        jobs.push(
          {
            comment: (job as any).Comment,
            jobName: (job as any).Name,
            createdTime: new Date((job as any).Created_Time * 1000),
            finishedTime: new Date((job as any).Finished_Time * 1000),
            taskNumber: (job as any).Task_Number,
            jobID: (job as any).ID,
            status: Status[(job as any).Status]
          }
        )
      }
      return jobs;
    }))
  }

  getJobInfoById(id: string): Observable<{job: Job, tasks: Task[]}> {
    const url = `${this.backEndURL}/job-info/${id}/json`;
    return this.http.get(url).pipe(map(data => {
      let jobInfo = {
        job: {
            comment: (data as any).Comment,
            jobName: (data as any).Name,
            createdTime: new Date((data as any).Created_Time * 1000),
            finishedTime: new Date((data as any).Finished_Time * 1000),
            taskNumber: (data as any).Task_Number,
            jobID: (data as any).ID,
            status: Status[(data as any).Status]
        }, tasks: []};

        for (let task of (data as any).Tasks) {
          jobInfo.tasks.push(
            {
              arguments: (task as any).Arguments,
              outputFilename: (task as any).Output,
              logFilename: (task as any).Log,
              stdout: (task as any).Stdout,
              stderr: (task as any).Stderr,
              finishTime: new Date((task as any).Finished_Time * 1000),
              status: Status[(task as any).Status],
              taskID: (task as any).ID
            }
          )
        }
      return jobInfo;
    }));
  }

  submitJob(jobName: string, jobComment: string, tasks: TaskInfo[]): Observable<boolean> {
    let job = {Job_Name: jobName, Job_Comment: jobComment, Tasks: []};
    for (let task of tasks) {
      job.Tasks.push({Tool_ID: 1, Files: task.files, Arguments: task.arguments})
    }
    const url = `${this.backEndURL}/job`;
    return this.http.post(url, JSON.stringify(job), this.httpOptions).pipe(map(data => {
      return (data as any).Status == 'ok';
      }
    ));
  }
}