import { Status } from "./status.enum";

export interface Task {
  programName: string,
  arguments: {[key: string]: string},
  outputFilename: Set<string>,
  finishTime: Date,
  stdout: boolean,
  stderr: boolean,
  status: Status,
  taskID: string
}
