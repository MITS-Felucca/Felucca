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
      <h4 class="modal-title">Update pharos</h4>
      <button type="button" class="close" aria-label="Close" (click)="activeModal.dismiss('Cross click')">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
    <div class="modal-body">
      <div class="input-group mb-3">
        <div class="input-group-prepend">
          <span class="input-group-text" id="basic-addon1">Docker Directroy</span>
        </div>
        <input [(ngModel)] = "dockerDir" type="text" class="form-control" placeholder="Docker Directroy" aria-describedby="basic-addon1">
      </div>
    </div>
    <div class="modal-footer">
      <button type="button" class="btn btn-outline-dark" (click)="update()">Update</button>
    </div>
  `
})
export class UpdatePharosComponent {
  dockerDir: String;
  constructor(public activeModal: NgbActiveModal,
              private router: Router) {
  }
  update() {
    console.log(this.dockerDir);
    this.activeModal.close('Close click');
  }
}

@Component({
  selector: 'navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})

export class NavbarComponent {
  constructor (private modalService: NgbModal) {

  }
  updatePharos() {
      const modalRef = this.modalService.open(UpdatePharosComponent);
  }
}