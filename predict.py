#!/usr/bin/python
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
				self.norm_lines.append([-1,-1])
			else:
				self.norm_lines.append([((float(self.lines[i][0])-self.minX)/self.dx),((float(self.lines[i][1])-self.minY)/self.dy)])

