import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module'

import { AppComponent } from './app.component';
import { JobInfoComponent } from './job-info/job-info.component';
import { JobListComponent } from './job-list/job-list.component';
import { JobService } from './job.service';
import { TaskService } from './task.service';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';


@NgModule({
  imports:      [ BrowserModule, FormsModule, AppRoutingModule, NgbModule ],
  declarations: [ AppComponent, JobInfoComponent, JobListComponent ],
  bootstrap:    [ AppComponent ],
  providers: [JobService, TaskService]
})
export class AppModule { }
