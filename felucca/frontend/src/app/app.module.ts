import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

import { AppRoutingModule } from './app-routing.module'
import { AppComponent } from './app.component';
import { HelloComponent } from './hello.component';
import { JobListComponent } from './job-list/job-list.component';
import { JobInfoComponent } from './job-info/job-info.component';
import { JobService } from './job.service';
import { SubmitJobComponent } from './submit-job/submit-job.component';
import { SubmitTaskComponent } from './submit-task/submit-task.component';
import { FileDisplayComponent } from './file-display/file-display.component';
import { FileService } from './file.service';

@NgModule({
  imports:      [ BrowserModule,
                  FormsModule,
                  ReactiveFormsModule,
                  HttpClientModule,
                  AppRoutingModule, 
                  NgbModule],
  declarations: [ AppComponent,
                  JobListComponent,
                  JobInfoComponent,
                  SubmitJobComponent,
                  SubmitTaskComponent,
                  HelloComponent,
                  FileDisplayComponent],
  bootstrap:    [ AppComponent ],
  providers: [ JobService, FileService ]
})
export class AppModule { }
