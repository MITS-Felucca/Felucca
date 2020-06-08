import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Job } from '../job';
import { Task } from '../task';
import { JobService } from '../job.service';
import { TaskService } from '../task.service';

@Component({
  selector: 'app-job-info',
  templateUrl: './job-info.component.html',
  styleUrls: ['./job-info.component.css']
})
export class JobInfoComponent implements OnInit {
  job: Job;
  tasks: Task[];
  jobID: string;

  constructor(
    private route: ActivatedRoute,
    private jobService: JobService,
    private taskService: TaskService
  ) { }

  ngOnInit() {
    this.jobID = this.route.snapshot.paramMap.get('jobID');
    this.getJob();
    this.getTasks();
  }

  getJob(): void {
    this.job = this.jobService.getJob(this.jobID);
  }

  getTasks(): void {
    this.tasks = this.taskService.getTasks(this.jobID);
  }
}
