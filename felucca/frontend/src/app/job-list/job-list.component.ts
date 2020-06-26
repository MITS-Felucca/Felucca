import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { JobService } from '../job.service';
import { Status } from '../status.enum'
import { Job } from '../job';

@Component({
  selector: 'app-job-list',
  templateUrl: './job-list.component.html',
  styleUrls: ['./job-list.component.css']
})
export class JobListComponent implements OnInit {
  id: string;
  jobs: Job[];
  status = Status;

  constructor(
    private route: ActivatedRoute,
    private jobService: JobService,
    private router: Router
  ) { }

  ngOnInit() {
    this.getJobList();
  }

  getJobList(): void {
    this.jobService.getJobList().subscribe(jobs => {
      this.jobs = jobs;
      this.jobs.sort((a, b) => {
        return a.createdTime.getTime() - b.createdTime.getTime();
      });
    });
  }
}
