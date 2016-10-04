import csv

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
    ranked = [(means[key],key) for key in means if "featureClockRate:" in key]
    ranked.sort()
    # Save ranked means
    fp = open(outfile, "w")
    for mean, key in ranked:
        fp.write("%s,%f\n" % (key, mean))
    fp.close()
    return ranked
