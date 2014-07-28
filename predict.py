#!/usr/bin/python
import math
import random
class Weight:
	def __init__(self, d):
		print "Init "+str(d)
		self.d=d
		self.w=[]
		for i in range(len(self.d)):
			if d[0][i]<.001:
				self.w.append(0)
			else:
				self.w.append(1.0/self.d[i])
		print "W="+str(self.w[0])
		#return self.w

	def __call__(self):
		print "Call-W "+str(self.w)
		print "Calling"
		return self.w
		
class Predictor:
	def inverse(d):
		w=[]
		for i in range(len(self.d)):
			if d[0][i]<.001:
				w.append(0)
			else:
				w.append(1.0/self.d[i])
		return w
		
	lines=[[]]
	norm_lines=[[]]
	knn_orig_x=[]
	knn_orig_y=[]
	knn_final_x=[]
	knn_final_y=[]
	allow_knn=True
	def predict(self,fromPoint, toPoint):
		return self.lines[toPoint]

	def predict_KNN(self,fromPoint, toPoint):
		from sklearn import preprocessing
		from sklearn.neighbors import KNeighborsRegressor
		neigh_x = KNeighborsRegressor(n_neighbors=7,algorithm='kd_tree')
		neigh_y = KNeighborsRegressor(n_neighbors=7,algorithm='kd_tree')
		#print "fromPoint="+str(fromPoint)+" "+str(toPoint)
		Xorig=  self.knn_orig_x[0]
		Xfinal=  self.knn_final_x[toPoint-fromPoint]
		
		Yorig= self.knn_orig_y[0]
		Yfinal=  self.knn_final_y[toPoint-fromPoint]
		#print "Example "+str(Xorig[0])+" "+str(Xfinal[0])	
		#print "len="+str(len(Xorig))+" "+str(len(Xfinal))
		#print "typ="+str(type(Xorig[0]))+" "+str(type(Xfinal[0]))
		#print "typ="+str(type(Xorig))+" "+str(type(Xfinal))
		neigh_x.fit(Xorig, Xfinal)
		neigh_y.fit(Yorig, Yfinal)
		#print len(self.lines)
#		print "XNeigh"+str(
		predX=neigh_x.predict(self.norm_lines[fromPoint-1])[0]
		predY=neigh_y.predict(self.norm_lines[fromPoint-1])[0]
		toRet=self.denorm((predX,predY))#self.norm_lines[toPoint])
		print str(self.lines[fromPoint])+" "+str(self.norm_lines[fromPoint][2])+","+str(self.norm_lines[fromPoint][3])+"->"+str(toRet)+" After "+str(toPoint-fromPoint)+"steps"
		return toRet

	def denorm(self, p):
		newx=p[0]*self.dx+self.minX
		newy=p[1]*self.dy+self.minY
		return (newx, newy)

	def read(self,filename):
		f = open(filename)
		self.lines=[line.strip().replace('[','').replace(',','').replace(']','').split() for line in f.readlines()]
		for i in range (len(self.lines)):
			self.lines[i][0]=int(self.lines[i][0])
			self.lines[i][1]=int(self.lines[i][1])
		f.close()
		self.normalize()
		self.process()
	
	def process(self):
		import numpy
		if self.allow_knn and len(self.knn_orig_x)==0:
			for i in range(64):
				#self.knn_orig_x.append( numpy.array(self.lines)[0:len(self.lines)-64,0:1]  )#.tolist())
 				#self.knn_orig_y.append( numpy.array(self.lines)[0:len(self.lines)-64,1:2]  )#.tolist())
				#self.knn_final_x.append(numpy.array(self.lines)[i:len(self.lines)-64+i,0])#.tolist())
				#self.knn_final_y.append(numpy.array(self.lines)[i:len(self.lines)-64+i,1])#.tolist())
				
				self.knn_orig_x.append( numpy.array(self.norm_lines)[0:len(self.norm_lines)-64,0:4]  )#.tolist())
 				self.knn_orig_y.append( numpy.array(self.norm_lines)[0:len(self.norm_lines)-64,0:4]  )#.tolist())
				self.knn_final_x.append(numpy.array(self.norm_lines)[i:len(self.norm_lines)-64+i,0])#.tolist())
				self.knn_final_y.append(numpy.array(self.norm_lines)[i:len(self.norm_lines)-64+i,1])#.tolist())
				self.weight_call=Weight
			#	//self.knn_orig_x[i]=self.norm_lines[0:len(self.norm_lines)-i][0]
			#	//self.knn_orig_y[i]=self.norm_lines[0:len(self.norm_lines)-i][1]
			#	//self.knn_final_x[i]=self.norm_lines[i:len(self.norm_lines)][0]
			#	//self.knn_final_y[i]=self.norm_lines[i:len(self.norm_lines)][1]

	def normalize(self):
		maxX=-1
		self.minX=100000000
		maxY=-1
		self.minY=100000000
		for i in range (0,len(self.lines)):
			if(self.lines[i][0] == "-1" or self.lines[i][1]== "-1"):
				continue
			maxX=max(float(self.lines[i][0]),maxX)
			maxY=max(float(self.lines[i][1]),maxY)
			self.minX=min(float(self.lines[i][0]),self.minX)
			self.minY=min(float(self.lines[i][1]),self.minY)
		self.dx=maxX-self.minX
		self.dy=maxY-self.minY
		for i in range(0,len(self.lines)):
			if(self.lines[i][0] == "-1" or self.lines[i][1]== "-1"):
				self.norm_lines.append([-1,-1,-1,-1])
			else:
				toAdd=[((float(self.lines[i][0])-self.minX)/self.dx),((float(self.lines[i][1])-self.minY)/self.dy),-1.,-1.]
				#If there is a previous point, calculate the angle and speed
				if i>0 and self.lines[i-1][0]!="-1":
					toAdd[2]=math.sqrt((toAdd[0]-self.norm_lines[-1][0])**2+(toAdd[1]-self.norm_lines[-1][1])**2)
					toAdd[3]=math.atan2(-1*(toAdd[1]-self.norm_lines[-1][1]),(toAdd[0]-self.norm_lines[-1][0]))

				self.norm_lines.append(toAdd)
		del self.norm_lines[0]

class Predictor2:
	"""A class for predicting robot positions based on training data."""

	def __init__(self,noise_parameter=0):
		self.lines=[[]]
		self.noise=noise_parameter

	def predict(self,fromPoint, toPoint):
		"""Predict the datapoint at index 'toPoint'"""
		x=self.lines[toPoint][0]+random.gauss(0,self.noise*abs(self.lines[toPoint][0]-self.lines[fromPoint][0]))
		y=self.lines[toPoint][1]+random.gauss(0,self.noise*abs(self.lines[toPoint][1]-self.lines[fromPoint][1]))
		return [x,y]

	def read(self,filename):
		f = open(filename)
		self.lines=[[float(d) for d in line.strip().replace('[','').replace(',','').replace(']','').split()] for line in f.readlines()]
		f.close()

	def process(self):
		"""Prepare the data for use.

		This involves:
		- Finding the min and max X and Y values in the data
		- Filtering out stray datapoints
		- Annotating each datapoint with speed and angle
		"""

		maxX=-1
		self.minX=100000000
		maxY=-1
		self.minY=100000000

		MAX_DELTA = 40	# Delta larger than this for consecutive points implies a bad datapoint
		bad_lines = 0
		for i in range(len(self.lines)):
			# First we check for crazy datapoints; there's at least one in the training data.
			# If we find one, convert it to [-1, -1]
			if i > 0 and self.lines[i][0] != -1:
				if abs(last_good_point[0] - self.lines[i][0]) > MAX_DELTA * (bad_lines+1) or abs(last_good_point[1] - self.lines[i][1]) > MAX_DELTA * (bad_lines+1):
					print 'Rejecting datapoint [%d, %d]' % (self.lines[i][0], self.lines[i][1])
					self.lines[i][0] = -1
					self.lines[i][1] = -1

			# Skip bad lines, but remember how many in a row we have seen:
			if(self.lines[i][0] == -1 or self.lines[i][1]== -1):
				bad_lines += 1
				continue

			bad_lines = 0
			last_good_point = self.lines[i]
			maxX=max(float(self.lines[i][0]),maxX)
			maxY=max(float(self.lines[i][1]),maxY)
			self.minX=min(float(self.lines[i][0]),self.minX)
			self.minY=min(float(self.lines[i][1]),self.minY)
		self.dx=maxX-self.minX
		self.dy=maxY-self.minY
		for i in range(len(self.lines)):
			if(self.lines[i][0] == -1 or self.lines[i][1]== -1):
				self.lines[i].append(-1.0)
				self.lines[i].append(-1.0)
			else:
				#If there is a previous point, calculate the angle and speed
				if i>0 and self.lines[i-1][0] != -1:
					self.lines[i].append(math.sqrt((self.lines[i][0]-self.lines[i-1][0])**2+(self.lines[i][1]-self.lines[i-1][1])**2))
					self.lines[i].append(math.atan2((self.lines[i][1]-self.lines[i-1][1]),((self.lines[i][0]-self.lines[i-1][0]))))

class Predictor_KNN:
	lines=[[]]
	norm_lines=[[]]
	def read(self,filename):
		f = open(filename)
		self.lines=[line.strip().replace('[','').replace(',','').replace(']','').split() for line in f.readlines()]
		f.close()
		self.normalize()

	def normalize(self):
		maxX=-1
		self.minX=100000000
		maxY=-1
		self.minY=100000000
		for i in range (0,len(self.lines)):
			if(self.lines[i][0] == "-1" or self.lines[i][1]== "-1"):
				continue
			maxX=max(float(self.lines[i][0]),maxX)
			maxY=max(float(self.lines[i][1]),maxY)
			self.minX=min(float(self.lines[i][0]),self.minX)
			self.minY=min(float(self.lines[i][1]),self.minY)
		self.dx=maxX-self.minX
		self.dy=maxY-self.minY
		for i in range(0,len(self.lines)):
			if(self.lines[i][0] == "-1" or self.lines[i][1]== "-1"):
				self.norm_lines.append([-1,-1,-1,-1])
			else:
				toAdd=[((float(self.lines[i][0])-self.minX)/self.dx),((float(self.lines[i][1])-self.minY)/self.dy),-1.,-1.]
				#If there is a previous point, calculate the angle and speed
				if i>0 and self.lines[i-1][0]!="-1":
					toAdd[2]=math.sqrt((toAdd[0]-self.norm_lines[-1][0])**2+(toAdd[1]-self.norm_lines[-1][1])**2)
					toAdd[3]=math.atan2(-1*(toAdd[1]-self.norm_lines[-1][1]),(toAdd[0]-self.norm_lines[-1][0]))

				self.norm_lines.append(toAdd)
		del self.norm_lines[0]
