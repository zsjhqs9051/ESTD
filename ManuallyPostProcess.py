import numpy as np
import pandas as pd
import os
import sys
import shutil
from PostProcess import *
#from PrepareProcess import *

postFolder = 'PostProcess/'
if os.path.exists(postFolder):
	shutil.rmtree(postFolder)
os.makedirs(postFolder)
dataanalysis = 'PostProcess/DataAnalysis.txt'
if os.path.exists(dataanalysis):
	os.remove(dataanalysis)
with open (dataanalysis,'a+') as f:
	ftitle = 'Case\tFlow Rate (L/s)\t' + 'tau_nominal (pa)'\
		+'\tFd/A (pa)\ttau_x (pa)\tFx/A (pa)\n'
	f.write (ftitle)

PP = PostProcess()
samplea = 'scan#'
i = 0
time = 10
Fd = 0
Ftaux = 0
Fx = 0
R_sample = 0.04

while i <= 90:
	sample = samplea + str(int(i))
	if os.path.exists(sample):
		print(sample)
		flowdatafile = sample + '/0/flowCondition'
		with open (flowdatafile) as f:
			data = f.readlines()
			flowrate = data[1].replace(';','').replace('flowrate','').replace('\t','').replace('\n','')
			Q = float(flowrate)*1000

		motherPatch = os.getcwd()
		os.chdir(sample)
		dataanalysis = 'PostProcess/DataAnalysis.txt'

		TauNominal = PP.TauAnalysis(time, sample,R_sample)
		Fd,Ftaux,Fx = PP.Force(time, sample,R_sample)
		PP.VelocityProfile(time, sample)


		with open ('../'+dataanalysis,'a+') as f:
			ftitle = sample +'\t' + str(Q)[0:8] +'\t' \
				+ str(TauNominal)[0:8] +'\t' + str(Fd)[0:8] +'\t' \
					+ str(Ftaux)[0:8] +'\t'  + str(Fx)[0:8] +'\n'
			f.write (ftitle)
		os.chdir(motherPatch)
	i = i+1
