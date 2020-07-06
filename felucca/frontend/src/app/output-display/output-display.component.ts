import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { saveAs } from 'file-saver';
import { FileService } from '../file.service';
import { interval } from 'rxjs';
import { takeWhile, map, concatAll } from 'rxjs/operators';
import { Status } from '../status.enum';

@Component({
  selector: 'app-output-display',
  templateUrl: './output-display.component.html',
  styleUrls: ['./output-display.component.css']
})
export class OutputDisplayComponent implements OnInit {
  taskID: string;
  outputType: string;
  content: string;
  status: Status;

  constructor(private route: ActivatedRoute, 
              private fileService: FileService) { }

  ngOnInit() {
    this.taskID = this.route.snapshot.paramMap.get('taskID');
    this.outputType = this.route.snapshot.paramMap.get('outputType');
    this.status = Status.Running;

    interval(1000).pipe(
      takeWhile(() => this.status === Status.Running),
      map(() => this.fileService.getOutput(this.taskID, this.outputType)),
      concatAll(),
    ).subscribe(data => {
      this.status = Status[data['status']];
      this.content = data['content'];
    });
  }

  saveFile() {
    let blob = new Blob([this.content], {type: "text/plain;charset=utf-8"});
    saveAs(blob, this.taskID + "_" + this.outputType);
  }
}
