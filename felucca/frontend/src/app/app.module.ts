import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module'

import { AppComponent } from './app.component';
import { HelloComponent } from './hello.component';
import { JobListComponent } from './job-list/job-list.component';

import { JobInfoComponent } from './job-info/job-info.component';
import { JobService } from './job.service';
import { TaskService } from './task.service';
import { SubmitJobComponent } from './submit-job/submit-job.component';
import { SubmitTaskComponent } from './submit-task/submit-task.component';
import {NgbModule} from '@ng-bootstrap/ng-bootstrap';

@NgModule({
  imports:      [ BrowserModule, FormsModule, ReactiveFormsModule, AppRoutingModule],
  declarations: [ AppComponent, HelloComponent, JobInfoComponent, SubmitJobComponent, SubmitTaskComponent, JobListComponent ],
  bootstrap:    [ AppComponent ],
  providers: [JobService, TaskService]
})
export class AppModule { }
