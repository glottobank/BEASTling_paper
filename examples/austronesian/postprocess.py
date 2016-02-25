#!/usr/bin/env python2
import sys

sys.path.append("..")
import utils

def main():

    print("Computing posterior mean paramter estimates...")
    utils.prepare_log_file("austronesian.log", "prepared.log")
    utils.write_means("prepared.log", "parameter_means.csv")

if __name__ == "__main__":
    main()
