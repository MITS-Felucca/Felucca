import { Injectable } from '@angular/core';
import { Task } from './task';
import { Status } from './status.enum';


@Injectable()
export class TaskService {

  constructor() { }

  getTasks(id: string): Task[] {
    // TODO call real back end API
    return [
      {
        commandInput: 'ooanalyzer ..',
        inputFilename: ['o1.exe'],
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
        inputFilename: ['oo.exe', 'sig.json'],
        outputFilename: ['output.json', 'output2.json'],
        logFilename: ['facts'],
        finishTime: new Date(),
        stdout: 'STDOUT',
        stderr: 'STDERR',
        status: Status.Successful,
        taskID: '2'
      },
      {
        commandInput: 'ooanalyzer ..',
        inputFilename: ['oo.exe'],
        outputFilename: [],
        logFilename: [],
        finishTime: new Date(),
        stdout: 'STDOUT',
        stderr: 'STDERR',
        status: Status.Killed,
        taskID: '3'
      }
    ]
  }
}
