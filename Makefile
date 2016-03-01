all: clean examples paper

# Clean
.PHONY: clean
clean:
	# Delete TeX cruft
	-rm beastling.aux
	-rm beastling.bbl
	-rm beastling.blg
	-rm beastling.log
	-rm beastling.out
	-rm beastling.pdf
	-rm supplement.aux
	-rm supplement.bbl
	-rm supplement.blg
	-rm supplement.log
	-rm supplement.out
	-rm supplement.pdf
	# Delete BEASTling and BEAST output
	-rm examples/*/*.xml
	-rm examples/*/*.log
	-rm examples/*/*.nex
	-rm examples/*/*.state
	# Delete processed data files
	-rm examples/indoeuropean/indoeuropean.csv
	# Delete results
	-rm examples/indoeuropean/parameter_means.csv
	-rm examples/indoeuropean/mcct.pdf

.PHONY: examples
examples: austronesian indoeuropean

.PHONY: austronesian
austronesian:
	cd examples/austronesian && \
		./preprocess.py && \
		beastling --overwrite austronesian.conf && \
		beast -overwrite -java austronesian.xml && \
		./postprocess.py

.PHONY: indoeuropean
indoeuropean:
	cd examples/indoeuropean && \
		./preprocess.py && \
		beastling --overwrite indoeuropean.conf && \
		beast -overwrite -java indoeuropean.xml && \
		./postprocess.py

# Targets for building the paper:
.PHONY: paper
paper:
	xelatex beastling
	bibtex beastling
	xelatex beastling
	xelatex beastling
	xelatex supplement
	xelatex supplement
