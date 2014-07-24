#!/usr/bin/python
import math
import random
import robot



def angle_trunc(a):
    """This maps all angles to a domain of [-pi, pi]"""
    while a < 0.0:
        a += math.pi * 2
    return ((a + math.pi) % (math.pi * 2)) - math.pi


class PfPredictor:
	"""A class for predicting robot positions based on a particle filter."""

	def __init__(self,noise_parameter=0):
		self.lines=[[]]
		self.noise=noise_parameter

	def within_collision_boundary(self, x, y, boundary):
		return self.minX + boundary > x or self.maxX - boundary < x or self.minY + boundary > y or self.maxY - boundary < y
	
	def predict(self, fromPoint, toPoint):
		"""Predict the datapoint at index 'toPoint'"""
		# TODO
		if toPoint >= len(self.lines):
			x = 0.0
			y = 0.0
		else:
			x=self.lines[toPoint][0] + 5.0
			y=self.lines[toPoint][1] - 5.0
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

		self.maxX=-1
		self.minX=100000000
		self.maxY=-1
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
			self.maxX=max(float(self.lines[i][0]),self.maxX)
			self.maxY=max(float(self.lines[i][1]),self.maxY)
			self.minX=min(float(self.lines[i][0]),self.minX)
			self.minY=min(float(self.lines[i][1]),self.minY)
			
		self.dx=self.maxX-self.minX
		self.dy=self.maxY-self.minY
		
		prev_heading = None
		MAX_TURN_ANGLE = 0.5	# Turn angle larger than this implies a collision
		COLLISION_REGION = 25
		self.collision_indices = []
		
		for i in range(len(self.lines)):
			# If previous and current points are valid, append the speed and heading,
			# and turn angle and collision flag, if possible
			# Any values that cannot be determined will be None
			if i>0 and self.lines[i-1][0] != -1 and self.lines[i][0] != -1:
				x_prev = self.lines[i-1][0]
				y_prev = self.lines[i-1][1]
				x_curr = self.lines[i][0]
				y_curr = self.lines[i][1]
				speed = math.sqrt((x_curr - x_prev)**2 + (y_curr - y_prev)**2)
				heading = math.atan2((y_curr - y_prev), (x_curr - x_prev))
				self.lines[i].append(speed)
				self.lines[i].append(heading)
				
				if prev_heading:
					turn_angle = angle_trunc(heading - prev_heading)
					self.lines[i].append(turn_angle)
					if abs(turn_angle) > MAX_TURN_ANGLE and self.within_collision_boundary(x_curr, y_curr, COLLISION_REGION):
						# We assume this is a collision...
						self.lines[i].append(True)
						self.collision_indices.append(i)
						if i < 1000:
							print "%5d: prev = %.3f, curr = %.3f (%.3f,%.3f to %.3f,%.3f), turn = %.3f, collision = %d" % (i, prev_heading, heading, x_prev, y_prev, x_curr, y_curr, turn_angle, self.lines[i][5])
					else:
						self.lines[i].append(False)
				else:
					self.lines[i] += [None, None]
				prev_heading = heading
			else:
				prev_heading = None
				self.lines[i] += [None, None, None, None]



p=PfPredictor()
p.read("training_video1-centroid_data")
p.process()
print "read %d lines, saw %d collisions" % (len(p.lines), len(p.collision_indices))
print "extent is (%d, %d) to (%d, %d)" % (p.minX, p.minY, p.maxX, p.maxY)

