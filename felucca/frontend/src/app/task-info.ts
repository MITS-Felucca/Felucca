export interface TaskInfo {
  files: {[key: string]: string},
  inputFileArguments: {[key: string]: string},
  inputTextArguments: {[key: string]: string},
  inputFlagArguments: string[],
  outputFileArguments: {[key: string]: string},
  toolName: string,
  programName: string
}
