import {Component, Inject, OnInit} from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DOCUMENT } from '@angular/common';

import { Job } from '../job';
import { Task } from '../task';
import { JobService } from '../job.service';
import { Status } from "../status.enum";

@Component({
  selector: 'app-job-info',
  templateUrl: './job-info.component.html',
  styleUrls: ['./job-info.component.css']
})
export class JobInfoComponent implements OnInit {
  job: Job;
  tasks: Task[];
  jobID: string;
  status = Status;

  constructor(
    @Inject(DOCUMENT) private document: Document,
    private route: ActivatedRoute,
    private jobService: JobService,
  ) {
  }

  ngOnInit() {
    this.jobID = this.route.snapshot.paramMap.get('jobID');
    this.jobService.getJobInfoById(this.jobID).subscribe(jobInfo => {
      this.job = jobInfo.job;
      this.tasks = jobInfo.tasks;
    });
  }

  goTo(taskID: string, type: string, fileName: string) {
    this.document.location.href = `http://localhost:5000/task/${taskID}/${type}/${fileName}/json`;
  }
}
