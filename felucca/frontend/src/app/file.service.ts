import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable()
export class FileService {

  private backEndURL = 'http://localhost:5000';

  constructor(private http: HttpClient) { }

  getFile(taskID: string, fileType: string, filename: string): Observable<string> {
    let url = `${this.backEndURL}/task/${taskID}/${fileType}/${filename}/json`;
    return this.http.get(url).pipe(map(data => {
      return (data as any).Content;
    }));
  }

  getOutput(taskID: string, outputType: string): Observable<string> {
    let url = `${this.backEndURL}/task/${taskID}/${outputType}/json`;
    return this.http.get(url).pipe(map(data => {
      return (data as any).Content;
    }));
  }
}
