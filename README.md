# BEASTling: a software tool for linguistic phylogenetics using BEAST 2

This is the repository for the paper "BEASTling: a software tool for
linguistic phylogenetics using BEAST 2", published in XXX.  It contains
not only the pre-print text of the paper, but also everything required for you
to do your own independent "build" of the paper.  All original data for the
example analyses is included in its original, untouched form.  All processing of
the data which is required before the analyses is performed by Python scripts,
so you can see exactly what was done and even see how the results change if you
do it differently.  Post-processing of the results from BEAST is performed from
scripts too, including programmatically creating every table and every figure in
the paper.  A Makefile and a Python virtual environment have been provided to
make builds as smooth as possible, although there may still be some bumps.
Nevertheless, with a little effort you should be able to produce your own PDF of
the paper, with slight differences in the tables and figures corresponding to
the probabilistic variation between MCMC runs.

The Makefile consists of three high level targets, explained below.

## Make clean

The repository contains the "official" BEAST XML files, tables and figures as
used in the published paper.  By running `make clean` in your local checkout of
the repository, everything will be deleted except for the original data files,
the BEASTling configuration files and the pre/post-processing scripts.  You
should have the following:

* `examples/austronesian/language.csv` - Raw WALS data, as available from
  http://wals.info/static/download/wals-language.csv.zip
* `examples/austronesian/a400-m1pcv-time.mcct.trees` - Austronesian summary
  tree from Gray et al's 2009 Science paper (kindly provided by Simon Greenhill)
* `examples/austronesian/iso.austronesian.txt` - Mapping from Austronesian
  family names as used in summary tree to ISO codes (kindly provided by Simon
  Greenhill)
* `examples/austronesian/preprocess.py` - Preprocessing script (described below)
* `examples/austronesian/austronesian.conf` - BEASTling configuration file
* `examples/austronesian/postprocess.py` - Postprocessing script (described
  below)
* `examples/indoeuropean/PIE.csv` - Raw Indo-European cognate data (kindly
* `examples/indoeuropean/Pagel-2007-200.tsv` - Pagel et al's meaning class
  stability ranking (kindly provided by Mattis List)
* `examples/indoeuropean/Starostin-2007-110.tsv` - Starostin's meaning class
  stability ranking (kindly provided by Mattis List)
* `examples/indoeuropean/Swadesh-1955-215.tsv` - Swadesh's meaning class
  stability ranking (kindly provided by Mattis List)
* `examples/indoeuropean/preprocess.py` - Preprocessing script (described below)
* `examples/indoeuropean/indoeuropean.conf` - BEASTling configuration file
* `examples/indoeuropean/postprocess.py` - Postprocessing script (described
  below)

## Make examples

Running `make examples` in your local checkout of the repository should complete
the following steps:

 * Both of the preprocessing scripts described above will be run, transforming
   the raw data files into the inputs required for BEASTling.
 * BEASTling will be run, transforming its configuration files into BEAST XML
   files.
 * BEAST will be run using the generated XML files, producing log files and tree
   files.
 * Both of the postprocessing scripts described above will be run, reading the
   files produced by BEAST and creating some `.tex` files containing tables for
   the paper and some `.tiff` files containing figures for the paper, as well as
   some intermediary outputs.

Note that running the BEAST analyses will take several hours, it may be
convenient to let this step run overnight.

This part of the process is the most likely to fail because it depends upon
several items of software, most obviously but not limited to BEASTling and BEAST.
The make target will attempt to ease you through this as follows.

 * BEAST 2.4.5 will be downloaded from the official BEAST 2 GitHub repository
   (please note it is UP TO YOU to have a working version of Java 8 installed).
 * If you do not have `virtualenv` installed, it will be downloaded from the
   official virtualenv GitHub repository and decompressed in the current
   directory.
 * The virtualenv will be activated and `pip` will be used to install the
   following dependencies:
     * BEASTling (used to create BEAST XML files)
     * [phyltr](https://github.com/lmaurits/phyltr/) (used to find maximum clade credibility trees)
     * ete2 (used to create Figure 2)
   Please note that none of this will affect your ordinary day-to-day Python
   environment.  The virtual environment created by Make will be deleted the
   next time you run `make clean`.

Please note that the following are up to you:

 * Make sure you have a working Java 8 JRE installed
 * Make sure you have a working Python 2.7 installed

Another point to be aware of is that `ete2` is not able to produce figures
unless another library, `PyQt4` is installed.  The virtual environment does not
take care of this step for you as `PyQt4` is unsupported and not available via
`pip` or similar tools.  So, by default the postprocessing script for the
Indo-European example analysis will not produce Figure 2.  If you want to
recreate the figure you will need to find your own way to install this
dependency, perhaps using your operating system's package management tools.
Note that even without `PyQt4` you will still get your own maximum clade
credibility tree saved to a file which you can view yourself with FigTree or any
other preferred tool.

## Make paper

Running `make paper` in your local checkout of the repository will run LaTeX and
BiBTeX to produce the paper as `beastling.pdf`.  The LaTeX `\include` command
will be used to pull in tables produced by the postprocessing scripts and the
`includegraphics` command will be used to pull in figures produced by the same
scripts.  If you run `make paper` after `make clean` but before `make examples`,
it will fail because these files will not be found.  It's up to you to have a
working LaTeX environment installed.
