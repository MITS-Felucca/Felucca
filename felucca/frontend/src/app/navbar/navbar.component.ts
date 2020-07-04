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
    <div>
      <dl>
        <dt>Current Docker Directroy:</dt>
        <dd>{{currentDockerDirectory}}</dd>
        <dt>Digest:</dt>
        <dd>{{digest}}</dd>
      </dl>
    </div>
    <div>
      <span>
        Warning: update kernel will kill all the running jobs.
      </span>
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
  @Input()
  currentDockerDirectory: string;

  @Input()
  digest: string;

  dockerDir: string;
  constructor(public activeModal: NgbActiveModal,
              private router: Router,
              private schemaService: SchemaService,) {
  }
  update() {
    console.log(this.dockerDir);
    this.schemaService.updatePharos(this.dockerDir).subscribe();
    this.activeModal.close('Close click');
  }
}

@Component({
  selector: 'navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})

export class NavbarComponent {
  isUpdating: boolean = true;
  dockerDirectory: string;
  digest: string;

  constructor (private modalService: NgbModal,
               private schemaService: SchemaService) {

  }

  ngOnInit() {
    this.schemaService.getUpdateStatus().subscribe(data => {
      this.isUpdating = data.isUpdating;
      this.dockerDirectory = data.dockerDirectory;
      this.digest = data.digest;
    });
  }

  updatePharos() {
      const modalRef = this.modalService.open(UpdatePharosComponent);
      modalRef.componentInstance.currentDockerDirectory = this.dockerDirectory;
      modalRef.componentInstance.digest = this.digest;
  }
}
