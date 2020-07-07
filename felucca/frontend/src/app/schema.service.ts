import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders} from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { map } from 'rxjs/operators';

import { Schema } from './schema';
import { ArgumentClass } from './argument-class';
import { Argument } from './argument';
import { ArgumentType } from './argument-type.enum';


@Injectable()
export class SchemaService {

  private backEndURL = 'http://localhost:5000';

  httpOptions = {
    headers: new HttpHeaders({ 'Content-Type': 'application/json' })
  };

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
          toolID: (schema as any).Tool_ID,
          isPharos: (schema as any).Is_Pharos,
          argumentClasses: classes
        });
      }
      return schemas;
    }));
  }

  getSchemaByID(schemaID: string): Observable<Schema> {
    let url = `${this.backEndURL}/tool/${schemaID}/json`;
    return this.http.get(url).pipe(map(data => {
      console.log(data);
      let classes: ArgumentClass[] = [];
      for (let argumentClass of (data as any).Classes) {
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
      return {
        toolName: (data as any).Tool_Name,
        programName: (data as any).Program_Name,
        toolID: (data as any).Tool_ID,
        isPharos: (data as any).Is_Pharos,
        argumentClasses: classes};
    }));
  }

  deleteSchemaByID(schemaID: string): Observable<boolean> {
    let url = `${this.backEndURL}/tool/${schemaID}/delete`;
    return this.http.get(url).pipe(map(data => {
      return (data as any).Status === 'ok';
    }))
  }

  createSchema(schema: Schema): Observable<boolean> {
    console.log(schema);
    let url = `${this.backEndURL}/tool`;
    let schemaInfo = {
      Tool_Name: schema.toolName,
      Program_Name: schema.programName,
      Is_Pharos: schema.isPharos,
      Classes: []
    };

    for (let argumentClass of schema.argumentClasses) {
      let argumentsInfo = [];
      for (let argumentInfo of argumentClass.arguments) {
        argumentsInfo.push({
          Full_Name: argumentInfo.fullName,
          Abbreviation: argumentInfo.abbreviation,
          Description: argumentInfo.description,
          Is_Required: argumentInfo.isRequired,
          Default_Value: argumentInfo.defaultValue,
          Type: argumentInfo.argumentType
        });
      }
      schemaInfo.Classes.push({
        Name: argumentClass.name,
        Arguments: argumentsInfo
      });
    }

    return this.http.post(url, JSON.stringify(schemaInfo), this.httpOptions).pipe(map(data => {
      return (data as any).Status === 'ok';
    }));
  }

  updateSchema(schema: Schema, schemaID: string): Observable<boolean> {
    let url = `${this.backEndURL}/tool/${schemaID}`;
    let schemaInfo = {
      Tool_Name: schema.toolName,
      Program_Name: schema.programName,
      Is_Pharos: schema.isPharos,
      Classes: []
    };

    for (let argumentClass of schema.argumentClasses) {
      let argumentsInfo = [];
      for (let argumentInfo of argumentClass.arguments) {
        argumentsInfo.push({
          Full_Name: argumentInfo.fullName,
          Abbreviation: argumentInfo.abbreviation,
          Description: argumentInfo.description,
          Is_Required: argumentInfo.isRequired,
          Default_Value: argumentInfo.defaultValue,
          Type: argumentInfo.argumentType
        });
      }
      schemaInfo.Classes.push({
        Name: argumentClass.name,
        Arguments: argumentsInfo
      });
    }

    return this.http.post(url, JSON.stringify(schemaInfo), this.httpOptions).pipe(map(data => {
      return (data as any).Status === 'ok';
    }));
  }

  updatePharos(dockerDir: string): Observable<boolean> {
    let data= {content: dockerDir};
    const url = `${this.backEndURL}/pharos`;
    return this.http.post(url, JSON.stringify(data), this.httpOptions).pipe(map(data => {
        return (data as any).status === 'ok';
      }
    ));
  }

  getUpdateStatus() {
    const url = `${this.backEndURL}/debug/pharos/metadata`;
    return this.http.get(url).pipe(map(data => {
        return {
          isUpdating: (data as any).Is_Updating_Kernel,
          dockerDirectory: (data as any).Docker_Directory,
          digest: (data as any).Digest
        }
      }
    ));
  }
}
