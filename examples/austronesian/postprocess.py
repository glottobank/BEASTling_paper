#!/usr/bin/env python2
import csv
import sys

sys.path.append("..")
import utils

def load_wals_feature_names():
    fp = open("language.csv","r")
    reader = csv.DictReader(fp)
    fn = reader.fieldnames
    features = [f for f in fn if f[0].isdigit()]
    features = [f.split(" ",1) for f in features]
    return dict(features)

def make_tables(ranked_means):
    nice = load_wals_feature_names()
    nice_ranked_means = [(r, \
            nice[n.split(":")[-1]]) for (r,n) in ranked_means]
    top_10 = nice_ranked_means[0:10]
    bottom_10 = nice_ranked_means[-10:]

    fp = open("table.tex", "w")
    fp.write("""\\begin{tabular}{|l|c|}
	\\hline
	Feature & Rate  \\\\ \hline
	\multicolumn{2}{|c|}{Slowest} \\\\ \\hline\n""")
    for (rate, name) in top_10:
        fp.write("%s & %.2f \\\\\n" % (name, rate))
    fp.write("\\hline\n""")
    fp.write("\\multicolumn{2}{|c|}{Fastest} \\\\ \\hline\n""")
    for (rate, name) in bottom_10:
        fp.write("%s & %.2f \\\\\n" % (name, rate))
    fp.write("\\hline\n""")
    fp.write("\\end{tabular}\n")
    
    fp = open("supp_feature_table.tex", "w")
    fp.write("""\\begin{tabular}{|c|l|}
	\\hline
	WALS feature ID & WALS feature Name  \\\\ \hline \n""")
    f_ids = [f_id.split(":")[-1] for (rate, f_id) in ranked_means]
    f_ids.sort(key = lambda x: int(x[:-1]))
    for f_id in f_ids:
        name = nice[f_id]
        fp.write("%s & %s \\\\\n" % (f_id, name))
    fp.write("\\hline\n""")
    fp.write("\\end{tabular}\n")
    
def main():

    print("Computing posterior mean paramter estimates...")
    utils.prepare_log_file("austronesian.log", "prepared.log")
    utils.write_means("prepared.log", "parameter_means.csv")
    ranked_means = utils.write_means("prepared.log", "parameter_means.csv")
    print("Generating LaTeX tables...")
    make_tables(ranked_means)

if __name__ == "__main__":
    main()
