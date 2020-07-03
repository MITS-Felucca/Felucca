import { Component, OnInit, Input} from '@angular/core';
import { Router } from '@angular/router';

import { TaskInfo } from '../task-info'
import { JobService } from '../job.service';
import { Schema } from '../schema';
import { SchemaService } from '../schema.service';
import { NgbModal, NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'ngbd-modal-content',
  template: `
    <div class="modal-header">
      <h4 class="modal-title">{{statusMessage}}</h4>
      <button type="button" class="close" aria-label="Close" (click)="activeModal.dismiss('Cross click')">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
    <div class="modal-body">
      <p>{{message}}</p>
    </div>
    <div class="modal-footer">
      <button type="button" class="btn btn-outline-dark" (click)="close()">Close</button>
    </div>
  `
})
export class SubmitResultComponent {
  @Input() status;
  @Input() message;
  @Input() statusMessage;


  constructor(public activeModal: NgbActiveModal,
              private router: Router) {
  }
  close() {
    console.log(this.status);
    if (this.status) {
      this.router.navigate(['/job-list']);
      this.activeModal.close('Close click');
    } else {
      this.activeModal.close('Close click');
    }
  }
}


@Component({
  selector: 'app-submit-job',
  templateUrl: './submit-job.component.html',
  styleUrls: ['./submit-job.component.css']
})
export class SubmitJobComponent implements OnInit{
  name: string;
  comment: string;
  tasks: TaskInfo[];
  schemas: Schema[];
  chosenSchema: Schema;
  chosenIndex: number;

  constructor(private jobService: JobService,
              private schemaService: SchemaService,
              private modalService: NgbModal) { }

  ngOnInit() {
    this.tasks = [];
    this.schemaService.getSchemas().subscribe(schemas => {this.schemas = schemas;});
    this.chosenSchema = undefined;
    this.chosenIndex = 0;
  }

  submitTask(newTask: TaskInfo) {
    this.tasks.push(newTask);
    this.chosenSchema = undefined;
    this.chosenIndex = 0;
  }

  deleteTask(id: number) {
    this.tasks.splice(id, 1);
  }

  displayAddTaskPage() {
    if (this.chosenIndex !== 0) {
      this.chosenSchema = this.schemas[this.chosenIndex - 1];
    } else {
      this.chosenSchema = undefined;
    }
  }

  submitJob() {
    if (!this.comment) {
      this.comment = '';
    }
    this.jobService.submitJob(this.name, this.comment, this.tasks).subscribe(result => {
      console.log(result);
      const modalRef = this.modalService.open(SubmitResultComponent);
      modalRef.componentInstance.status = result;
      if (result) {
        modalRef.componentInstance.statusMessage = "Submitted successfully";
        modalRef.componentInstance.message = `Job ${this.name} submit successfully.`;
      } else {
        modalRef.componentInstance.statusMessage = 'Submitted failed';
        modalRef.componentInstance.message = 'The server is being upgraded, please try again later.';
      }
    });
  }

  isValidJob(): boolean {
    return this.name && this.name.length > 0 && this.tasks.length > 0;
  }
}
