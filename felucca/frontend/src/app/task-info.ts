export interface TaskInfo {
  files: {[key: string]: Blob},
  arguments: {[key: string]: any},
  toolName: string
}