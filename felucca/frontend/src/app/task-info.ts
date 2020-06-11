export interface TaskInfo {
  files: {[key: string]: string},
  arguments: {[key: string]: string},
  toolName: string
}
