import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { saveAs } from 'file-saver';
import { FileService } from '../file.service';

@Component({
  selector: 'app-file-display',
  templateUrl: './file-display.component.html',
  styleUrls: ['./file-display.component.css']
})
export class FileDisplayComponent implements OnInit {
  taskID: string;
  filename: string;
  fileType: string;
  content: string;
  constructor(private route: ActivatedRoute, 
              private fileService: FileService) { }

  ngOnInit() {
    this.taskID = this.route.snapshot.paramMap.get('taskID');
    this.filename = this.route.snapshot.paramMap.get('filename');
    this.fileType = this.route.snapshot.paramMap.get('fileType');
    this.fileService.getFile(this.taskID,  this.fileType, this.filename).subscribe(
      content => {this.content = content});
  }

  saveFile() {
    let blob = new Blob([this.content], {type: "text/plain;charset=utf-8"});
    saveAs(blob, this.taskID + "_" + this.filename);
  }
}