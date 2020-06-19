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
  isAdding: boolean;
  tasks: TaskInfo[];
  schemas: Schema[];
  chosenSchema: Schema;
  chosenIndex: number;
  toolNames: string[];

  constructor(private jobService: JobService,
              private schemaService: SchemaService,
              private router: Router) { }

  ngOnInit() {
    this.isAdding = false;
    this.tasks = [];
    this.schemaService.getSchemas().subscribe(schemas => {this.schemas = schemas;});
    this.chosenSchema = undefined;
    this.chosenIndex = 0;
  }

  submitTask(newTask: TaskInfo) {
    console.log(newTask);
    this.tasks.push(newTask);
    this.isAdding = false;
    this.chosenSchema = undefined;
    this.chosenIndex = 0;
  }

  deleteTask(id: number) {
    this.tasks.splice(id, 1);
  }

  displayAddTaskPage() {
    if (this.chosenIndex !== 0) {
      this.isAdding = true;
      this.chosenSchema = this.schemas[this.chosenIndex - 1];
    }
  }

  submitJob() {
    if (!this.comment) {
      this.comment = '';
    }
    this.jobService.submitJob(this.name, this.comment, this.tasks).subscribe();
    this.router.navigate(['/job-list']);
  }

  isValidJob(): boolean {
    return this.name && this.name.length > 0 && this.tasks.length > 0;
  }
}
