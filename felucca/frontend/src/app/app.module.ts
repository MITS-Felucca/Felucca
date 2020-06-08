import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module'

import { AppComponent } from './app.component';
import { JobInfoComponent } from './job-info/job-info.component';
import { JobListComponent } from './job-list/job-list.component';
import { SubmitJobComponent } from './submit-job/submit-job.component';
import { SubmitTaskComponent } from './submit-task/submit-task.component';
import { JobService } from './job.service';
import { TaskService } from './task.service';


@NgModule({
  imports:      [ BrowserModule, FormsModule, ReactiveFormsModule, AppRoutingModule ],
  declarations: [ AppComponent, JobInfoComponent, JobListComponent, SubmitJobComponent, SubmitTaskComponent ],
  bootstrap:    [ AppComponent ],
  providers: [JobService, TaskService]
})
export class AppModule { }
