all: clean examples paper

# Clean
.PHONY: clean_beast
clean_beast:
	rm -r beast/

.PHONY: clean
clean: clean_beast
	# Delete TeX cruft
	rm -f beastling.aux
	rm -f beastling.bbl
	rm -f beastling.blg
	rm -f beastling.log
	rm -f beastling.out
	rm -f beastling.pdf
	rm -f supplement.aux
	rm -f supplement.bbl
	rm -f supplement.blg
	rm -f supplement.log
	rm -f supplement.out
	rm -f supplement.pdf
	# Delete BEASTling and BEAST output
	rm -f examples/*/*.xml
	rm -f examples/*/*.log
	rm -f examples/*/*.nex
	rm -f examples/*/*.state
	# Delete processed data files
	rm -f examples/indoeuropean/indoeuropean.csv
	# Delete results
	rm -f examples/indoeuropean/parameter_means.csv
	rm -f examples/indoeuropean/mcct.pdf

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

# Check java
java_is_8:
	java -version 2> java_version && \
		grep -F 'version "1.8' java_version && \
		echo "YES" > java_is_8

## Install beast:
# Download core
beast/distfiles/beast.tgz:
	mkdir -p beast/distfiles
	curl -Lo beast/distfiles/beast.tgz \
		"https://github.com/CompEvol/beast2/releases/download/v2.4.3/BEAST.v2.4.3.Linux.tgz"

# Unpack core
beast/beast/bin/beast: beast/distfiles/beast.tgz
	cd beast/ && \
		tar -xzf distfiles/beast.tgz

# Test beast
beast_version: java_is_8 beast/beast/bin/beast
	beast/beast/bin/beast -version > beast_version


