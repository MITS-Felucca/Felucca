import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { JobInfoComponent } from './job-info/job-info.component';

const routes: Routes = [
  { path: '', redirectTo: '/job-list', pathMatch: 'full' },
  { path: 'job-info/:job_id', component: JobInfoComponent }
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
