# 1. Get the help string in a file
# 2. Run the script
# 3. Manually check
# 4. Add header

import re
import json
import sys

fileName = sys.argv[1]
f = open(fileName,"r")
lines = f.readlines()
result = {}
result["Classes"] = []
idx = 0
classStart = False
newClass = {}

argsReg = r'\s\s(\-\w)\s\[\s(\-\-.*)?\s\]\sarg\s+(.*)'
noArgsReg = r'\s\s(\-\w)\s\[\s(\-\-.*)?\s\]\s+(.*)'
noShortArgsReg = r'\s\s(\-\-[\w+\-]+)\sarg\s+(.*)'
noShortNoArgsReg = r'\s\s(\-\-[\w+\-]+)\s+(.*)'

prevArgs = {}
for line in lines:
    idx += 1
    if len(line) == 1:
        if prevArgs != {}:
            newClass["Arguments"].append(prevArgs)
        classStart = False
        result["Classes"].append(newClass)
        newClass = {}
        continue
    if line[0] != " " and not classStart:
        classStart = True
        newClass["Name"] = line[:-1]
        newClass["Arguments"] = []
        prevArgs = {}
        continue
    if classStart:
        args = {}
        # has no short
        if line[2:4] == "--":
            if prevArgs != {}:
                newClass["Arguments"].append(prevArgs)
            matchObj = re.match(noShortArgsReg, line)
            if matchObj == None:
                matchObj = re.match(noShortNoArgsReg, line)
                tmp = "Input_Flag_Args"
            else:
                tmp = "Input_Text_Args"
            args["Full_Name"] = matchObj.group(1)
            args["Abbreviation"] = ""
            args["Description"] = matchObj.group(2)
            args["Is_Required"] = False
            args["Default_Value"] = ""
            args["Type"] = tmp
            prevArgs = args
        # has short
        elif line[2] == "-":
            if prevArgs != {}:
                newClass["Arguments"].append(prevArgs)
            matchObj = re.match(argsReg, line)
            if matchObj == None:
                matchObj = re.match(noArgsReg, line)
                tmp = "Input_Flag_Args"
            else:
                tmp = "Input_Text_Args"
            args["Full_Name"] = matchObj.group(2)
            args["Abbreviation"] = matchObj.group(1)
            args["Description"] = matchObj.group(3)
            args["Is_Required"] = False
            args["Default_Value"] = ""
            args["Type"] = tmp
            prevArgs = args
        else:
            prevArgs["Description"] += (" " + line.strip())

if prevArgs != {}:
    newClass["Arguments"].append(prevArgs)
result["Classes"].append(newClass)
resultStr = json.dumps(result, indent=4)
print(resultStr)

resultFile = open(fileName+".json", "w")
resultFile.write(resultStr)
resultFile.close()

