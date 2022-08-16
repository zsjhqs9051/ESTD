import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import shutil
import re
from itertools import islice


class PostProcess():
	def __int__(self):
		pass

	def TimeFolder(self,time):
		T = str(time)
		if not T.find('.'):
			return(str(int(time)))
		else:
			return T
	#read cell area data
	def CellAreaFile(self,time):
		CellFile1 = '%time%/FaceArea'
		CellFile = CellFile1.replace('%time%',self.TimeFolder(time))
		CellArea = []
		with open(CellFile,'r') as f:
			data = f.read()
			start = data.index('(')+1
			end = data.rfind(')')
			data1 = data[start:end]
			data1 = data1.split('\n')
			data = list(filter(None,data1))
		for cell in data:
			CellArea.append(float(cell))
		return CellArea
	#shear read and analysis
	def TauAnalysis(self,time,Casenumber,R_sample):
		PointFile1 = 'postProcessing/sampleDict/%time%/tau/faceCentres'
		TauFile1 = 'postProcessing/sampleDict/%time%/tau/vectorField/wallShearStress'
		PointFile = PointFile1.replace('%time%',self.TimeFolder(time))
		TauFile = TauFile1.replace('%time%',self.TimeFolder(time))
		X = []
		Y = []
		Z = []
		TauX = []
		TauY = []
		TauZ = []
		Tau = []
		with open(PointFile,'r') as f:
			data = f.read()
			start = data.index('(')+1
			end = data.rfind(')')
			data1 = data[start:end].replace('(','').replace(')','')
			data1 = data1.split('\n')
			data = list(filter(None,data1))
		for elements in data:
			element = elements.split(' ')
			X.append(float(element[0]))
			Y.append(float(element[1]))
			Z.append(float(element[2]))
		with open(TauFile,'r') as f:
			data = f.read()
			start = data.index('(')+1
			end = data.rfind(')')
			data1 = data[start:end].replace('(','').replace(')','')
			data1 = data1.split('\n')
			data = list(filter(None,data1))
		for elements in data:
			element = elements.split(' ')
			TauX.append( 997.561 * float(element[0]))
			TauY.append( 997.561 * float(element[1]))
			TauZ.append( 997.561 * float(element[2]))
			taumag = 997.561 * ((float(element[0])) ** 2 + (float(element[1])) ** 2 + (float(element[2])) ** 2) ** 0.5
			Tau.append(taumag)
		#nominal tau
		CellArea = self.CellAreaFile(time)
		project_area = sum(CellArea)
		data1 = list(zip(CellArea,X,Y,Tau))
		TauAnalysis = sorted(data1,key =lambda x:x[3],reverse = True)
		a = []
		b = []
		area_sum = 0
		tau = 0
		tau_average = 0
		for i in range(0,len(TauAnalysis)):
			if area_sum <= project_area:
				area_sum = area_sum + TauAnalysis[i][0]
				tau = TauAnalysis[i][0] * TauAnalysis[i][3] + tau
				tau_average = (tau / area_sum)
				a.append(area_sum * 10000)
				b.append(tau_average)
		plt.figure(0)
		plt.plot(a,b,'-',a[-1],b[-1],'ro')
		plt.ylabel(r'$\tau$ (pa)')
		plt.xlabel('Area$_{cumulate}$ (cm$^2$)')
		plt.title('Nominal Wall Shear Stree of '+ Casenumber)
		content = r'$\tau$ = ' + str(b[-1])[0:5] + ' pa'
		plt.text(a[-1]*0.9,2.25*b[-1],content,backgroundcolor = 'white' )
		figName = Casenumber +'-NominalTau'
		figsave = '../PostProcess/' + figName + '.jpg'
		plt.savefig(figsave,dpi = 1024)
		TauNominal = b[-1]
		plt.close()
		#Tau distribution
		data = list(zip(X,Y,Tau))
		XX = []
		YY = []
		TT = []
		for i in range(0,len(data)):
			r = (data[i][0]**2+data[i][1]**2)**0.5
			if r <= R_sample:
				XX.append(data[i][0]*100)
				YY.append(data[i][1]*100)
				TT.append(data[i][2])
		T1 = sorted(TT)
		MinInd = int(np.floor(0.02 * len(T1)))
		MaxInd = int(np.ceil(0.98 * len(T1)))
		plt.figure(1)
		plt.scatter(XX,YY,s=5,c=TT,cmap='jet',marker = "o", vmin = T1[MinInd], vmax = T1[MaxInd])
		cbar = plt.colorbar()
		cbar.set_label(r'$\tau$ (pa)')
		plt.arrow(-5.5,0,1,0,head_width = 0.4,width = 0.1)
		plt.arrow(-5.5,-1,1,0,head_width = 0.4,width = 0.1)
		plt.arrow(-5.5,1,1,0,head_width = 0.4,width = 0.1)
		plt.text(-5.3,-2,"flow",backgroundcolor = 'white' )
		plt.axis("equal")
		plt.xlabel('X (cm)')
		plt.ylabel('Y (cm)')
		plt.title(Casenumber+' '+r'$\tau$ Distribution')
		figName = Casenumber +'-TauDistribution'
		figsave = '../PostProcess/' + figName + '.jpg'
		plt.savefig(figsave,dpi = 1024)
		plt.close()
		return TauNominal
	#force analysis
	def Force(self,time,Casenumber,R_sample):
		ForceFile = 'postProcessing/Forces/0/forces.dat'
		Fd = []
		Fl = []
		Ftaux = []
		Fx = []
		Time = []
		with open(ForceFile,'r') as f:
			for line in islice(f,4,None):
				data2 = re.sub(' +','\t',line)
				data3 = data2.replace('(','').replace(')','').replace(' ','\t').replace('\n','\t')
				data1 = data3.split('\t')
				data = list(filter(None,data1))
				Time.append(float(data[0]))
				Fd.append(float(data[1]))
				Fl.append(float(data[3]))
				Ftaux.append(float(data[4]))
				Fx.append(float(data[1]) + float(data[4]) + float(data[7]))
		A = np.pi * R_sample**2
		FFd = [i/A for i in Fd]
		FFtaux = [i/A for i in Ftaux]
		FFx = [i/A for i in Fx]
		plt.figure(0)
		plt.figure(dpi = 1024)
		plt.plot(Time,FFd,'rx',markersize = 5,label = 'F$_{d}$/A')
		plt.plot(Time,FFtaux,'g--',markersize = 1,label = r'$\tau$$_{x}$')
		plt.plot(Time,FFx,'y.',markersize = 3,label = 'F$_{x}$/A')
		plt.xlabel('Time (s)')
		plt.ylabel('F$_{d}$/A,   'r'$\tau$$_{x}$'',   F$_{x}$/A (pa)')
		plt.title(Casenumber + ' Force Analysis')
		plt.legend(['F$_{d}$/A',r'$\tau$$_{x}$','F$_{x}$/A'])
		figName = Casenumber +'-ForceAnalysis'
		figsave = '../PostProcess/' + figName + '.jpg'
		plt.savefig(figsave,dpi = 1024)
		plt.close()
		FdA = Fd[-1]/A
		FtauxA = Ftaux[-1]/A
		FxA = Fx[-1]/A
		return FdA,FtauxA,FxA
	#velocity distribution visualization
	def VelocityProfile(self,time,casename):
		plt.figure(0)
		plt.figure(dpi = 1024)
		UFile1 = 'postProcessing/sampleDictU/%time%/'
		UFile = UFile1.replace('%time%',self.TimeFolder(time))
		lines = ['Line1_U.csv','Line2_U.csv','Line3_U.csv','Line4_U.csv']
		symble = ['rs','bx','g+','yo']
		for i in range(0,len(lines)):
			File = UFile + lines[i]
			df = pd.read_csv(File)
			data = df.values.tolist()
			Z = [z[0] * 1000 for z in data]
			Ux = [U[1] * 100 for U in data]
			plt.plot(Ux,Z,symble[i])
		plt.xlabel( 'Ux (cm/s)' )
		plt.ylabel ( ' Depth (mm) ' )
		figName = casename + ' Velocity Distribution'
		plt.title(figName)
		plt.legend(['Line 1','Line 2','Line 3','Line 4'])
		figsave = '../PostProcess/' + figName + '.jpg'
		plt.savefig(figsave,dpi = 1024)
		plt.close()
