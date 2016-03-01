#!/usr/bin/env python2
import csv
import subprocess
import sys

import ete2
import scipy.stats

sys.path.append("..")
import utils

def find_mcc_tree():
    command = "phyltr cat indoeuropean.nex | phyltr support --sort | " \
            "head -n 1 > mcct.nex"
    subprocess.call(command, shell=True)

def ultrametric(node):
    node.img_style["vt_line_width"]=0
    if node.is_leaf():
        node.img_style["size"]=5
    else:
        node.img_style["size"]=0
#        if node.dist > 0.05:
#            node.add_face(ete2.TextFace("%.2f" % node.support, fsize=4),column=0,position="branch-top")

def plot_mcc_tree():
    t = ete2.Tree("mcct.nex")
    ts = ete2.TreeStyle()
    ts.show_scale = False
    ts.show_branch_support = True
    t.render("mcct.pdf", ultrametric, tree_style=ts)

def load_starostin_ranking():
    ranking = []
    fp = open("Starostin-2007-110.tsv", "r")
    r = csv.DictReader(fp, delimiter="\t")
    for row in r:
        word = row["GLOSS"].lower()
        word = "walk" if word =="walk(go)" else word
        rank = int(row["NUMBER"])
        ranking.append((rank, word))
    fp.close()
    ranking.sort()
    return [w for (n,w) in ranking]

def load_swadesh_ranking():
    ranking = []
    fp = open("Swadesh-1955-215.tsv", "r")
    r = csv.DictReader(fp, delimiter="\t")
    for row in r:
        word = row["ENGLISH"].lower()
        if word.startswith("*"):
            word = word[1:]
        if "(" in word:
            word = word.split("(")[0].strip()
        rank = int(row["STABILITY_SCORE"])
        ranking.append((rank, word))
    fp.close()
    ranking.sort()
    ranking.reverse()
    return [w for (n,w) in ranking]

def load_pagel_ranking():
    ranking = []
    fp = open("Pagel-2007-200.tsv", "r")
    r = csv.DictReader(fp, delimiter="\t")
    for row in r:
        word = row["ENGLISH"].lower()
        if "(" in word:
            word = word.split("(")[0].strip()
        if word.startswith("to "):
            word = word.split(" ",1)[1]
        rank = float(row["MEAN_RATE"])
        ranking.append((rank, word))
    fp.close()
    ranking.sort()
    return [w for (n,w) in ranking]

def compute_ranking_correls(ranked_means):
    ranked_means = [w.split(":")[-1].lower() for (r,w) in ranked_means]
    ranked_means = [w[:-4] if w.endswith(" (v)") else w for w in ranked_means]

    starostin = load_starostin_ranking()
    starostin = [s for s in starostin if s in ranked_means]
    posterior = [p for p in ranked_means if p in starostin]
    starostin = [starostin.index(w) for w in posterior]
    posterior = [posterior.index(w) for w in posterior]
    starostin_correl = scipy.stats.spearmanr(posterior, starostin)[0]

    swadesh = load_swadesh_ranking()
    swadesh = [s for s in swadesh if s in ranked_means]
    posterior = [p for p in ranked_means if p in swadesh]
    swadesh = [swadesh.index(w) for w in posterior]
    posterior = [posterior.index(w) for w in posterior]
    swadesh_correl = scipy.stats.spearmanr(posterior, swadesh)[0]

    pagel = load_pagel_ranking()
    pagel = [s for s in pagel if s in ranked_means]
    posterior = [p for p in ranked_means if p in pagel]
    pagel = [pagel.index(w) for w in posterior]
    posterior = [posterior.index(w) for w in posterior]
    pagel_correl = scipy.stats.spearmanr(posterior, pagel)[0]

    starostin = load_starostin_ranking()
    swadesh = load_swadesh_ranking()
    starostin = [s for s in starostin if s in ranked_means and s in swadesh]
    swadesh = [s for s in swadesh if s in ranked_means and s in starostin]
    posterior = [p for p in ranked_means if p in starostin and p in swadesh]
    starostin = [starostin.index(w) for w in posterior]
    swadesh = [swadesh.index(w) for w in posterior]
    posterior = [posterior.index(w) for w in posterior]
    mean = [(st+sw)/2.0 for st,sw in zip(starostin,swadesh)]
    mean_correl = scipy.stats.spearmanr(posterior, mean)[0]

    fp = open("ranking_correlations.csv", "w")
    fp.write("%s, %f\n" % ("Starostin", starostin_correl))
    fp.write("%s, %f\n" % ("Swadesh", swadesh_correl))
    fp.write("%s, %f\n" % ("Mean", mean_correl))
    fp.write("%s, %f\n" % ("Pagel", pagel_correl))
    fp.close()


def make_table(ranked_means):
    fp = open("table.tex", "w")
    fp.write("""\\begin{tabular}{|l|c||l|c|}
    \\hline
    \\multicolumn{2}{|c||}{Slowest} & \\multicolumn{2}{|c|}{Fastest} \\\\ \\hline
    Feature & Rate  & Feature & Rate \\\\ \\hline
""")
    top_10 = ranked_means[0:10]
    bottom_10 = ranked_means[-10:]
    for ((f_rate, f_name),(s_rate,s_name)) in zip(top_10, bottom_10):
        f_name = f_name.split(":")[-1]
        s_name = s_name.split(":")[-1]
        fp.write("  %s & %.2f & %s & %.2f \\\\ \n" % \
                (f_name, f_rate, s_name, s_rate))
    fp.write("\\hline\n")
    fp.write("\\end{tabular}\n")
    fp.close()

def main():

    print("Finding maximum clade credibility tree...")
    find_mcc_tree()
    print("Plotting maximum clade credibility tree...")
    plot_mcc_tree()
    print("Computing posterior mean paramter estimates...")
    utils.prepare_log_file("indoeuropean.log", "prepared.log")
    ranked_means = utils.write_means("prepared.log", "parameter_means.csv")
    print("Computing ranking correlations...")
    compute_ranking_correls(ranked_means)
    print("Generating LaTeX table...")
    make_table(ranked_means)


if __name__ == "__main__":
    main()
