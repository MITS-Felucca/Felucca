import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { JobService } from '../job.service';
import { TaskService } from '../task.service';

@Component({
  selector: 'app-job-info',
  templateUrl: './job-info.component.html',
  styleUrls: ['./job-info.component.css']
})
export class JobInfoComponent implements OnInit {
  id: string
  constructor(
    private route: ActivatedRoute,
    private jobService: JobService,
    private taskService: TaskService
  ) { }

  ngOnInit() {
    this.getId()
  }

  getId(): void {
    this.id = this.route.snapshot.paramMap.get('job_id');
  }

}
