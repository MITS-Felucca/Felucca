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
            taskNumber: 1,
            jobID: id,
            status: Status.Pending}
  }
}
