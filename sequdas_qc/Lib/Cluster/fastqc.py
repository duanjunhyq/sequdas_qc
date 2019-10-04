import subprocess
import sys
subprocess.call(['fastqc' ,sys.argv[1]])