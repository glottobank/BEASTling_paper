#!/usr/bin/env python2
import codecs

def main():
    """
    Prepare the cognate data for the Indo-European analysis.  This just
    involves some minor recoding of the original data file to put it
    in CLDF format.
    """
    format_data()

def format_data():
    """
    Convert the original data file to CLDF format.
    """
    fp_in = codecs.open("PIE.csv", "r", "UTF8")
    header = True
    fp_out = codecs.open("indoeuropean.csv", "w", "UTF8")
    for line in fp_in:
        # Skip comment lines.
        if line.startswith("#"):
            continue
        # Despite being called PIE.csv, the original data is tab-delimited.
        row = [x.strip() for x in line.split("\t")]
        # Change column names to CLDF format
        if header:
            row[1] = "Language_ID"
            row[2] = "Feature_ID"
            row[6] = "Value"
            header = False
        # Negative cognate classes indicate borrowings.
        # Replace these with missing data points.
        elif int(row[-1]) < 0:
            row[-1] = "?"
        # Reassemble the row with commas instead of tabs
        row = ",".join(row) + "\n"
        fp_out.write(row)
    fp_out.close
    fp_in.close()

if __name__ == "__main__":
    main()
