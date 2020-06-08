import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { JobInfoComponent } from './job-info/job-info.component';
import { JobListComponent } from './job-list/job-list.component';
import { SubmitJobComponent } from './submit-job/submit-job.component'


const routes: Routes = [
  { path: '', redirectTo: '/job-list', pathMatch: 'full' },
  { path: 'job-info/:jobID', component: JobInfoComponent },
  { path: 'submit-job', component: SubmitJobComponent},
  { path: 'job-list', component: JobListComponent }
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
