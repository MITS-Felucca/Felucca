import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module'

import { AppComponent } from './app.component';
import { JobInfoComponent } from './job-info/job-info.component';
import { JobService } from './job.service';
import { TaskService } from './task.service';


@NgModule({
  imports:      [ BrowserModule, FormsModule, AppRoutingModule ],
  declarations: [ AppComponent, JobInfoComponent ],
  bootstrap:    [ AppComponent ],
  providers: [JobService, TaskService]
})
export class AppModule { }
