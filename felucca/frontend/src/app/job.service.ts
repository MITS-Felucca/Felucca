import { Injectable } from '@angular/core';
import { Job } from './job'
import { Status } from './status.enum'

@Injectable()
export class JobService {

  constructor() { }

  getJob(id: string): Job {
    return {jobName: 'job-1', 
            comment: 'test job', 
            createdTime: new Date(), 
            taskNumber: 2, 
            jobID: id, 
            status: Status['Pending']}
  }
  getAllJob(): Job[] {
    // TODO call real back end API
    return [
      {
        jobName: 'job-1', 
        comment: 'test job', 
        createdTime: new Date(), 
        taskNumber: 1, 
        jobID: "1", 
        status: Status.Successful
      },
      {
        jobName: 'job-2', 
        comment: 'test job', 
        createdTime: new Date(), 
        taskNumber: 2, 
        jobID: "2", 
        status: Status.Pending
        },
      {
        jobName: 'job-3', 
        comment: 'test job', 
        createdTime: new Date(), 
        taskNumber: 3, 
        jobID: "3", 
        status: Status.Killed
        }
      ]
  }
}