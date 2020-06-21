import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { JobInfoComponent } from './job-info/job-info.component';
import { JobListComponent } from './job-list/job-list.component';
import { SubmitJobComponent } from './submit-job/submit-job.component'
import { FileDisplayComponent } from './file-display/file-display.component'
import { OutputDisplayComponent } from './output-display/output-display.component';

const routes: Routes = [
  { path: '', redirectTo: '/job-list', pathMatch: 'full' },
  { path: 'job-info/:jobID', component: JobInfoComponent },
  { path: 'submit-job', component: SubmitJobComponent},
  { path: 'job-list', component: JobListComponent },
  { path: 'task/:taskID/:fileType/:filename', component: FileDisplayComponent },
  { path: 'task/:taskID/:outputType', component: OutputDisplayComponent }
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
