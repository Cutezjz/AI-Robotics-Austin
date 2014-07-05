#!/usr/bin/python
class Predictor:
	lines=[[]]
	def predict(self,fromPoint, toPoint):
		return self.lines[toPoint]
	def read(self,filename):
		f = open(filename)
		self.lines=[line.strip().replace('[','').replace(',','').replace(']','').split() for line in f.readlines()]
		f.close()




