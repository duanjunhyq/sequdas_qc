#!/bin/bash
#$ -V
#$ -N sequdas_coverage
#$ -cwd
#$ -pe smp 10
#$ -l h_vmem=100G
#$ -e /data/sequdas/sequdas_server/Log/Qsub
#$ -o /data/sequdas/sequdas_server/Log/Qsub

python $6/Lib/Cluster/coverage.py $1 $2 $3 $4 $5