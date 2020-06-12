import {Component, Inject, OnInit} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

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
    private route: ActivatedRoute,
    private jobService: JobService,
    private router: Router
  ) {
  }

  ngOnInit() {
    this.jobID = this.route.snapshot.paramMap.get('jobID');
    this.jobService.getJobInfoById(this.jobID).subscribe(jobInfo => {
      this.job = jobInfo.job;
      this.tasks = jobInfo.tasks;
    });
  }

  goToFile(taskID: string, filetype: string, filename: string): void {
    const url = this.router.serializeUrl(
      this.router.createUrlTree(['/task', taskID, filetype, filename])
    );
    window.open(url, '_blank');
    
  }
}
