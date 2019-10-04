#!/bin/bash
#$ -V
#$ -N sequdas_fastqc
#$ -cwd
#$ -pe smp 7
#$ -l h_vmem=8G
#$ -e /data/sequdas/sequdas_server/Log/Qsub
#$ -o /data/sequdas/sequdas_server/Log/Qsub

python $2/fastqc.py $1

