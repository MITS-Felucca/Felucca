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
import { SchemaService } from './schema.service';
import { OutputDisplayComponent } from './output-display/output-display.component';
import { ToolListComponent } from './tool-list/tool-list.component';
import { EditToolComponent } from './edit-tool/edit-tool.component';
import { SubmitResultComponent } from './submit-job/submit-job.component'; 
import { NavbarComponent } from './navbar/navbar.component';
import { UpdatePharosComponent } from './navbar/navbar.component';

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
                  FileDisplayComponent,
                  OutputDisplayComponent,
                  ToolListComponent,
                  EditToolComponent,
                  SubmitResultComponent,
                  NavbarComponent,
                  UpdatePharosComponent],
  bootstrap:    [ AppComponent ],
  providers: [ JobService, FileService, SchemaService ]
})

export class AppModule { }
