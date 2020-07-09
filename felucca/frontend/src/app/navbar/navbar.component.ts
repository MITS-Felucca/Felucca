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
    <div style="text-align:center">
      <span class="badge badge-warning">Warning</span>
      <span>
        Update kernel will kill all the running jobs
      </span>
    </div>
    <div class="modal-body">
      <div class="input-group mb-3">
        <div class="input-group-prepend">
          <span class="input-group-text" id="basic-addon1">Docker Directroy</span>
        </div>
        <input [(ngModel)] = "dockerDir" type="text" class="form-control" placeholder="seipharos/pharos:latest" aria-describedby="basic-addon1">
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
    if (!this.dockerDir) {
      this.dockerDir = "seipharos/pharos:latest";
    }
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
  shortDigest: string;

  constructor (private modalService: NgbModal,
               private schemaService: SchemaService) {

  }

  ngOnInit() {
    this.schemaService.getUpdateStatus().subscribe(data => {
      this.isUpdating = data.isUpdating;
      this.dockerDirectory = data.dockerDirectory;
      this.digest = data.digest;
      this.shortDigest = this.digest.substring(0,12);
    });
  }

  updatePharos() {
      const modalRef = this.modalService.open(UpdatePharosComponent);
      modalRef.componentInstance.currentDockerDirectory = this.dockerDirectory;
      modalRef.componentInstance.digest = this.digest;
  }
}
