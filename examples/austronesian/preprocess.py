#!/usr/bin/env python2
import csv
import subprocess
import sys

import newick

sys.path.append("..")
import utils

def load_wals_iso_names():
    fp = open("language.csv","r")
    reader = csv.DictReader(fp)
    mapping = {}
    for row in reader:
        if row["iso_code"] != "?":
            mapping[row["Name"]] = row["iso_code"]
    fp.close()
    all_isos = [i for i in mapping.values()]
    duplicates = [l for l in mapping if all_isos.count(mapping[l]) > 1]
    return mapping, duplicates

def reformat_wals(killable_names):
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
        if row["Name"].lower() in killable_names:
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
    fp_in = open("a400-m1pcv-time.mcct.trees", "r")
    fp_out = open("austronesian_reference.nex", "w")
    for line in fp_in:
        # Skip comments and NEXUS cruft
        if not line.startswith("tree"):
            continue
        # Trim "tree TREE1 = " from tree line
        line = line[13:]
        # Remove named internal nodes, which confuse phyltr
        bad_strings = (
                "centralpacific",
                "malayicchamic",
                "micronesian",
                "PAN",
                "PMP",
                "protochamic",
                "protojavanese",
                "protomalagasy",
                "polynesian",
                "protooceanic",
                "protorsc",
                "root",
                "tuvtok",
                )
        for bad_string in bad_strings:
            line = line.replace(bad_string, "")
        fp_out.write(line)
    fp_in.close()
    fp_out.close()

def load_austro_iso_names():
    fp = open("iso.austronesian.txt", "r")
    untranslatable = []
    mapping = {}
    # Separate languages with ISO codes from those without
    for line in fp:
        iso, lang = [x.strip() for x in line.split("\t")]
        if iso == "XXX":
            untranslatable.append(lang)
        else:
            mapping[lang] = iso
    fp.close()
    # Check for duplicated ISO codes
    all_isos = [i for i in mapping.values()]
    duplicates = [l for l in mapping if all_isos.count(mapping[l]) > 1]
    return (untranslatable, mapping, duplicates)

def make_phyltr_rename_file(translation):
    fp = open("phyltr_rename.txt", "w")
    for lang in translation:
        fp.write("%s:%s\n" % (lang, translation[lang]))
    fp.close()

def resolve_duplicates(a_trans, a_dupes, w_trans, w_dupes):
    killable_austro_langs = []
    killable_wals_langs = []
    austro_duped_isos = set([a_trans[l] for l in a_dupes])
    # First, iterated over all ISO codes which are duplicated in the refrence
    # Austronesian tree.  Get all of the names in the ref. tree which map to
    # an ISO, and all of the names in WALS which map to that ISO.  Find the
    # intersection (i.e. those names used by both).  If there is one such
    # common name, identify these as the same language and kill all the
    # others.  If there is no name overlap, kill everything.
    for iso in austro_duped_isos:
        a_names = set([l.lower() for l in a_trans if a_trans[l] == iso])
        w_names = set([l.lower() for l in w_trans if w_trans[l] == iso])
        true_name = a_names.intersection(w_names)
        if len(true_name) == 1:
            # Keep the common name, kill others
            killable_austro_langs.extend(a_names.difference(true_name))
            killable_wals_langs.extend(w_names.difference(true_name))
        else:
            # Kill everything
            killable_austro_langs.extend(a_names)
            killable_wals_langs.extend(w_names)
    for a in killable_austro_langs:
        if a in a_dupes:
            a_dupes.remove(a)
    for w in killable_wals_langs:
        if w in w_dupes:
            w_dupes.remove(w)
    # Now there might be ISO codes which are duplicates in WALS but not the
    # reference tree.
    wals_duped_isos = set([w_trans[l] for l in w_dupes])
    for iso in wals_duped_isos:
        a_names = set([l.lower() for l in a_trans if a_trans[l] == iso])
        w_names = set([l.lower() for l in w_trans if w_trans[l] == iso])
        true_name = a_names.intersection(w_names)
        if len(true_name) == 1:
            # Keep the common name, kill others
            killable_wals_langs.extend(w_names.difference(true_name))
        else:
            killable_wals_langs.extend(w_names)
    return killable_austro_langs, killable_wals_langs

def adjust_reference_tree(translation, kill_list):
    make_phyltr_rename_file(translation)
    kill_list = ",".join(kill_list)
    command = "phyltr prune %s austronesian_reference.nex | " \
            "phyltr rename -f phyltr_rename.txt > " \
            "austronesian.nex" % kill_list
    subprocess.call(command, shell=True)
    # ete2 (hence phyltr) writes trees with exponential notation lengths
    # BEAST chokes on these
    # So, use newick module to fix this.  Kind of gross!
    root = newick.read("austronesian.nex")[0]
    for d in root.walk():
        if not d.length:
            continue
        length = float(d.length)
        d.length = "%f" % length
    newick.write([root], "austronesian.nex")
    # Save a BEASTling compatible list of ISO codes
    isos = [n.name for n in root.walk() if n.is_leaf]
    fp = open("language_list.txt", "w")
    for iso in isos:
        fp.write("%s\n" % iso)
    fp.close()

def main():

    print("Resolving ISO codes...")
    untranslatable, austro_translation, austro_duplicates = load_austro_iso_names()
    wals_translation, wals_duplicates = load_wals_iso_names()
    killable_austro, killable_wals = resolve_duplicates(austro_translation, \
            austro_duplicates, wals_translation, wals_duplicates)
    print("Reformatting WALS data...")
    reformat_wals(killable_wals)
    print("Preparing reference tree...")
    clean_reference_tree()
    killable_austro.extend(untranslatable)
    killable_austro.extend(austro_duplicates)
    adjust_reference_tree(austro_translation, killable_austro)

if __name__ == "__main__":
    main()
