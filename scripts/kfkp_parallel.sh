#!/bin/bash
cd ../testcfg/
for slice in `seq 1 50`
do
    python run_experiment_cnf_kfkp_parallel.py --seed $slice --grammars 10 ../data/kfkp.$slice &> ../log/kfkp.log.$slice &
done
