import numpy as np
import pandas as pd
import os
import sys
import shutil
import time

def replacement(route,replacedict = {}):
	with open(route) as file:
		content = file.read()
	for key, value in replacedict.items():
		keyword = '%' + key + '%'
		content = content.replace(keyword,value)
	with open(route,'w') as newfile:
		newfile.write(content)

def kEpsilon(Q):
	rho = 997.561
	viscosity = 8.90883E-07
	C_nu = 0.09
	width = 0.12
	depth = 0.0195
	U = Q/(width*depth)
	#hydraulic parameters
	A = width*depth
	Pw = 2.0*depth + 2.0*width
	Rh = A/Pw
	Dh = 4*Rh
	Re = U*Dh/viscosity
	I = 0.16*Re**(-0.125)
	k = 1.5*(U*I)**2.0
	epsilon = 0.164*k**1.5/(0.07*Dh)
	nut = C_nu*k**2/epsilon
	return U,k, epsilon,nut,Re

def TimeStamp ():
	return time.strftime ( '%Y-%m-%d %H:%M:%S: ' )

class SimpleLog ( ):
	def __init__ ( self, FileName=None ):
		self.File = None
		if FileName is not None:
			self.File = open ( FileName, 'a' )
			self.File.write ( '\n' )
			self.File.write ( '\n' )
	def Log ( self, *Args ):
		Message = ' '.join ( map ( str, Args ) )
		if self.File is not None:
			for Line in Message.rstrip ().split ( '\n' ):
				self.File.write ( TimeStamp () + Line.rstrip () + '\n' )
		else:
			for Line in Message.rstrip ().split ( '\n' ):
				print (TimeStamp() + Line.rstrip())
	def Flush ( self ):
		if self.File is not None:
			self.File.flush ()
		else:
			sys.stdout.flush ()
	def __del__ ( self ):
		if self.File is not None:
			self.File.close ()
