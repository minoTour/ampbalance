#!/usr/bin/env python
import mlpy
import sklearn.preprocessing
import random
import math
import csv
import numpy as np
import array as ar
import configargparse
import subprocess
import shutil



parser = configargparse.ArgParser(description='eboladb_squiggle_align: A program providing the ability to determine which region of the ebola genome and individual read is derived from.')
parser.add('-fasta', '--reference_fasta_file', type=str, dest='fasta', required=True, default=None, help="The fasta format file for the reference sequence for your organism.")
parser.add('-ids', nargs = '*', dest='ids',required=True, help = 'A list of start and stop positions for each amplicon from the reference genome')
args = parser.parse_args()



######################################################
# Connect to the database 							 #
######################################################
dbhost = 'localhost'
dbusername = 'minion'
dbpass = 'nan0p0re'
dbport = 3306

limitbases = "50,200"

######################################################
	
######################################################
def get_amplicons():
	for sequence in args.ids:
		print sequence
		start = int(float(sequence.split(':', 1 )[1].split('-',1)[0]))
		stop = int(float(sequence.split(':', 1 )[1].split('-',1)[1]))
		print start
		print stop
		REVERSE_stop = seqlengths['EM_079517']-start
		REVERSE_start = seqlengths['EM_079517']-stop
		print REVERSE_stop
		print REVERSE_start

######################################################
def get_seq_len(ref_fasta):
	seqlens=dict()
	for record in SeqIO.parse(ref_fasta, 'fasta'):
		seq=record.seq
		seqlens[record.id]=len(seq)
	return seqlens

#######################################################################
def runProcess(exe):
	p=subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	while(True):
		retcode= p.poll()
		line=p.stdout.readline()
		yield line
		if(retcode is not None):
			break
	
#######################################################################
def squiggle_search(squiggle,kmerhash2,channel_id,read_id,seqlen):
	result=[]
	for id in kmerhash2:
		for ref in kmerhash2[id]:
			#print len(kmerhash2[id][ref]['F'])
			queryfile=str(channel_id)+"_"+str(read_id)+"_query.bin"
			#We are going to normalise this sequence with the sklearn preprocessing algorithm to see what happens.		
			queryarray = sklearn.preprocessing.scale(np.array(squiggle),axis=0,with_mean=True,with_std=True,copy=True)
			#queryarray = np.array(squiggle)
			with open(queryfile, "wb") as f:
				f.write(ar.array("f", queryarray))
			subjectfile = id+"_"+str(ref)+"_"+"F"+"_subject.bin"
			subjectfile = re.sub('\|','_',subjectfile)
			#seqlen2 = str(seqlen[id])
			commands = queryfile+' '+subjectfile+' 200 '+str(len(kmerhash2[id][ref]['F']))+' 0.05'
			#print commands
			#current = str(multiprocessing.current_process())
			#currentnum=int(re.search(r'\d+', current).group())
			gpucode=str()
			#if (currentnum % 2 == 0):
				#print "Even"
			gpucode='./GPU-DTW '
			#else:
			#	#print "Odd"
			#	gpucode='./GPU-DTW '
			runcommand = gpucode+commands
			location = ()
			distance = ()
			for line in runProcess(runcommand.split()):
				if "Location" in line:			
					location = int(line.split(': ',1)[1].rstrip('\n'))
				if "Distance" in line:
					distance = float(line.split(': ',1)[1].rstrip('\n'))
			result.append((distance,id,"F",location,ref))
			subjectfile = id+"_"+str(ref)+"_"+"R"+"_subject.bin"
			subjectfile = re.sub('\|','_',subjectfile)
			#seqlen2 = str(seqlen[id])
			commands = queryfile+' '+subjectfile+' 200 '+str(len(kmerhash2[id][ref]['R']))+' 0.05'
			#print commands
			#current = str(multiprocessing.current_process())
			#currentnum=int(re.search(r'\d+', current).group())
			gpucode=str()
			#if (currentnum % 2 == 0):
				#print "Even"
			gpucode='./GPU-DTW '
			#else:
			#	#print "Odd"
			#	gpucode='./GPU-DTW '
			runcommand = gpucode+commands
			location = ()
			distance = ()
			for line in runProcess(runcommand.split()):
				if "Location" in line:			
					location = int(line.split(': ',1)[1].rstrip('\n'))
				if "Distance" in line:
					distance = float(line.split(': ',1)[1].rstrip('\n'))
			result.append((distance,id,"R",location,ref))
			os.remove(queryfile)

	return sorted(result,key=lambda result: result[0])[0][1],sorted(result,key=lambda result: result[0])[0][0],sorted(result,key=lambda result: result[0])[0][2],sorted(result,key=lambda result: result[0])[0][3],sorted(result,key=lambda result: result[0])[0][4]

#######################################################################
def squiggle_search3(squiggle,kmerhash2,channel_id,read_id,seqlen):
	result=[]
	for id in kmerhash2:
		for ref in kmerhash2[id]:
			#print len(kmerhash2[id][ref]['F'])
			queryfile=str(channel_id)+"_"+str(read_id)+"_query.txt"
			#We are going to normalise this sequence with the sklearn preprocessing algorithm to see what happens.		
			queryarray = sklearn.preprocessing.scale(np.array(squiggle),axis=0,with_mean=True,with_std=True,copy=True)
			#queryarray = np.array(squiggle)
			np.savetxt(queryfile, queryarray, delimiter=',')
			subjectfile = id+"_"+str(ref)+"_"+"F"+"_subject.txt"
			subjectfile = re.sub('\|','_',subjectfile)
			#seqlen2 = str(seqlen[id])
			commands = subjectfile+' '+queryfile+' 200	 0.1'
			#print commands
			#current = str(multiprocessing.current_process())
			#currentnum=int(re.search(r'\d+', current).group())
			gpucode=str()
			#if (currentnum % 2 == 0):
				#print "Even"
			gpucode='./UCR_DTW '
			#else:
			#	#print "Odd"
			#	gpucode='./GPU-DTW '
			runcommand = gpucode+commands
			#print runcommand
			location = ()
			distance = ()
			for line in runProcess(runcommand.split()):
				#print line
				if "Location" in line:			
					location = int(line.split(': ',1)[1].rstrip('\n'))
					#print location
				if "Distance" in line:
					distance = float(line.split(': ',1)[1].rstrip('\n'))
					#print distance
			result.append((distance,id,"F",location,ref))
			subjectfile = id+"_"+str(ref)+"_"+"R"+"_subject.txt"
			subjectfile = re.sub('\|','_',subjectfile)
			#seqlen2 = str(seqlen[id])
			commands = subjectfile+' '+queryfile+' 200'+' 0.1'
			#print commands
			#current = str(multiprocessing.current_process())
			#currentnum=int(re.search(r'\d+', current).group())
			gpucode=str()
			#if (currentnum % 2 == 0):
				#print "Even"
			gpucode='./UCR_DTW '
			#else:
			#	#print "Odd"
			#	gpucode='./GPU-DTW '
			runcommand = gpucode+commands
			#print runcommand
			location = ()
			distance = ()
			for line in runProcess(runcommand.split()):
				if "Location" in line:			
					location = int(line.split(': ',1)[1].rstrip('\n'))
				if "Distance" in line:
					distance = float(line.split(': ',1)[1].rstrip('\n'))
			result.append((distance,id,"R",location,ref))
			os.remove(queryfile)

	return sorted(result,key=lambda result: result[0])[0][1],sorted(result,key=lambda result: result[0])[0][0],sorted(result,key=lambda result: result[0])[0][2],sorted(result,key=lambda result: result[0])[0][3],sorted(result,key=lambda result: result[0])[0][4]

#######################################################################
def squiggle_search2(squiggle,kmerhash2,channel_id,read_id,seqlen):
	result=[]
	for id in kmerhash2:
		for ref in kmerhash2[id]:
			#print len(kmerhash2[id][ref]['F'])
			queryfile=str(channel_id)+"_"+str(read_id)+"_query.bin"
			#We are going to normalise this sequence with the sklearn preprocessing algorithm to see what happens.		
			queryarray = sklearn.preprocessing.scale(np.array(squiggle),axis=0,with_mean=True,with_std=True,copy=True)
			
			dist, cost, path = mlpy.dtw_subsequence(queryarray,kmerhash2[id][ref]['Fprime'])
			result.append((dist,id,"F",path[1][0],ref))
			dist, cost, path = mlpy.dtw_subsequence(queryarray,kmerhash2[id][ref]['Rprime'])
			result.append((dist,id,"R",path[1][0],ref))
			

	return sorted(result,key=lambda result: result[0])[0][1],sorted(result,key=lambda result: result[0])[0][0],sorted(result,key=lambda result: result[0])[0][2],sorted(result,key=lambda result: result[0])[0][3],sorted(result,key=lambda result: result[0])[0][4]

######################################################################

#######################################################
# Retrieve a model from the database rather than the  #
# expected data 									  #

def retrieve_model():
	model_kmers = dict()
	db = MySQLdb.connect(host=dbhost, user=dbusername, passwd=dbpass, port=dbport)
	sql = "SELECT * FROM minion_LomanLabz_013731_11rx_v2_3135.model_data where model like '%template%'"
	cursor.execute(sql)			
	kmerresults = cursor.fetchall()
	for line in kmerresults:
		kmer = line[2]
		mean = line[4]
		#print kmer,mean
		model_kmers[kmer]=mean
	return model_kmers

							
	kmer_means2=dict()
	
	for record in SeqIO.parse(ref_fasta, 'fasta'):
		counter = 1
		kmer_means2[record.id]=dict()
		for amplicon in args.ids:
			kmer_means2[record.id][counter]=dict()
			kmer_means2[record.id][counter]["F"]=list()
			kmer_means2[record.id][counter]["R"]=list()
			print amplicon
			seq = record.seq
			#print seq
			start = int(float(amplicon.split(':', 1 )[1].split('-',1)[0]))
			stop = int(float(amplicon.split(':', 1 )[1].split('-',1)[1]))
			newseq=seq[start:stop]
			print "Length of newseq:",len(newseq)
			shortregion=round(len(newseq)/2)
			print shortregion
			for x in range(int(shortregion)):
			print counter,"F",newseq
			newseq2 = revcomp = newseq.reverse_complement()
			#for x in range(len(newseq2)+1-kmer_len):
			for x in range(int(shortregion)):
			print counter,"R",newseq2
			kmer_means2[record.id][counter]["Fprime"]=sklearn.preprocessing.scale(kmer_means2[record.id][counter]["F"], axis=0, with_mean=True, with_std=True, copy=True)
			kmer_means2[record.id][counter]["Rprime"]=sklearn.preprocessing.scale(kmer_means2[record.id][counter]["R"], axis=0, with_mean=True, with_std=True, copy=True)
			counter += 1
			
			
		kmer_means[record.id]["Fprime"]=list()
		kmer_means[record.id]["Rprime"]=list()
		kmer_means[record.id]["Rprime"]=sklearn.preprocessing.scale(kmer_means[record.id]["R"], axis=0, with_mean=True, with_std=True, copy=True)


fasta_file = args.fasta
#fasta_file = "EM_079517.fasta"
model_kmer_means = retrieve_model()
seqlengths = get_seq_len(fasta_file)
print seqlengths['EM_079517']
get_amplicons()


for id in kmerhash2:
		for ref in kmerhash2[id]:
			print id,ref
			#print (kmerhash2[id][ref]['F'])
			testarray = kmerhash2[id][ref]['Fprime']
			filename = id+"_"+str(ref)+"_F_subject.bin"
			filename = re.sub('\|','_',filename)			
			with open(filename, "wb") as f:
				f.write(ar.array("f", testarray))
			filename = id+"_"+str(ref)+"_F_subject.txt"
			filename = re.sub('\|','_',filename)
			np.savetxt(filename, testarray, delimiter=',')
			testarray = kmerhash2[id][ref]['Rprime']
			filename = id+"_"+str(ref)+"_R_subject.bin"
			filename = re.sub('\|','_',filename)			
			with open(filename, "wb") as f:
				f.write(ar.array("f", testarray))
			filename = id+"_"+str(ref)+"_R_subject.txt"
			filename = re.sub('\|','_',filename)
			np.savetxt(filename, testarray, delimiter=',')


#ecit




db = MySQLdb.connect(host=dbhost, user=dbusername, passwd=dbpass, port=dbport)
#sql = "use minion_PLSP57501_2014_10_10_DSmin1_run2_LambdaSK002_5041"
#sql = "use minion_PLSP57501_20140909_JA_defA_4434"
sql = "use minion_LomanLabz_013731_11rx_v2_3135"
print sql
cursor.execute(sql)

numbers = range(0,10)

for number in numbers:
	#print number

	sql = "SELECT basename_id ,pos,flag, channel, read_id,tracking_id.basename,file_path FROM caller_basecalled_template_%s inner join align_sam_basecalled_2d using (basename_id) inner join config_general using (basename_id) inner join tracking_id using (basename_id) group by basename_id limit 1" %(number)
	#sql = "SELECT basename_id , channel, read_id FROM caller_basecalled_template_%s inner join config_general using (basename_id) where basename_id not in (select basename_id from align_sam_basecalled_template) group by basename_id" %(number)
	print sql
					
	
	
	basenameids = cursor.fetchall()
	
	#print basenameids
	
	for ids in basenameids:
		#print ids[0]
		sql = "SELECT mean FROM caller_basecalled_template_%s where basename_id = %s limit %s" % (number,ids[0],limitbases)
		#print sql
		#sql = "SELECT mean FROM caller_basecalled_template where basename_id = %s " % (ids[0]) 
		cursor.execute(sql)
		means = cursor.fetchall()
		meanlist = list()
		for mean in means:
			meanlist.append(float(mean[0]))
		
		#print len(meanlist)
		#print squiggle_search3(meanlist,kmerhash2,ids[3],ids[4],seqlengths),
		#print squiggle_search(meanlist,kmerhash2,ids[3],ids[4],seqlengths),
		matchseq,dist,orientation,matchstart,amplicon = squiggle_search2(meanlist,kmerhash2,ids[3],ids[4],seqlengths)
		print matchseq,dist,orientation,matchstart,amplicon,
		x=np.array(meanlist)
		Xprime = sklearn.preprocessing.scale(x, axis=0, with_mean=True, with_std=True, copy=True)
		result_sum=dict()
		scale_result_sum=dict()
		
		if not os.path.exists('symsplit'):
			os.makedirs('symsplit')
		destdir = os.path.join('symsplit',str(amplicon),'downloads')    	
		if not os.path.exists(destdir):
			os.makedirs(destdir)
		
		print ids[6],
		sourcefile = ids[6]

		filename = ids[5]+'.fast5'
		destfile = os.path.join(destdir,filename)
		print "sourcefile is:",sourcefile
		print "destfile is:",destfile
		#os.symlink(sourcefile, destfile)
		
		for seqid in kmerhash:
			y=np.array(kmerhash[seqid]["F"])
			z=np.array(kmerhash[seqid]["R"])
			
			Yprime = np.array(kmerhash[seqid]["Fprime"])
			Zprime = np.array(kmerhash[seqid]["Rprime"])
			
			dist, cost, path = mlpy.dtw_subsequence(Xprime,Yprime)
			secondarray=path[1]
			scale_result_sum[dist]=dict()
			scale_result_sum[dist][seqid]=dict()
			scale_result_sum[dist][seqid]["F"]=list()
			scale_result_sum[dist][seqid]["F"].append(secondarray[0])
			
			dist, cost, path = mlpy.dtw_subsequence(Xprime,Zprime)
			secondarray=path[1]
			scale_result_sum[dist]=dict()
			scale_result_sum[dist][seqid]=dict()
			scale_result_sum[dist][seqid]["R"]=list()
			scale_result_sum[dist][seqid]["R"].append(secondarray[0])
			
			print (ids[0],ids[1],ids[2],ids[3],ids[4]),
			#print (ids[0],ids[1],ids[2]),

			for key in sorted(scale_result_sum):
			    for seqid in scale_result_sum[key]:
			    	for direct in scale_result_sum[key][seqid]:
			    		for pos in scale_result_sum[key][seqid][direct]:
			    			if not 25000<pos<30000:
			    				print "SEQID",(seqid),
			    				print "POS",(pos),
			    				print "DIRECT",(direct),
			    				print "KEY",key
			    			else:
			    				print "SEQID",(seqid),
			    				print "POS",(pos),
			    				print "DIRECT",(direct),
			    				print "KEY",key
			    break