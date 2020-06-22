import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FileService } from '../file.service';

@Component({
  selector: 'app-output-display',
  templateUrl: './output-display.component.html',
  styleUrls: ['./output-display.component.css']
})
export class OutputDisplayComponent implements OnInit {
  taskID: string;
  outputType: string;
  content: string;
  constructor(private route: ActivatedRoute, 
              private fileService: FileService) { }

  ngOnInit() {
    this.taskID = this.route.snapshot.paramMap.get('taskID');
    this.outputType = this.route.snapshot.paramMap.get('outputType');
    this.fileService.getOutput(this.taskID, this.outputType).subscribe(
      content => {this.content = content});
  }
}