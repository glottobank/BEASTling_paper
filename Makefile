all: clean examples paper

BEAST_BIN ?= beast/beast/bin/beast

# Clean
.PHONY: clean_beast
clean_beast:
	rm -r beast/
	rm java_version
	rm java_is_8
	rm beast_version
	rm beast_is_24

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
austronesian: $(BEAST_BIN)
	cd examples/austronesian && \
		./preprocess.py && \
		beastling --overwrite austronesian.conf && \
		$(BEAST_BIN) -overwrite -java austronesian.xml && \
		./postprocess.py

.PHONY: indoeuropean
indoeuropean: $(BEAST_BIN)
	cd examples/indoeuropean && \
		./preprocess.py && \
		beastling --overwrite indoeuropean.conf && \
		$(BEAST_BIN) -overwrite -java indoeuropean.xml && \
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

## Install beast:
# Check java
java_is_8:
	java -version 2> java_version && \
		grep -F 'version "1.8' java_version && \
		echo "YES" > java_is_8
# Download core
beast/distfiles/beast.tgz:
	mkdir -p beast/distfiles
	curl -Lo beast/distfiles/beast.tgz \
		"https://github.com/CompEvol/beast2/releases/download/v2.4.3/BEAST.v2.4.3.Linux.tgz"
# Unpack core
beast/beast/bin/beast: beast/distfiles/beast.tgz
	cd beast/ && \
		tar -xzf distfiles/beast.tgz
# Get beast version
beast_version: java_is_8 $(BEAST_BIN)
	$(BEAST_BIN) -version > beast_version
beast_is_24: beast_version
	grep -F 'v2.4' beast_version && \
		echo "YES" > beast_is_24

