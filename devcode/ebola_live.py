#!/usr/bin/env python

parser = configargparse.ArgParser(description='eboladb_squiggle_align: A program providing the ability to determine which region of the ebola genome and individual read is derived from.')
parser.add('-fasta', '--reference_fasta_file', type=str, dest='fasta', required=True, default=None, help="The fasta format file for the reference sequence for your organism.")
parser.add('-ids', nargs = '*', dest='ids',required=True, help = 'A list of start and stop positions for each amplicon from the reference genome')
parser.add('-w', '--watch-dir', type=str, required=True, default=None, help="The path to the folder containing the downloads directory with fast5 reads to analyse - e.g. C:\data\minion\downloads (for windows).", dest='watchdir')
args = parser.parse_args()


#########################################################