cd ../testcfg/
for slice in `seq 1 40`
do
    python run_experiment_cnf_kfkp_parallel.py --seed $slice --grammars 25 ../data/kfkp.$slice > ../log/kfkp.log.$slice &
done
