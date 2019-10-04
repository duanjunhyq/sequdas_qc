import subprocess
import sys

subprocess.call("kraken2 --threads 30 --db "+sys.argv[5]+" --report "+ sys.argv[1]+ " --output " +sys.argv[2]+" --paired --gzip-compressed "+ sys.argv[3]+ " "+sys.argv[4], shell = True)
