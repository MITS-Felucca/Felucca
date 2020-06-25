import { Component, Input, Output, OnChanges, SimpleChange, EventEmitter } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';

import { ArgumentType } from '../argument-type.enum';
import { TaskInfo } from '../task-info';
import { Schema } from '../schema';

@Component({
  selector: 'app-submit-task',
  templateUrl: './submit-task.component.html',
  styleUrls: ['./submit-task.component.css']
})
export class SubmitTaskComponent implements OnChanges {
  @Input() schema: Schema;
  @Output() submission = new EventEmitter<TaskInfo>();

  files: {[key: string]: string} = {};
  form: FormGroup;
  defaultNames: {[key: string]: string} = {};
  argumentType = ArgumentType;
  
  ngOnChanges(changes: {[key: string]: SimpleChange}) {
    if (this.schema != undefined) {
      this.refreshForm();
    }
  }

  onFileChange(event, key: string) {
    console.log("called" + key);
    let reader = new FileReader();

    if (event.target.files && event.target.files.length) {
      const [file] = event.target.files;
      reader.readAsDataURL(file);
      reader.onload = () => {
        this.files[key] = (<string> reader.result).split(',')[1];
        this.form.get(['inputFile', key]).patchValue(file.name);
        this.form.get(['inputFile', key]).markAsDirty();
      };
    }

    event.srcElement.value = '';
  }

  fileClear(key: string) {
    delete this.files[key];
    this.form.get(['inputFile', key]).markAsPristine();
    this.form.get(['inputFile', key]).patchValue('');
  }

  onSubmit() {
    let inputFileForm: {[key: string]: string} = {};
    let inputTextForm: {[key: string]: string} = {};
    let inputFlagForm: string[] = [];
    let outputFileForm: {[key: string]: string} = {};

    let rawInputFileForm = (this.form.get('inputFile') as FormGroup).getRawValue();

    for (let key in rawInputFileForm) {
      if (rawInputFileForm[key] !== '') {
        inputFileForm[key] = rawInputFileForm[key];
      }
    }

    let rawInputFlagForm = (this.form.get('inputFlag') as FormGroup).getRawValue();

    for (let key in rawInputFlagForm) {
      if (rawInputFlagForm[key] !== false) {
        inputFlagForm.push(key);
      }
    }

    let rawInputTextForm = (this.form.get('inputText') as FormGroup).getRawValue();

    for (let key in rawInputTextForm) {
      if (rawInputTextForm[key] !== '') {
        inputTextForm[key] = rawInputTextForm[key];
      }
    }

    let rawOutputFileForm = (this.form.get('outputFile') as FormGroup).getRawValue();

    for (let key in rawOutputFileForm) {
      if (rawOutputFileForm[key] !== false) {
        outputFileForm[key] = this.defaultNames[key];
      }
    }

    let taskInfo = {
      files: this.files,
      inputFileArguments: inputFileForm,
      inputTextArguments: inputTextForm,
      inputFlagArguments: inputFlagForm,
      outputFileArguments: outputFileForm,
      toolName: this.schema.toolName,
      programName: this.schema.programName
    };

    this.submission.emit(taskInfo);
  }

  refreshForm() {
    this.files = {};
    this.defaultNames = {};

    let inputFileKeys = {};
    let inputTextKeys = {};
    let inputFlagKeys = {};
    let outputFileKeys = {};
    for (let argumentClass of this.schema.argumentClasses) {
      for (let argument of argumentClass.arguments) {
        if (argument.argumentType === ArgumentType.OutputFile) {
          if (argument.isRequired) {
            outputFileKeys[argument.key] = new FormControl(true, Validators.requiredTrue);
          } else {
            outputFileKeys[argument.key] = new FormControl(false);
          }
          this.defaultNames[argument.key] = argument.defaultValue;
        } else if (argument.argumentType === ArgumentType.InputFlag) {
            if (argument.isRequired) {
              inputFlagKeys[argument.key] = new FormControl(true, Validators.requiredTrue);
            } else {
              inputFlagKeys[argument.key] = new FormControl(false);
            }
        } else if (argument.argumentType == ArgumentType.InputText) {
          if (argument.defaultValue !== undefined && argument.isRequired) {
            inputTextKeys[argument.key] = new FormControl(argument.defaultValue, Validators.required);
          } else if (argument.defaultValue !== undefined && argument.isRequired === false) {
            inputTextKeys[argument.key] = new FormControl(argument.defaultValue);
          } else if (argument.isRequired) {
            inputTextKeys[argument.key] = new FormControl('', Validators.required);
          } else {
            inputTextKeys[argument.key] = new FormControl('');
          }
        } else {
          if (argument.isRequired) {
            inputFileKeys[argument.key] = new FormControl('', Validators.required);
          } else {
            inputFileKeys[argument.key] = new FormControl('');
          }
        }
     }
    } 
    this.form = new FormGroup ({
      inputFile: new FormGroup(inputFileKeys), 
      outputFile: new FormGroup(outputFileKeys),
      inputText: new FormGroup(inputTextKeys),
      inputFlag: new FormGroup(inputFlagKeys)
    });
  }
}
