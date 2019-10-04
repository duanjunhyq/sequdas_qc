import subprocess
import sys
import json


read_length_F = int(subprocess.check_output("zcat "+sys.argv[1]+" | paste - - - - | cut -f 2 | tr -d '\n' | wc -c", shell = True))
read_length_R = int(subprocess.check_output("zcat "+sys.argv[2]+" | paste - - - - | cut -f 2 | tr -d '\n' | wc -c", shell = True))
read_length = read_length_F + read_length_R
with open(sys.argv[3]+"/"+sys.argv[4]+"_$$$"+sys.argv[5]+'delete.txt', 'w') as outfile: 
    json.dump(read_length, outfile)