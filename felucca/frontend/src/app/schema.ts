import { ArgumentClass } from './argument-class'

export interface Schema {
  toolName: string;
  programName: string;
  toolID: string;
  isPharos: boolean;
  argumentClasses: ArgumentClass[];
}