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

def main():

    print("Finding maximum clade credibility tree...")
    find_mcc_tree()
    print("Plotting maximum clade credibility tree...")
    plot_mcc_tree()
    print("Computing posterior mean paramter estimates...")
    utils.prepare_log_file("indoeuropean.log", "prepared.log")
    utils.write_means("prepared.log", "parameter_means.csv")

if __name__ == "__main__":
    main()
