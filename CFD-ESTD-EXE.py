import numpy as np
import pandas as pd
import os
import sys
import shutil
from PostProcess import *
from PrepareProcess import *
from Supports import *
from OpenFOAMConduct import *

#command information python CFD-ESTD-EXE.py [c=16] [g=3]
#c is the processor number of each case, default value is 16
#g is the subprocessor number,default value is 1
Value = 16
Group = 3
for cmd in sys.argv:
	if cmd.startswith ( 'c=' ):
		Value = int ( cmd[2:] )
	if  cmd.startswith ( 'g=' ):
		Group = int ( cmd[2:] )

#CFD information
#radius of the hole on the channel bed
R_sample = 0.04      #m

#input the d50 of soil sample
d50 = 1.5      #mm

#physical time
time = 10      #s


ks = 2 * d50 *0.001
deltaT = 1e-6
maxCo = 150
maxDeltaT = 0.005
TimeControl = { 'MinimumDeltaT': deltaT,
						'TargetDeltaT': maxDeltaT,
						'AllowableTargetCount': maxCo}

#necessary folder route
#Openfoam Model Template
CFDModelPath = 'Configure'

#folder to save the generated soil sample surface stl
SampleSurfacePath = 'test-sample-surface'
foldergenerator(SampleSurfacePath)

# #folder to save postprocessor data
# postFolder = 'PostProcess/'
# foldergenerator(postFolder)
# dataanalysis = 'PostProcess/DataAnalysis.txt'
# if os.path.exists(dataanalysis):
# 	os.remove(dataanalysis)
# with open (dataanalysis,'a+') as f:
# 	ftitle = 'Case\tFlow Rate (L/s)\t' + 'tau_nominal (pa)'\
# 		+'\tFd/A (pa)\ttau_x (pa)\tFx/A (pa)\n'
# 	f.write (ftitle)
# 	
#log file

logPath1 = 'log.txt'
if os.path.exists(logPath1):
	os.remove(logPath1)
	
motherPatch = os.getcwd()

	
######prepare process
prepare = PrepareProcess()
FlowCondition = prepare.sheetread()
CFDCaseName = []
for sample1 in FlowCondition.keys():
	print(sample1)
	sample = prepare.scanbed(sample1)
	with open (logPath1,'a+') as log:
		content = sample + ':\n'
		log.write(content)
	logPath = '../' + logPath1
	Q = FlowCondition[sample1] * 1e-3
	U,k, epsilon,nut,Re = kEpsilon(Q)
	if os.path.exists(sample):
		shutil.rmtree(sample)

	if Re <= 15000:
		with open (logPath1,'a+') as log:
			content = '\t' + sample + ' is laminar flow!\n'
			log.write(content)
	else:
		CFDCaseName.append(sample)
		shutil.copytree('Configure',sample)
		#copy sample surface stl file
		src = 'test-sample-surface/' + sample + '.stl'
		dst = sample + '/constant/triSurface/Sample.stl'
		#bedcmd = 'surfaceMeshConvert ' + src + ' ' + dst + ' -scaleIn 0.001'
		#os.system(bedcmd)
		#prepare openfoam model
		os.chdir(sample)
		replacedict = {'d50':str(ks),'flowrate':str(Q),'U':str(U),'k':str(k),'epsilon':str(epsilon),'nut':str(nut)}
		route = '0/flowCondition'
		replacement(route,replacedict)
		route = 'system/decomposeParDict'
		replacedict = {'NumCoresSolver' : str(Value)}
		replacement(route,replacedict)
		route = 'system/controlDict'
		replacedict = {'physicalTime' : str(time),'deltaT' : str(deltaT),\
				 'maxCo' : str(maxCo),'maxDeltaT' : str(maxDeltaT)}
		replacement(route,replacedict)
		os.chdir(motherPatch)
#Group CFD models
for i in range(Group):
	GroupFolder = 'Group' + str(i)
	if os.path.exists(GroupFolder):
			os.remove(GroupFolder)
	os.mkdir(GroupFolder)
for i in range(len(CFDCaseName)):
	srcCFD = CFDCaseName[i]
	GroupNo = int(i%Group)
	tgtCFD = 'Group' + str(GroupNo) + '/' + CFDCaseName[i]
	shutil.move(srcCFD,tgtCFD)

		#with open (logPath,'a+') as log:
		#	content = '\t' + sample + ' is meshing!\n'
		#	log.write(content)
		#RunOpenFOAMTool('paraFoam', Options = '-touch' )
		#RunOpenFOAMTool('surfaceFeatures' )
		#RunOpenFOAMTool('blockMesh' )
		#RunOpenFOAMTool('decomposePar' )
		#RetCode = RunOpenFOAMTool('snappyHexMesh',Options = '-overwrite',NumberCores = Value,TimeControl = TimeControl )
		#RunOpenFOAMTool('reconstructParMesh',Options = '-constant' )
		#RunOpenFOAMTool('checkMesh' )
		#DeleteProcessors()

		#with open (logPath,'a+') as log:
		#	content = '\t' + sample + ' is running!\n'
		#	log.write(content)
		#RunOpenFOAMTool('decomposePar' )
		#RetCode = RunOpenFOAMTool('pimpleFoam',NumberCores = Value,TimeControl = TimeControl )
		#RunOpenFOAMTool('reconstructPar',Options = '-latestTime' )
		#DeleteProcessors()
		#DataSample()
		#Datacollection = PostProcess()
		#FdA,FtauxA,FxA = Datacollection.Force(time,sample,R_sample)
		#TauNominal = Datacollection.TauAnalysis(time, sample,R_sample)
		#Datacollection.VelocityProfile(time, sample)
		#with open ('../'+dataanalysis,'a+') as f:
		#	ftitle = sample +'\t' + str(Q * 1000.0) +'\t' \
		#		+ str(TauNominal) +'\t' + str(FdA) +'\t' \
		#			+ str(FtauxA) +'\t'  + str(FxA) +'\n'
		#	f.write (ftitle)
		#with open (logPath,'a+') as log:
		#	content = sample + ' finished!\n\n'
		#	log.write(content)
		#os.chdir(motherPatch)
