import { Injectable } from '@angular/core';
import { HttpClient} from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { map } from 'rxjs/operators';

import { Schema } from './schema';
import { ArgumentClass } from './argument-class';
import { Argument } from './argument';
import { ArgumentType } from './argument-type.enum';


@Injectable()
export class SchemaService {

  private backEndURL = 'http://localhost:5000';

  constructor(private http: HttpClient) { }

  getSchemas(): Observable<Schema[]> {
    let url = `${this.backEndURL}/tool-list/json`;
    return this.http.get(url).pipe(map(data => {
      let schemas: Schema[] = [];
      for (let schema of (data as any).Schemas) {
        let classes: ArgumentClass[] = [];
        for (let argumentClass of (schema as any).Classes) {
          let toolArguments: Argument[] = [];
          for (let argument of (argumentClass as any).Arguments) {
            let key: string;
            if ((argument as any).Abbreviation === '') {
              key = (argument as any).Full_Name;
            } else {
              key = (argument as any).Abbreviation;
            }
            toolArguments.push({
              key: key,
              fullName: (argument as any).Full_Name,
              abbreviation: (argument as any).Abbreviation,
              description: (argument as any).Description,
              isRequired: (argument as any).Is_Required,
              defaultValue: (argument as any).Default_Value,
              argumentType: (argument as any).Type as ArgumentType
            });
          }
          classes.push({
            name: (argumentClass as any).Name,
            arguments: toolArguments
          });
        }
        schemas.push({
          toolName: (schema as any).Tool_Name,
          programName: (schema as any).Program_Name,
          isPharos: (schema as any).Is_Pharos,
          argumentClasses: classes
        });
      }
      return schemas;
    }));
  }

}