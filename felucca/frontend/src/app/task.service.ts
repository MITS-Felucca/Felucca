import { Injectable } from '@angular/core';
import { Task } from './task';
import { Status } from './status.enum';


@Injectable()
export class TaskService {

  constructor() { }

  getTasks(id: string): Task[] {
    return [
      {
        arguments: {'tool': 'ooanalyzer', '-f': 'o1.exe', 
        '-j': 'output.json', '-R': 'result', '-F': 'facts'},
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
        arguments: {'tool': 'ooanalyzer', '-f': 'o1.exe', 
        '-j': 'output.json', '-s': 'sig.json', '-F': 'facts'},
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
        arguments: {'tool': 'ooanalyzer', '-f': 'oo.exe'},
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