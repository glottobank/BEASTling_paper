import csv

def prepare_log_file(infile, outfile):
    fp_in = open(infile,"r")
    fp_out = open(outfile,"w")
    for line in fp_in:
        if not line.startswith("#"):
            fp_out.write(line)
    fp_in.close()
    fp_out.close()

bad_keys = ("posterior", "likelihood", "prior","clockRate", "birthRate", \
    "Sample")
bad_subkeys = ("covarion", "GammaShape")

def want(key):
    return not(key in bad_keys or \
            any([s in key for s in bad_subkeys]))

def write_means(logfile, outfile):
    fp = open(logfile,"r")
    reader = csv.DictReader(fp, delimiter="\t")
    # Find number of samples
    N = 0
    for row in reader:
        N += 1
    # Rewind file
    fp.seek(0)
    # Skip over 10% burnin
    for i in range(0, int(0.1*N)):
        reader.next()
    # Compute means from remaining 90%
    means = {}
    for field in reader.fieldnames:
        if field:
            means[field] = 0
    for row in reader:
        for key in row:
            if key:
                means[key] += float(row[key])
    means = {key:means[key]/N for key in means}
    fp.close()
    # Rank columns by mean values
    ranked = [(means[key],key) for key in means if want(key)]
    ranked.sort()
    # Save ranked means
    fp = open(outfile, "w")
    for mean, key in ranked:
        fp.write("%s,%f\n" % (key, mean))
    fp.close()
    return ranked
