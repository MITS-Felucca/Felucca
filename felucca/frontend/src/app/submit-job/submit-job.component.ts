import { Component, OnInit} from '@angular/core';

import { SubmitTaskComponent } from '../submit-task/submit-task.component'
import { TaskInfo } from '../task-info'

import { Task } from '../task'

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

  constructor() { }

  ngOnInit() {
    this.isAdding = false;
    this.toolNames = ['ooanalzyer'];
    this.tasks = [];
    this.chosenTool = '';
  }

  submitTask(newTask: TaskInfo) {
    this.tasks.push(newTask);
    this.isAdding = false;
    this.chosenTool = '';
  }

  displayAddTaskPage() {
    if (this.chosenTool != '') {
      this.isAdding = true;
    }
  }
}