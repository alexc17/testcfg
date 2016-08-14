# Run this with something like
# nohup sh kfkp.sh &> ../log/kfkp.log &
cd ../testcfg
python run_experiment_cnf_kfkp.py
aws ses send-email --from alexsclark@gmail.com --to alexsclark@gmail.com --subject "Job completed" --text run_experiment_cnf_kfkp
aws s3 cp --region us-east-1 ../figures/figure_cnf-kfkp.pdf  s3://testcfgresults/x_kfkp.pdf

