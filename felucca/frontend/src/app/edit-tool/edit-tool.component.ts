import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormGroup, FormControl, Validators, FormControlName, FormArray } from '@angular/forms';

import { Schema } from '../schema'
import { SchemaService } from '../schema.service';
import { ArgumentType } from '../argument-type.enum'

@Component({
  selector: 'app-edit-tool',
  templateUrl: './edit-tool.component.html',
  styleUrls: ['./edit-tool.component.css']
})
export class EditToolComponent implements OnInit {

  operation: string;
  metadata: FormGroup;
  toolID: string;
  argumentType = ArgumentType;

  constructor(private schemaService: SchemaService, 
              private route: ActivatedRoute,
              private router: Router) { }

  ngOnInit() {
    this.operation = this.route.snapshot.paramMap.get('operation');
  
    if (this.operation === 'create') {
      this.metadata = new FormGroup ({
        toolName: new FormControl("", Validators.required), 
        programName: new FormControl("", Validators.required), 
        isPharos: new FormControl(true),
        argumentClasses: new FormArray([])
      });
    } else if (this.operation === 'create-from') {
      this.metadata = new FormGroup ({
        toolName: new FormControl("", Validators.required), 
        programName: new FormControl("", Validators.required), 
        isPharos: new FormControl(true),
        argumentClasses: new FormArray([])
      });
      this.schemaService.getSchemaByID(this.route.snapshot.paramMap.get('toolID')).subscribe(schema => {
        this.fromSchema(schema);
      });
    } else {
      this.toolID = this.route.snapshot.paramMap.get('toolID');
      this.schemaService.getSchemaByID(this.toolID).subscribe(schema => {
        this.metadata = new FormGroup ({
          toolName: new FormControl(schema.toolName, Validators.required), 
          programName: new FormControl(schema.programName, Validators.required), 
          isPharos: new FormControl(schema.isPharos),
          argumentClasses: new FormArray([])
        });
        this.fromSchema(schema);
      });
    }
  }

  fromSchema(schema: Schema): void {
    for (let argumentClass of schema.argumentClasses) {
      let argumentsForm = [];
      for (let argumentInfo of argumentClass.arguments) {
        argumentsForm.push(new FormGroup ({
          fullName: new FormControl(argumentInfo.fullName),
          abbreviation: new FormControl(argumentInfo.abbreviation),
          description: new FormControl(argumentInfo.description),
          isRequired: new FormControl(argumentInfo.isRequired),
          defaultValue: new FormControl(argumentInfo.defaultValue),
          argumentType: new FormControl(argumentInfo.argumentType, Validators.required)
        }, this.argumentValidator));
      }
      (this.metadata.get('argumentClasses') as FormArray).push(new FormGroup({
        name: new FormControl(argumentClass.name, Validators.required),
        arguments: new FormArray(argumentsForm)
      }));
    }
  }

  get classGroups(): FormArray {
    return this.metadata.get('argumentClasses') as FormArray;
  }

  getArgumentGroups(index: number): FormArray {
    return ((this.metadata.get('argumentClasses') as FormArray).at(index) as FormGroup).get('arguments') as FormArray;
  }

  addArgument(index: number): void {
    this.getArgumentGroups(index).push(new FormGroup ({
      fullName: new FormControl(''),
      abbreviation: new FormControl(''),
      description: new FormControl(),
      isRequired: new FormControl(''),
      defaultValue: new FormControl(''),
      argumentType: new FormControl('', Validators.required)
    }, this.argumentValidator));
  }

  deleteArgument(classIndex: number, argumentIndex: number): void {
    this.getArgumentGroups(classIndex).removeAt(argumentIndex);
  }

  addClass(): void {
    this.classGroups.push(new FormGroup ({
      name: new FormControl('', Validators.required),
      arguments: new FormArray([])
    }));
  }

  deleteClass(index: number): void {
    this.classGroups.removeAt(index);
  } 

  onSubmit(): void {
    if (this.operation === "edit") {
      this.schemaService.updateSchema(this.metadata.getRawValue(), this.toolID).subscribe(data => {
        this.router.navigate(['tool-list']);
      });
    } else {
      this.schemaService.createSchema(this.metadata.getRawValue()).subscribe(data => {
        this.router.navigate(['tool-list']);
      });
    }
  }

  argumentValidator(formGroup: FormGroup) {
    let errors = {};
    if (formGroup.get('fullName').value === '' && formGroup.get('abbreviation').value === '') {
      errors['emptyKey'] = true;
    }

    if (formGroup.get('argumentType').value === ArgumentType.OutputFile && formGroup.get('defaultValue').value === '') {
      errors['emptyDefaultValue'] = true;
    }

    if (JSON.stringify(errors) === '{}') {
      return null;
    }
    return errors;
  }
}
  