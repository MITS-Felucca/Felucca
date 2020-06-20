import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
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
}