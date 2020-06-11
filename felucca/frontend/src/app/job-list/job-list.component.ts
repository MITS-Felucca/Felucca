import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { JobService } from '../job.service';

import { Job } from '../job';

@Component({
  selector: 'app-job-list',
  templateUrl: './job-list.component.html',
  styleUrls: ['./job-list.component.css']
})
export class JobListComponent implements OnInit {
  id: string
  jobs: Job[]
  constructor(
    private route: ActivatedRoute,
    private jobService: JobService,
  ) { }

  ngOnInit() {
    this.getAllJob()
  }

  getAllJob(): void {
    this.jobs = this.jobService.getAllJob()
  }

  goTo(jobID: String): void {
    
  }
}