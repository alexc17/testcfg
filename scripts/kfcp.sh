# Run using
# nohup sh kfcp.sh &> ../log/kfcp.log &

cd ../testcfg
python run_experiment_cnf_kfcp.py
aws ses send-email --from alexsclark@gmail.com --to alexsclark@gmail.com --subject "Job completed" --text run_experiment_cnf_kfcp
aws s3 cp --region us-east-1 ../figures/figure_cnf-kfcp.pdf  s3://testcfgresults/x_kfcp.pdf

