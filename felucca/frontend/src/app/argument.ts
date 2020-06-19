import { ArgumentType } from "./argument-type.enum";

export interface Argument {
  key: string;
  fullName: string | undefined;
  abbreviation: string | undefined;
  description: string;
  isRequired: boolean;
  defaultValue: string | undefined;
  argumentType: ArgumentType;
}