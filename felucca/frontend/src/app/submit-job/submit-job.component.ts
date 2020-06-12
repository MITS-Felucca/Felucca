import { Component, OnInit} from '@angular/core';
import { Router } from '@angular/router';

import { TaskInfo } from '../task-info'
import { JobService } from "../job.service";

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
  chosenTool: string;
  toolNames: string[];

  constructor(private jobService: JobService,
              private router: Router) { }

  ngOnInit() {
    this.isAdding = false;
    this.toolNames = ['', 'ooanalzyer'];
    this.tasks = [];
    this.chosenTool = '';
  }

  submitTask(newTask: TaskInfo) {
    console.log(newTask);
    this.tasks.push(newTask);
    this.isAdding = false;
    this.chosenTool = '';
  }

  deleteTask(id: number) {
    this.tasks.splice(id, 1);
  }

  displayAddTaskPage() {
    this.isAdding = this.chosenTool != '';
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
