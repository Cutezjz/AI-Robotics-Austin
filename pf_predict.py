#!/usr/bin/python
import math
import random
import robot
import visualize


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

	def learn(self):
		PARTICLE_COUNT = 10
		PARTICLE_REMOVAL_FRACTION = 0.1
		START_TURNING_NOISE = 0.1
		TURNING_NOISE = 0.0
		DISTANCE_NOISE = 0.0
		MEASUREMENT_NOISE = 0.0

		# First, find reasonable initial settings for the first robots:
		pt = 0
		self.robot_data = []
		while len(self.lines[pt]) < 6 or not self.lines[pt][2] or not self.lines[pt][4] or self.lines[pt][5]:
			self.robot_data.append([-1.0, -1.0, 0.0, 0.0])
			pt += 1
		init_x, init_y, init_speed, init_heading, init_turn_angle, init_collision = self.lines[pt]
		print "initial speed = %.3f, angle = %.3f" % (init_speed, init_turn_angle)

		# Create the initial particle fleet:
		particles = []
		for i in range(PARTICLE_COUNT):
			noisy_turn_angle = random.gauss(init_turn_angle, START_TURNING_NOISE)
			r = robot.robot(init_x, init_y, init_heading, noisy_turn_angle, init_speed)
			r.set_noise(TURNING_NOISE, DISTANCE_NOISE, MEASUREMENT_NOISE)
			particles.append(r)
		
		# Begin moving particles and learning:
		while pt < len(self.lines):
			# Move particles
			for i in range(PARTICLE_COUNT):
				particles[i].move_in_circle()
				
			# Filter particles and create new ones to replace those removed
			# TODO: this properly
			if len(self.lines) >= 5 and self.lines[pt][0] != -1.0 and self.lines[pt][4]:
				init_x, init_y, init_speed, init_heading, init_turn_angle, init_collision = self.lines[pt]
				r = robot.robot(init_x, init_y, init_heading, init_turn_angle, init_speed)
				r.set_noise(TURNING_NOISE, DISTANCE_NOISE, MEASUREMENT_NOISE)
				particles = particles[1:] + [r]
			
			# Calculate average values for all particles
			avg_x = sum([r.x for r in particles]) / PARTICLE_COUNT
			avg_y = sum([r.y for r in particles]) / PARTICLE_COUNT
			avg_speed = sum([r.distance for r in particles]) / PARTICLE_COUNT
			avg_heading = sum([r.heading for r in particles]) / PARTICLE_COUNT
			self.robot_data.append([avg_x, avg_y, avg_speed, avg_heading])
			pt += 1
			
		
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

		last_good_point = [0.0, 0.0]		
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
		COLLISION_REGION = 30
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



# Run the code below only if this module is being directly executed
if __name__ == "__main__":
	p=PfPredictor()
	p.read("training_video1-centroid_data")
	p.process()
	print "read %d lines, saw %d collisions" % (len(p.lines), len(p.collision_indices))
	print "extent is (%d, %d) to (%d, %d)" % (p.minX, p.minY, p.maxX, p.maxY)
	p.learn()
	
	vis = visualize.Visualizer(p)
	vis.visualize(512, 16, 512, True, True)

