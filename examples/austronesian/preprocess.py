#!/usr/bin/env python2
import csv
import subprocess
import sys

import newick

language_csv = "language.csv"
wals_csv = "wals_data.csv"
iso_map = "iso.austronesian.txt"
tree_file_name = "a400-m1pcv-time.mcct.trees"
reference_tree_file_name = "austronesian.nex"

def load_wals_iso_names():
    fp = open(language_csv, "r")
    reader = csv.DictReader(fp)
    mapping = {}
    for row in reader:
        if row["iso_code"] != "?":
            mapping[row["Name"]] = row["iso_code"]
    fp.close()
    all_isos = [i for i in mapping.values()]
    return mapping

def reformat_wals(exclusions):
    fp_in = open(language_csv, "r")
    fp_out = open(wals_csv, "w")

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
    fp_in = open(tree_file_name, "r")
    fp_out = open(reference_tree_file_name, "w")
    for line in fp_in:
        # Skip comments and NEXUS cruft
        if not line.startswith("tree"):
            continue
        # Trim "tree TREE1 = " from tree line
        line = line[13:]
        fp_out.write(line)
    fp_in.close()
    fp_out.close()

def load_austro_iso_names():
    fp = open(iso_map, "r")
    untranslatable = []
    mapping = {}
    # Separate languages with ISO codes from those without
    for line in fp:
        iso, lang = [x.strip() for x in line.split("\t")]
        mapping[lang] = iso
    fp.close()
    return mapping

def make_phyltr_rename_file(translation):
    fp = open("phyltr_rename.txt", "w")
    for lang in translation:
        fp.write("%s:%s\n" % (lang, translation[lang]))
    fp.close()

def resolve_languages():
    a_mapping = load_austro_iso_names()
    w_mapping = load_wals_iso_names()
    a_exclusions = []
    w_exclusions = []

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

    make_table(a_mapping, w_mapping)

    return a_exclusions, a_mapping, w_exclusions

def make_table(a_mapping, w_mapping):
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

def adjust_reference_tree(kill_list, translation):
    tree = newick.read(reference_tree_file_name)[0]
    tree.remove_internal_names()
    for n in tree.walk():
        if n.name:
            n.name = n.name.lower() # Kill list is in lowercase
        if n.is_leaf and n.name in translation:
            n.name = translation[n.name]
    tree.prune_by_names(kill_list)
    newick.write([tree], reference_tree_file_name)
    # Save a BEASTling compatible list of ISO codes
    isos = [n.name for n in tree.walk() if n.is_leaf]
    fp = open("language_list.txt", "w")
    for iso in isos:
        fp.write("%s\n" % iso)
    fp.close()

def main():

    print("Resolving ISO codes...")
    a_exclusions, a_mapping, w_exclusions = resolve_languages()
    print("Reformatting WALS data...")
    reformat_wals(w_exclusions)
    print("Preparing reference tree...")
    clean_reference_tree()
    adjust_reference_tree(a_exclusions, a_mapping)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Consolidate wals data and trees")
    parser.add_argument("tree", default=tree_file_name, nargs='?')
    parser.add_argument("iso_map", default=iso_map, nargs='?')
    parser.add_argument("out", default=reference_tree_file_name,
                        nargs='?')
    parser.add_argument("--language_csv", default=language_csv)
    parser.add_argument("--wals_csv", default=wals_csv)
    args = parser.parse_args()
    language_csv = args.language_csv
    wals_csv = args.wals_csv
    iso_map = args.iso_map
    tree_file_name = args.tree
    reference_tree_file_name = args.out
    main()
