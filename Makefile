all: clean examples paper

BEAST_BIN ?= beast/beast/bin/beast
PYTHON ?= $(shell which python2)
PY_ENV ?= beastling_ve
ACTIVATE ?= $(PY_ENV)/bin/activate
BEASTLING_BIN ?= $(PY_ENV)/bin/beastling

# Clean
.PHONY: clean_beast
clean_beast:
	rm -r beast/
	rm java_version
	rm java_is_8
	rm beast_version
	rm beast_is_24

.PHONY: clean_virtualenv
clean_virtualenv:
	# We are not cleaning your custom virtualenv.
	# That way lie accidents!
	rm -r beastling_ve/

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
examples: examples/austronesian/table.tex examples/indoeuropean/table.tex

examples/austronesian/austronesian.xml: $(BEASTLING_BIN) $(ACTIVATE)
	source $(ACTIVATE) && \
		cd examples/austronesian && \
		python ./preprocess.py && \
		beastling --overwrite austronesian.conf
examples/austronesian/austronesian.log: $(BEAST_BIN) examples/austronesian/austronesian.xml
	$(BEAST_BIN) -overwrite -working -java examples/austronesian/austronesian.xml
examples/austronesian/table.tex: $(ACTIVATE) examples/austronesian/austronesian.log
	source $(ACTIVATE) && \
		cd examples/austronesian && \
		python postprocess.py

examples/indoeuropean/indoeuropean.xml: $(BEASTLING_BIN) $(ACTIVATE)
	source $(ACTIVATE) && \
		cd examples/indoeuropean && \
		python preprocess.py && \
		beastling --overwrite indoeuropean.conf
examples/indoeuropean/indoeuropean.log: $(BEAST_BIN) examples/indoeuropean/indoeuropean.xml
	$(BEAST_BIN) -overwrite -working -java examples/indoeuropean/indoeuropean.xml
examples/indoeuropean/table.tex: $(ACTIVATE) examples/indoeuropean/indoeuropean.log
	source $(ACTIVATE) && \
		cd examples/indoeuropean && \
		python postprocess.py

# Targets for building the paper:
.PHONY: paper
paper:
	xelatex beastling
	bibtex beastling
	xelatex beastling
	xelatex beastling
	xelatex supplement
	xelatex supplement

## Create beastling virtual environment:
# Make sure we can use virtualenv
$(ACTIVATE):
	$(PYTHON) -m virtualenv $(PY_ENV) 2> virtualenv_error || \
		make force-$(ACTIVATE)
force-$(ACTIVATE):
	# Fallback because virtualenv was not available: Download a virtualenv release from github and run that.
	grep -F 'No module named virtualenv' virtualenv_error
	curl -Lo virtualenv-15.0.3.tar.gz "https://github.com/pypa/virtualenv/archive/15.0.3.tar.gz"
	tar -xvzf virtualenv-15.0.3.tar.gz
	$(PYTHON) virtualenv-15.0.3/virtualenv.py $(PY_ENV)
# Install beastling to the virtualenv
beastling_ve/bin/beastling: $(ACTIVATE)
	source $(ACTIVATE) && \
	pip install beastling

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
		tar -xvzf distfiles/beast.tgz
# Get beast version
beast_version: java_is_8 $(BEAST_BIN)
	$(BEAST_BIN) -version > beast_version
beast_is_24: beast_version
	grep -F 'v2.4' beast_version && \
		echo "YES" > beast_is_24

