import { Component, Input, Output, OnChanges, SimpleChange, EventEmitter } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';

import { ArgumentType } from '../argument-type.enum';
import { TaskInfo } from '../task-info';

@Component({
  selector: 'app-submit-task',
  templateUrl: './submit-task.component.html',
  styleUrls: ['./submit-task.component.css']
})
export class SubmitTaskComponent implements OnChanges {
  @Input() toolName: string;
  @Output() submission = new EventEmitter<TaskInfo>();
  arguments: {[key: string]: [number, string, string]}
  form: FormGroup;
  payload = '';
  argumentType = ArgumentType;
  constructor() { 
    this.refreshForm();
  }

  ngOnChanges(changes: {[key: string]: SimpleChange}) {
    if (this.toolName != '') {
      this.refreshForm();
    }
  }

  onSubmit() {
    let taskInfo = {toolName: this.toolName, arguments: this.form.getRawValue(), files: null}
    this.payload += JSON.stringify(this.form.getRawValue());
    this.submission.emit(taskInfo)
  }

  refreshForm() {
    this.arguments = {'-f' : [ArgumentType.InputFile, '--file', 'Executable file'],
                      '-j' : [ArgumentType.OutputFile, '--json', 'json output'],
                      '-R' : [ArgumentType.OutputFile, '--prolog-results', 'Results log file'],
                      '-F' : [ArgumentType.OutputFile, '--prolog-facts', 'Facts log file'],
                      '--no-guessing' : [ArgumentType.InputFlag, null, 'do not perform hypothetical reasoning never use except for experiments'],
                      '-n' : [ArgumentType.InputText, '--new-method', 'function at address is a new() method']};
    let keys = {}
    for (let key in this.arguments) {
      if (this.arguments[key][0] == ArgumentType.OutputFile || 
          this.arguments[key][0] == ArgumentType.InputFlag) {
            keys[key] = new FormControl(false);
      } else if (this.arguments[key][0] == ArgumentType.InputText) {
        keys[key] = new FormControl('');
      } else {
        keys[key] = new FormControl();
      }
    }
    this.form = new FormGroup(keys)
  }
}