#!/usr/bin/env python2
import subprocess
import sys

import ete2

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
        if node.dist > 0.05:
            node.add_face(ete2.TextFace("%.2f" % node.support, fsize=4),column=0,position="branch-top")

def plot_mcc_tree():
    t = ete2.Tree("mcct.nex")
    ts = ete2.TreeStyle()
    ts.show_branch_support = False
    t.render("mcct.pdf", ultrametric, w=600, tree_style=ts)

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
    print("Generating LaTeX table...")
    make_table(ranked_means)


if __name__ == "__main__":
    main()
