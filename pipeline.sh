#!/bin/bash

#NAADSMTRACE=$1
#ID=$2
#NAADSMDATA=$3 

python read_naadsm.py --multiple --input $NAADSMTRACE --output $NAADSMDATA
python outbreaksize.py --input $NAADSMDATA --output outbreak_hist_$ID.csv
R --no-save --args "outbreak_hist_$ID" < plot_outbreaksize.R 
python residence_histogram.py --input $NAADSMDATA --id $ID
R --no-save --args "clinical_$ID" < plot_individual_dist.R
R --no-save --args "latent_$ID" < plot_individual_dist.R
R --no-save --args "susceptible_$ID" < plot_individual_dist.R

