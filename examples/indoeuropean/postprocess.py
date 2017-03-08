#!/usr/bin/env python2
import csv
import subprocess
import sys

import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats
import seaborn as sns

import ete2
try:
    import ete2.treeview
    _CAN_PLOT = True
except ImportError:
    _CAN_PLOT = False

sys.path.append("..")
import utils

def main():
    """
    Postanalysis of the indoeuropean.log and indoeuropean.nex files generated
    by BEAST when the Indo-European analysis is run.  This will find the
    maximum clade credibility tree and try to generate a plot of it, as well
    as compute the ranking of meaning classes by posterior mean mutation rate
    and compare this ranking to others from the literature.
    """

    print("Finding maximum clade credibility tree...")
    find_mcc_tree()
    if _CAN_PLOT:
        print("Plotting maximum clade credibility tree...")
        plot_mcc_tree()
    else:
        print("Skipping plotting tree due to lack of PyQt4 support. :(")
    print("Computing posterior mean paramter estimates...")
    ranked_means = utils.write_means("indoeuropean.log", "parameter_means.csv")
    print("Computing ranking correlations...")
    compute_ranking_correls(ranked_means)
    print("Generating LaTeX table...")
    make_table(ranked_means)
    print("Generating rate variation figure...")
    make_figure("category_rates.eps")

def find_mcc_tree():
    """
    Use the phyltr program to find the maximum clade credibility tree
    for this analysis, and save it to the file mcct.nex.
    """
    command = "phyltr cat -b 10 indoeuropean.nex | phyltr support --sort | " \
            "head -n 1 > mcct.nex"
    subprocess.call(command, shell=True)

def plot_mcc_tree():
    """
    Use ETE2 to save a PDF image of the tree stored in the mcct.nex file.
    """
    t = ete2.Tree("mcct.nex")
    ts = ete2.treeview.TreeStyle()
    ts.show_scale = False
    ts.show_leaf_name = False
    ts.show_branch_support = False
    ts.scale = 500
    margin = 10
    ts.margin_top = margin
    ts.margin_bottom = margin
    ts.margin_left = margin
    ts.margin_right = margin

    germ_style = ete2.NodeStyle()
    germ_style["bgcolor"] = "LightSteelBlue"
    proto_germ = t.get_common_ancestor("Danish", "Norwegian","Icelandic","Swedish", "Dutch", "German", "English")
    proto_germ.set_style(germ_style)

    bs_style = ete2.NodeStyle()
    bs_style["bgcolor"] = "Moccasin"
    proto_bs = t.get_common_ancestor("Bulgarian", "Czech","Polish","Russian")
    proto_bs.set_style(bs_style)

    ital_style = ete2.NodeStyle()
    ital_style["bgcolor"] = "DarkSeaGreen"
    proto_ital = t.get_common_ancestor("French", "Romanian", "Italian", "Portuguese", "Spanish")
    proto_ital.set_style(ital_style)

    t.render("mcct.eps", style_func, tree_style=ts, dpi=600, units="px", w=2250)

def style_func(node):
    """
    ETE2 styling function.
    """
    # Get rid of dots
    node.img_style["size"]=0
    node.img_style["hz_line_width"] = 2
    node.img_style["vt_line_width"] = 2
    if node.is_leaf():
        # Add name label
        node.add_face(ete2.TextFace(" " + node.name,fsize=10), column=0)
        node.img_style["hz_line_type"] = 0
        node.img_style["vt_line_type"] = 0
    else:
        # Set line type by support
        if node.support < 0.33:
            line_type = 2 # Dotted lines for low support
        elif node.support < 0.66:
            line_type = 1 # Dashed lines for moderate support
        else:
            line_type = 0 # Solid lines for strong support
        node.img_style["hz_line_type"] = line_type
        node.img_style["vt_line_type"] = line_type

def compute_ranking_correls(ranked_means):
    """
    Compute the correlation coefficient between our ranking of meaning
    classes by stability against three other published rankings.
    """
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

def load_starostin_ranking():
    """
    Load the ranking of meaning classes by stability provided by Starostin.
    """
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
    """
    Load the ranking of meaning classes by stability provided by Swadesh.
    """
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
    """
    Load the ranking of meaning classes by stability provided by Pagel.
    """
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

def make_table(ranked_means):
    """
    Generate a LaTeX table of fastest and slowest meaning classes and save it
    in the file table.tex for inclusion in the manuscript.
    """
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

def make_figure(filename):
    """
    Generate an image file for Figure 3 in the paper, showing the distribution
    of relative rates for different meaning class categories.
    """
    # Read mean feature rates
    fp = open("parameter_means.csv", "r")
    mean_rates = {}
    for line in fp:
        feature, rate = line.strip().split(",")
        feature = feature.split(":")[-1]
        mean_rates[feature] = float(rate)
    fp.close()

    # Define categories
    def get_category(meaning):
        if meaning.endswith("(V)"):
            return "Verb"
        elif meaning in "belly breast ear eye foot hair hand head heart knee liver mouth neck nose tongue tooth skin bone".split():
            return "Body part"
        elif meaning in "big cold far full good heavy long near new round short small thin warm dry many".split():
            return "Adjective"
        elif meaning in "black green red yellow white".split():
            return "Colour"
        elif meaning in "I thou we who what this that all".split():
            return "Pronoun"
        # There's only one adverb, so forget it
        elif meaning == "not":
            return None
        # There are only two numbers, so they don't plot well
        elif meaning in "one two".split():
            return None
        # Everything else is a boring old noun
        else:
            return "Noun"

    # Build a DataFrame
    categories = ["Verb","Noun","Body part","Pronoun","Adjective","Colour"]
    dataframes = []
    for category in categories:
        dataframes.append(pd.DataFrame({category:[mean_rates[f] for f in mean_rates if get_category(f) == category]}))
    df = pd.concat(dataframes)

    # Plot it
    fig = plt.figure()
    sns.set(style="whitegrid", palette="muted")
    sns.set_context("paper",font_scale=1.25)
    ax = sns.boxplot(data=df,order=categories,width=0.75)
    ax.set_ylim(0, 2.5)
    ax.set(ylabel='Relative rate of change')
    ax.set(xlabel='Part of speech')
    plt.tight_layout()
    # Make a narrow plot whose width is PLoS's maximum
    fig.set_size_inches(w=7.5,h=7.5/2)
    # Save at PLoS's maximum permitted DPI
    plt.savefig(filename, dpi=600)

if __name__ == "__main__":
    main()
