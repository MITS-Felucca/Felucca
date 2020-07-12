import os
import sys
fname="../../DockerFile_for_updating"
os.path.abspath(fname)
with open(fname, 'r' ) as f:
  print( f.read() )