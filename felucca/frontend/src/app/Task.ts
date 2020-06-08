import { Status } from "./status.enum";

export interface Task {
  arguments: {[key: string]: string},
  inputFilename: string[],
  outputFilename: string[],
  logFilename: string[],
  stdout: string,
  stderr: string,
  finishTime: Date,
  status: Status,
  taskID: String
}
