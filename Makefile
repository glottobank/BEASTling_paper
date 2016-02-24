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
		beastling austronesian.conf && \
		beast -java austronesian.xml && \
		./postprocess.py

.PHONY: indoeuropean
indoeuropean:
	cd examples/indoeuropean && \
		./preprocess.py && \
		beastling indoeuropean.conf && \
		beast -java indoeuropean.xml && \
		./postprocess.py

# Targets for building the paper:
.PHONY: paper
paper:
	xelatex beastling
	bibtex beastling
	xelatex beastling
