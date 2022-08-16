import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import shutil
import glob
import vtk
from mayavi import mlab
from scipy.spatial import Delaunay

class PrepareProcess():
	__file = glob.glob(os.path.join('Experiment','*.xlsx'))
	
	def __int__(self):
		pass
	#read ESTD experiment data, include flow rate and surface scan data
	def sheetread(self):
		expfile = self.__file[0]
		df = pd.ExcelFile(expfile)
		flowdata = df.sheet_names[0]
		FlowState = pd.read_excel(expfile,sheet_name = flowdata).values
		flowCondition = {}
		for i in range(0,len(FlowState)):
			key = df.sheet_names[i+1]
			value = FlowState[i][2]
			flowCondition[key] = value
		return flowCondition
	#generate the stl for scan XXX
	def scanbed(self,scan):
		X1 = []
		Y1 = []
		Z1 = []
		expfile = self.__file[0]
		bedxyz = pd.read_excel(expfile,sheet_name = scan).values
		for cood in bedxyz:
			X1.append(cood[0])
			Y1.append(cood[1])
			Z1.append(cood[2])
		X = []
		Y = []
		Z = []
		Rs = [40,40.5,41]
		thetas = np.linspace(0,2*np.pi,720)
		for theta in thetas:
			for R in Rs:
				x = R * np.cos(theta)
				y = R * np.sin(theta)
				z = 0
				X.append(x)
				Y.append(y)
				Z.append(z)
		for i in range(0,len(X1)):
			l2 = ((X1[i])**2 + (Y1[i])**2)**0.5
			if l2 <= 40.0:
				X.append(X1[i])
				Y.append(Y1[i])
				Z.append(Z1[i])
		xy = np.column_stack((X,Y))
		tri = Delaunay(xy)
		element = tri.simplices
		surface = mlab.pipeline.triangular_mesh_source(X,Y,Z,element)
		surface_vtk = surface.outputs[0]._vtk_obj
		stlWriter = vtk.vtkSTLWriter()
		FR_index = scan.index('F')
		name = scan[0:FR_index] + '.stl'
		bedname = scan[0:FR_index].replace(' ','')
		scanbed = 'test-sample-surface/' + name.replace(' ','')
		stlWriter.SetFileName(scanbed)
		stlWriter.SetInputConnection(surface_vtk.GetOutputPort())
		stlWriter.Write()
		mlab.close()
		return bedname