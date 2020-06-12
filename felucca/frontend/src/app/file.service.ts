import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable()
export class FileService {

  private backEndURL = 'http://localhost:5000';

  constructor(private http: HttpClient) { }

  getFile(taskID: string, filetype: string, filename: string): Observable<string> {
    let url = `${this.backEndURL}/task/${taskID}/${filetype}/${filename}/json`;
    return this.http.get(url).pipe(map(data => {
      return (data as any).Content;
    }));
  }
}
