import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Schema } from '../schema'
import { SchemaService } from '../schema.service';


@Component({
  selector: 'app-tool-list',
  templateUrl: './tool-list.component.html',
  styleUrls: ['./tool-list.component.css']
})
export class ToolListComponent implements OnInit {

  schemas: Schema[];
  chosenIndex: number;
  constructor(private schemaService: SchemaService, 
              private router: Router) { }

  ngOnInit() {
    this.getSchemas();
    this.chosenIndex = 0;
  }

  deleteSchema(schemaID: string): void {
    this.schemaService.deleteSchemaByID(schemaID).subscribe(data => {
      this.getSchemas();
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

}