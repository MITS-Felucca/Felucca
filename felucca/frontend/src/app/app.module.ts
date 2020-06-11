import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module'
import { AppComponent } from './app.component';
import { JobListComponent } from "./job-list/job-list.component";
import { JobInfoComponent } from './job-info/job-info.component';
import { JobService } from './job.service';
import { SubmitJobComponent } from './submit-job/submit-job.component';
import { SubmitTaskComponent } from './submit-task/submit-task.component';


@NgModule({
  imports:      [ BrowserModule,
                  FormsModule,
                  ReactiveFormsModule,
                  HttpClientModule,
                  AppRoutingModule],
  declarations: [ AppComponent,
                  JobListComponent,
                  JobInfoComponent,
                  SubmitJobComponent,
                  SubmitTaskComponent ],
  bootstrap:    [ AppComponent ],
  providers: [ JobService ]
})
export class AppModule { }
