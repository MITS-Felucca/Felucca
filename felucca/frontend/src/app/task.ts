import { Status } from "./status.enum";

export interface Task {
  commandInput: string,
  inputFilename: string[],
  outputFilename: string[],
  logFilename: string[],
  stdout: string,
  stderr: string,
  finishTime: Date,
  status: Status,
  taskID: String
}