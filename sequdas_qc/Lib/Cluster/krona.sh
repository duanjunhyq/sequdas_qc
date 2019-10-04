#!/bin/bash
#$ -V
#$ -N sequdas_krona
#$ -cwd
#$ -pe smp 7
#$ -l h_vmem=100G
#$ -e /data/sequdas/sequdas_server/Log/Qsub
#$ -o /data/sequdas/sequdas_server/Log/Qsub

python $6/Lib/Cluster/krona.py $1 $2 $3 $4 $5 $7 $6