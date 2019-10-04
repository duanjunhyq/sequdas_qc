import subprocess
import sys


with open(sys.argv[1], 'w') as output_file:
    subprocess.call(['python',sys.argv[7]+'/kraken_parse.py','G','2','5', sys.argv[2]],stdout=output_file)
output_file.close()

with open(sys.argv[3], 'w') as output_file:
    subprocess.call(['cut','-f2,3',sys.argv[4]],stdout=output_file)
output_file.close()

subprocess.call([sys.argv[6],sys.argv[3],'-o', sys.argv[5]])



