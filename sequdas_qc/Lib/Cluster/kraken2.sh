#!/bin/bash
#$ -V
#$ -N sequdas_kraken2
#$ -cwd
#$ -pe smp 30
#$ -l h_vmem=100G
#$ -e /data/sequdas/sequdas_server/Log/Qsub
#$ -o /data/sequdas/sequdas_server/Log/Qsub

python $5/kraken2.py $1 $2 $3 $4 $6
