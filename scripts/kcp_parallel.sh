cd ../testcfg/
for slice in `seq 1 40`
do
    python run_experiment_cnf_kfcp_parallel.py --seed $slice --grammars 40 ../data/kfcp.$slice &
done
