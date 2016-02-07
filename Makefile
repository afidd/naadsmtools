#NAADSMTRACE=test/HPAI_Kershaw_Parameters_no_controls_airborne_only_p5_runs1000_2.out
NAADSMTRACE=naadsm.out
#NAADSMDATA=test/naadsm.h5
NAADSMDATA=naadsm.h5
ID=default

.PHONY: ALL rpackages

ALL: clinical_$(ID).pdf latent_$(ID).pdf susceptible_$(ID).pdf outbreak_hist_$(ID).pdf

clinical_$(ID).pdf: clinical_$(ID).csv
	R --no-save --args "clinical_$(ID)" < individual_dist.R

latent_$(ID).pdf: latent_$(ID).csv
	R --no-save --args "latent_$(ID)" < individual_dist.R

susceptible_$(ID).pdf: susceptible_$(ID).csv
	R --no-save --args "susceptible_$(ID)" < individual_dist.R

clinical_$(ID).csv latent_$(ID).csv susceptible_$(ID).csv: $(NAADSMDATA)
	python residence_histogram.py --input $(NAADSMDATA) --id $(ID)

outbreak_hist_$(ID).pdf: outbreak_hist_$(ID).csv
	R --no-save --args "outbreak_hist_$(ID)" < plot_outbreaksize.R 

outbreak_hist_$(ID).csv: $(NAADSMDATA)
	python outbreaksize.py --input $(NAADSMDATA) --output outbreak_hist_$(ID).csv

$(NAADSMDATA): $(NAADSMTRACE)
	python read_naadsm.py --multiple --input $(NAADSMTRACE) --output $(NAADSMDATA)

clean:
	rm -f clinical_$(ID).pdf latent_$(ID).pdf susceptible_$(ID).pdf clinical_$(ID).csv latent_$(ID).csv susceptible_$(ID).csv outbreak_hist_$(ID).csv outbreak_hist_$(ID).pdf

# This target helps to initialize a new R installation
# with all of the libraries used in the R scripts
rpackages:
	for p in `grep -h library *.R | sort | uniq | cut -c9- | cut -d')' -f1`; \
	do                                                                       \
		R -e "install.packages(\"$$p\", repos=\"http://lib.stat.cmu.edu/R/CRAN/\")"; \
	done;
