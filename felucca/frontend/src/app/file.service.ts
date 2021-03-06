import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, interval } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../environments/environment'

@Injectable()
export class FileService {

  private backEndURL = environment.backendUrl;

  constructor(private http: HttpClient) { }

  getFile(taskID: string, fileType: string, filename: string): Observable<string> {
    let url = `${this.backEndURL}/task/${taskID}/${fileType}/${filename}/json`;
     return this.http.get(url).pipe(map(data => {
      return (data as any).Content;
    }));
  }

  getOutput(taskID: string, outputType: string): Observable<{[key: string]: string}> {
    let url = `${this.backEndURL}/task/${taskID}/${outputType}/json`;

    return this.http.get(url).pipe(map(data => {
      return {
        content: (data as any).Content,
        status: (data as any).Status
      }
    }));
  }
}
