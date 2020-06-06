import { Status } from "./status.enum";

export interface Job {
  jobName: string;
  comment: string;
  createdTime: Date;
  taskNumber: number;
  jobID: string,
  status: Status
}
