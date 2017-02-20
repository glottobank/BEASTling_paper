#!/usr/bin/env python2
import csv
import subprocess
import sys

import newick

sys.path.append("..")
import utils

def main():
    """
    Prepare the MCC tree and WALS data for the Austronesian analysis.  This
    involves establishing a duplicate-free mapping from language names to ISO
    codes and pruning the tree accordingly.  The WALS data has to be
    reformatted into CLDF format as well,
    """
    print("Resolving ISO codes...")
    a_exclusions, a_mapping, w_exclusions = resolve_languages()
    print("Reformatting WALS data...")
    reformat_wals(w_exclusions)
    print("Preparing reference tree...")
    clean_reference_tree()
    adjust_reference_tree(a_exclusions, a_mapping)

def resolve_languages():
    """
    Programmatically establish a duplicate-free mapping between Austronesian
    language family names and ISO codes so we can link WALS data to the MCC
    tree.
    """
    a_mapping = load_austro_iso_names()
    w_mapping = load_wals_iso_names()
    a_exclusions = []   # Austronesian MCC langs to drop
    w_exclusions = []   # WALS langs to drop

    a_exclusions.extend(l.lower() for l in a_mapping if a_mapping[l] == "XXX")

    a_duped_isos = set([i for i in a_mapping.values() \
            if list(a_mapping.values()).count(i) > 1])
    # First, iterated over all ISO codes which are duplicated in the refrence
    # Austronesian tree.  Get all of the names in the ref. tree which map to
    # an ISO, and all of the names in WALS which map to that ISO.  Find the
    # intersection (i.e. those names used by both).  If there is one such
    # common name, identify these as the same language and kill all the
    # others.  If there is no name overlap, kill everything.
    for iso in a_duped_isos:
        a_names = set([l.lower() for l in a_mapping if a_mapping[l] == iso])
        w_names = set([l.lower() for l in w_mapping if w_mapping[l] == iso])
        true_name = a_names.intersection(w_names)
        if len(true_name) == 1:
            # Keep the common name, kill others
            a_exclusions.extend(a_names.difference(true_name))
            w_exclusions.extend(w_names.difference(true_name))
        else:
            # Kill everything
            a_exclusions.extend(a_names)
            w_exclusions.extend(w_names)
    # Now there might be ISO codes which are duplicates in WALS but not the
    # reference tree.
    w_duped_isos = set([i for i in w_mapping.values() \
            if list(w_mapping.values()).count(i) > 1])
    for iso in w_duped_isos:
        a_names = set([l.lower() for l in a_mapping if a_mapping[l] == iso])
        w_names = set([l.lower() for l in w_mapping if w_mapping[l] == iso])
        true_name = a_names.intersection(w_names)
        if len(true_name) == 1:
            # Keep the common name, kill others
            w_exclusions.extend(w_names.difference(true_name))
        else:
            w_exclusions.extend(w_names)
    for l in list(a_mapping.keys()):
        if l.lower() in set(a_exclusions):
            a_mapping.pop(l)
    for l in list(w_mapping.keys()):
        if l.lower() in set(w_exclusions):
            w_mapping.pop(l)

    # Save the mapping to a LaTeX table
    make_table(a_mapping, w_mapping)

    return a_exclusions, a_mapping, w_exclusions

def load_austro_iso_names():
    """
    Build a dictionary mapping Austronesian language names to ISO codes.
    """
    fp = open("iso.austronesian.txt", "r")
    untranslatable = []
    mapping = {}
    # Separate languages with ISO codes from those without
    for line in fp:
        iso, lang = [x.strip() for x in line.split("\t")]
        mapping[lang] = iso
    fp.close()
    return mapping

def load_wals_iso_names():
    """
    Build a dictionary mapping WALS language names to ISO codes.
    """
    fp = open("language.csv","r")
    reader = csv.DictReader(fp)
    mapping = {}
    for row in reader:
        if row["iso_code"] != "?":
            mapping[row["Name"]] = row["iso_code"]
    fp.close()
    all_isos = [i for i in mapping.values()]
    return mapping

def make_table(a_mapping, w_mapping):
    """
    Generate a LaTeX table of the language mappings and save it in the file
    supp_language_table.tex for inclusion in the manuscript.
    """
    fp = open("supp_language_table.tex", "w")
    fp.write("""\\begin{tabular}{|c|l|l||c|l|l|}
    \\hline
    ISO code & Gray et. al. name & WALS name & ISO code & Gray et. al. name & WALS name \\\\ \\hline
""")
    a_isos = set(a_mapping.values())
    w_isos = set(w_mapping.values())
    isos = list(a_isos & w_isos)
    isos.sort()
    a_rev = {v: k for k, v in a_mapping.items()}
    w_rev = {v: k for k, v in w_mapping.items()}
    pivot = int(0.5*len(isos))
    left, right = isos[0:pivot], isos[pivot:]
    for l,r in zip(left, right):
        fp.write("%s & %s & %s & %s & %s & %s \\\\ \n" % (l, a_rev[l].replace("_","\\_"), w_rev[l], r, a_rev[r].replace("_","\\_"), w_rev[r]))
    fp.write("\\hline\n")
    fp.write("\\end{tabular}\n")
    fp.close()

def reformat_wals(exclusions):
    """
    Convert the WALS data file to CLDF format.
    """
    fp_in = open("language.csv","r")
    fp_out = open("wals_data.csv","w")

    reader = csv.DictReader(fp_in)

    fn = reader.fieldnames
    fn = [name.split()[0] if name[0].isdigit() else name for name in fn]
    fn = ["iso" if name == "iso_code" else name for name in fn]
    fn = [name for name in fn if name == "iso" or name[0].isdigit()]
    fn.remove("95A")
    fn.remove("96A")
    fn.remove("97A")
    fn.remove("iso")
    fn.insert(0,"iso")

    writer = csv.DictWriter(fp_out, fn)
    writer.writeheader()

    for row in reader:
        newrow = {}
        if row["Name"].lower() in exclusions:
            continue
        for key in row.keys():
            newkey = key.split()[0] if key[0].isdigit() else key
            newkey = "iso" if newkey == "iso_code" else newkey
            if newkey not in fn:
                continue
            val = row[key]
            newval = val.split()[0] if val and val[0].isdigit() else val
            newval = newval if newval else "?"
            newrow[newkey] = newval
        if newrow["iso"] == "?":
                continue
        writer.writerow(newrow)
    
    fp_in.close()
    fp_out.close()

def clean_reference_tree():
    """
    Produce a copy of the file containing the MCC tree which consists of just
    a Newick-formatted tree, without any extraneous NEXUS syntax.
    """
    fp_in = open("a400-m1pcv-time.mcct.trees", "r")
    fp_out = open("austronesian_reference.nex", "w")
    for line in fp_in:
        # Skip comments and NEXUS cruft
        if not line.startswith("tree"):
            continue
        # Trim "tree TREE1 = " from tree line
        line = line[13:]
        fp_out.write(line)
    fp_in.close()
    fp_out.close()

def adjust_reference_tree(kill_list, translation):
    """
    Remove unwanted languages from the reference tree and change the names of
    the languages we do want to ISO codes.
    """
    tree = newick.read("austronesian_reference.nex")[0]
    tree.remove_internal_names()
    for n in tree.walk():
        if n.name:
            if n.name in translation:
                # Replace name by ISO
                n.name = translation[n.name]
            else:
                # Convert to lowercase to match kill list
                n.name = n.name.lower()
    # Remove languages not in WALS
    tree.prune_by_names(kill_list)
    # The pruning above will have left some un-named leaf nodes, so kill these
    while None in tree.get_leaf_names():
        unnamed_leaves = [
            node
            for node in tree.get_leaves()
            if node.name is None]
        tree.prune(unnamed_leaves)
    # All of the above has likely left some redundant tree nodes, i.e. nodes
    # with only one descendant, so get rid of these
    tree.remove_redundant_nodes()
    newick.write([tree], "processed_austronesian_reference.nex")
    # Save a BEASTling compatible list of ISO codes
    isos = [n.name for n in tree.walk() if n.is_leaf]
    fp = open("language_list.txt", "w")
    for iso in isos:
        fp.write("%s\n" % iso)
    fp.close()

if __name__ == "__main__":
    main()
