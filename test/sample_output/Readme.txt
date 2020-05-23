Command:
ooanalyzer -j output.json -F facts -R results -f oo.exe

Output file:
output.json

Prelog fact:
facts

Prelog result:
results

Stdout:
OPTI[INFO ]: Analyzing executable: oo.exe
OPTI[INFO ]: OOAnalyzer version 1.0.
OPTI[INFO ]: ROSE stock partitioning took 12.4535 seconds.
OPTI[INFO ]: Partitioned 8791 bytes, 2839 instructions, 800 basic blocks, 0 data blocks and 193 functions.
OPTI[INFO ]: Pharos function partitioning took 18.5175 seconds.
OPTI[INFO ]: Partitioned 89088 bytes, 3598 instructions, 1009 basic blocks, 88 data blocks and 358 functions.
OPTI[INFO ]: Function analysis complete, analyzed 283 functions in 17.9497 seconds.
OOAN[ERROR]: Missing return value from new() call at 0x00411221
OPTI[INFO ]: OOAnalyzer analysis complete, found: 10 classes, 30 methods, 4 virtual calls, and 13 usage instructions.
OPTI[INFO ]: Successfully exported to JSON file 'output.json'.
OPTI[INFO ]: OOAnalyzer analysis complete.