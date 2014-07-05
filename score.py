#!/usr/bin/python
from predict import Predictor
import math
class Scorer:
	def __init__(self, pred):
		self.p=pred

	#Calculate the average error per point from the initial point on.
	#For each point, sum the error predicting the next 63 points
	def error(self,initial_point):
		sum=0
		count=0
		for i in range(initial_point, len(self.p.lines)-64):
			count+=1
			for j in range(0,64):
				sum+=Scorer.squared_err(p.predict(i,i+j),self.p.lines[i+j])		
		return sum/count

	@staticmethod
	def squared_err(p1,p2):
		return math.sqrt((float(p1[0])-float(p2[0]))**2+(float(p1[1])-float(p2[1]))**2)


p=Predictor()
p.read("training_video1-centroid_data")
s=Scorer(p)
p.normalize()
print p.predict(0,2)
print s.error(0)
print p.lines
print p.norm_lines
