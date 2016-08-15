# testcfg

## Testing distributional learnability properties of context-free grammars.

This is code for the paper Testing Distributional Properties of Context-Free Grammars by Alexander Clark
which will appear in the proceedings of ICFG 2016.

It should run cleanly on a suitable machine with Python installed. The diagrams can be produced using the scripts provided which start with run.

git clone https://github.com/alexc17/testcfg.git
cd testcfg/testcfg
python run_experiment_cnf_density_2.py
aws s3 cp --region us-east-1 ../figures/cnf_density_3.pdf s3://testcfgresults/cnf_density_3.pdf
aws ses send-email --from alexsclark@gmail.com --to alexsclark@gmail.com --subject "Job completed" --text run_experiment_cnf_density_2.py
python run_experiment_cnf_1fkp.py
aws s3 cp --region us-east-1 ../figures/figure_cnf-1fkp.pdf  s3://testcfgresults/figure_cnf-1fkp.pdf
aws ses send-email --from alexsclark@gmail.com --to alexsclark@gmail.com --subject "Job completed" --text run_experiment_cnf_1fkp
aws ses send-email --from alexsclark@gmail.com --to alexsclark@gmail.com --subject "Terminating instance" --text empty
sudo shutdown -h now


