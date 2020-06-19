import { ArgumentClass } from './argument-class'

export interface Schema {
  toolName: string;
  programName: string;
  isPharos: boolean;
  argumentClasses: ArgumentClass[];
}
