import { Status } from "./status.enum";

export interface Task {
  arguments: {[key: string]: string},
  outputFilename: string[],
  logFilename: string[],
  stdout: string,
  stderr: string,
  finishTime: Date,
  status: Status,
  taskID: string
}
