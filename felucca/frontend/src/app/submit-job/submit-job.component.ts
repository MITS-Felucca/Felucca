import { Component, OnInit} from '@angular/core';
import { Router } from '@angular/router';

import { TaskInfo } from '../task-info'
import { JobService } from '../job.service';
import { Schema } from '../schema';
import { SchemaService } from '../schema.service';

@Component({
  selector: 'app-submit-job',
  templateUrl: './submit-job.component.html',
  styleUrls: ['./submit-job.component.css']
})
export class SubmitJobComponent implements OnInit{
  name: string;
  comment: string;
  tasks: TaskInfo[];
  schemas: Schema[];
  chosenSchema: Schema;
  chosenIndex: number;

  constructor(private jobService: JobService,
              private schemaService: SchemaService,
              private router: Router) { }

  ngOnInit() {
    this.tasks = [];
    this.schemaService.getSchemas().subscribe(schemas => {this.schemas = schemas;});
    this.chosenSchema = undefined;
    this.chosenIndex = 0;
  }

  submitTask(newTask: TaskInfo) {
    this.tasks.push(newTask);
    this.chosenSchema = undefined;
    this.chosenIndex = 0;
  }

  deleteTask(id: number) {
    this.tasks.splice(id, 1);
  }

  displayAddTaskPage() {
    if (this.chosenIndex !== 0) {
      this.chosenSchema = this.schemas[this.chosenIndex - 1];
    } else {
      this.chosenSchema = undefined;
    }
  }

  submitJob() {
    if (!this.comment) {
      this.comment = '';
    }
    this.jobService.submitJob(this.name, this.comment, this.tasks).subscribe(data => {
      this.router.navigate(['/job-list']);
    });
  }

  isValidJob(): boolean {
    return this.name && this.name.length > 0 && this.tasks.length > 0;
  }
}
