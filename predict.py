#!/usr/bin/python
import math
import random
class Predictor:
	lines=[[]]
	norm_lines=[[]]
	def predict(self,fromPoint, toPoint):
		return self.lines[toPoint]

	def read(self,filename):
		f = open(filename)
		self.lines=[line.strip().replace('[','').replace(',','').replace(']','').split() for line in f.readlines()]
		f.close()
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

