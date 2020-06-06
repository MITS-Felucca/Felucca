import { Injectable } from '@angular/core';
import { Task } from './task'
import { Status } from './status.enum'


@Injectable()
export class TaskService {

  constructor() { }

  getTasks(id: string): Task[] {
    return [
      {
        commandInput: 'ooanalyzer ..',
        inputFilename: ['oo.exe'],
        outputFilename: ['output.json'],
        logFilename: ['facts', 'results'],
        finishTime: new Date(),
        stdout: 'stdout',
        stderr: 'stderr',
        status: Status.Successful,
        taskID: '1'
      },
      {
        commandInput: 'ooanalyzer ..',
        inputFilename: ['oo.exe'],
        outputFilename: ['output.json'],
        logFilename: ['facts', 'results'],
        finishTime: new Date(),
        stdout: 'stdout',
        stderr: 'stderr',
        status: Status.Successful,
        taskID: '1'
      }
    ]
  }
}
