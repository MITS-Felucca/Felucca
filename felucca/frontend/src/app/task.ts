import { Status } from "./status.enum";

export interface Task {
  programName: string,
  arguments: {[key: string]: string},
  outputFilename: Set<string>,
  finishTime: Date,
  status: Status,
  taskID: string
}
