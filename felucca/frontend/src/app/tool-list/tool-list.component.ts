import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Title }     from '@angular/platform-browser';

import { Schema } from '../schema'
import { SchemaService } from '../schema.service';
import { NgbModal, NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { saveAs } from 'file-saver';


@Component({
  selector: 'delete-tool',
  template: `
    <div class="modal-header">
      <h4 class="modal-title">Delete Tool</h4>
      <button type="button" class="close" aria-label="Close" (click)="activeModal.dismiss('Cross click')">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
    <div style="text-align:center">
      <span class="badge badge-warning">Warning</span>
      <span>
        Are you sure you want to delete {{toolName}}?
      </span>
    </div>
    <div class="modal-footer">
      <button type="button" class="btn btn-danger" (click)="delete()">Delete</button>
      <button type="button" class="btn btn-outline-dark" (click)="cancel()">Cancel</button>

    </div>
  `
})
export class DeleteToolComponent {
  toolName : String;

  constructor(public activeModal: NgbActiveModal,
              private router: Router,
              private schemaService: SchemaService,) {
  }
  delete() {
    this.activeModal.close('delete');

  }
  cancel() {
    this.activeModal.close('Close click');
  }
}


@Component({
  selector: 'app-tool-list',
  templateUrl: './tool-list.component.html',
  styleUrls: ['./tool-list.component.css']
})
export class ToolListComponent implements OnInit {

  schemas: Schema[];
  chosenIndex: number;
  constructor(private schemaService: SchemaService, 
              private router: Router,
              private modalService: NgbModal,
              private titleService: Title) {
                this.titleService.setTitle( "Felucca - Tool List" );
              }

  ngOnInit() {
    this.getSchemas();
    this.chosenIndex = 0;
  }

  deleteSchema(schemaID: string, toolName: string): void {
    const modalRef = this.modalService.open(DeleteToolComponent);
    modalRef.componentInstance.toolName = toolName;

    modalRef.result.then((data) => {
      if ( data === 'delete' ) {
        this.schemaService.deleteSchemaByID(schemaID).subscribe(data => {
        this.getSchemas();
        })
      }
    }, (reason) => {
    });

  }

  editSchema(schemaID: string): void {
    this.router.navigate(['tool', 'edit', schemaID]);
  }

  createSchema(): void {
    if (this.chosenIndex == 0) {
      this.router.navigate(['tool', 'create']);
    } else {
      this.router.navigate(['tool', 'create-from', this.schemas[this.chosenIndex - 1].toolID]);
    }
  }

  getSchemas(): void {
    this.schemaService.getSchemas().subscribe(schemas => {
      this.schemas = schemas;
    });
  }

  downloadSchema(index: number): void {
    let blob = new Blob([JSON.stringify(this.schemas[index], null, ' ')], {type: "text/json;charset=utf-8"});
    saveAs(blob, this.schemas[index].toolName + ".json");
  }

}
