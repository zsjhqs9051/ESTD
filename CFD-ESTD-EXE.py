import numpy as np
import pandas as pd
import os
import sys
import shutil
from PostProcess import *
from PrepareProcess import *
from Supports import *
from OpenFOAMConduct import *

for N in range ( len ( sys.argv ) ):
	if N > 0:
		if  sys.argv[N].startswith ( 'c=' ):
			Value = int ( sys.argv[N][2:] )
		else:
			sys.exit ()
	else:
		Value = 16
############input information


R_sample = 0.04
d50 = 1.5 #mm
time = 10  #s
ks = 2 * d50 *0.001
deltaT = 1e-6
maxCo = 150
maxDeltaT = 0.005
TimeControl = { 'MinimumDeltaT': deltaT,
						'TargetDeltaT': maxDeltaT,
						'AllowableTargetCount': maxCo}

CFDModelPath = 'Configure'

SampleSurfacePath = 'test-sample-surface/'
if os.path.exists(SampleSurfacePath):
	shutil.rmtree(SampleSurfacePath)
os.makedirs(SampleSurfacePath)

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
motherPatch = os.getcwd()
logPath1 = 'log.txt'
if os.path.exists(logPath1):
	os.remove(logPath1)

######prepare process
prepare = PrepareProcess()
FlowCondition = prepare.sheetread()

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
		shutil.copytree('Configure',sample)
		#copy sample surface stl file
		src = 'test-sample-surface/' + sample + '.stl'
		dst = sample + '/constant/triSurface/Sample.stl'
		bedcmd = 'surfaceMeshConvert ' + src + ' ' + dst + ' -scaleIn 0.001'
		os.system(bedcmd)
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
		with open (logPath,'a+') as log:
			content = '\t' + sample + ' is meshing!\n'
			log.write(content)
		RunOpenFOAMTool('paraFoam', Options = '-touch' )
		RunOpenFOAMTool('surfaceFeatures' )
		RunOpenFOAMTool('blockMesh' )
		RunOpenFOAMTool('decomposePar' )
		RetCode = RunOpenFOAMTool('snappyHexMesh',Options = '-overwrite',NumberCores = Value,TimeControl = TimeControl )
		RunOpenFOAMTool('reconstructParMesh',Options = '-constant' )
		RunOpenFOAMTool('checkMesh' )
		DeleteProcessors()

		with open (logPath,'a+') as log:
			content = '\t' + sample + ' is running!\n'
			log.write(content)
		RunOpenFOAMTool('decomposePar' )
		RetCode = RunOpenFOAMTool('pimpleFoam',NumberCores = Value,TimeControl = TimeControl )
		RunOpenFOAMTool('reconstructPar',Options = '-latestTime' )
		DeleteProcessors()
		DataSample()
		Datacollection = PostProcess()
		FdA,FtauxA,FxA = Datacollection.Force(time,sample,R_sample)
		TauNominal = Datacollection.TauAnalysis(time, sample,R_sample)
		Datacollection.VelocityProfile(time, sample)
		with open ('../'+dataanalysis,'a+') as f:
			ftitle = sample +'\t' + str(Q * 1000.0) +'\t' \
				+ str(TauNominal) +'\t' + str(FdA) +'\t' \
					+ str(FtauxA) +'\t'  + str(FxA) +'\n'
			f.write (ftitle)
		with open (logPath,'a+') as log:
			content = sample + ' finished!\n\n'
			log.write(content)
		os.chdir(motherPatch)
