cd ../testcfg/
for slice in 1 2 
do
    python run_experiment_cnf_kfcp_parallel.py --seed $slice --grammars 1 ../data/kfcp.$slice &
done
