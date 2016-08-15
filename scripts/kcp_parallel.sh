cd ../testcfg/
for slice in `seq 1 50`
do
    python run_experiment_cnf_kfcp_parallel.py --seed $slice --grammars 10 ../data/kfcp.$slice > ../log/kfcp.log.$slice &
done
