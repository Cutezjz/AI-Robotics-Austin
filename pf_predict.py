#!/usr/bin/python
import math
import random
from robot import *
import visualize


def angle_trunc(a):
	"""This maps all angles to a domain of [-pi, pi]"""
	while a < 0.0:
		a += math.pi * 2
	return ((a + math.pi) % (math.pi * 2)) - math.pi

def Gaussian2d(mu, sigma, x):
    """calculates the probability of x for 2D (but circular) Gaussian with mean mu and var. sigma"""
    dist = sqrt((mu[0] - x[0]) ** 2 + (mu[1] - x[1]) ** 2)
    result = exp(- (dist ** 2) / (sigma ** 2) / 2.0) / sqrt(2.0 * pi * (sigma ** 2))
    # print 'Gaussian2d: dist = %.5f, sigma = %.5f, result = %.5f' % (dist, sigma, result)
    return result

def measurement_prob(robot, measurement, sigma):
    # calculates how likely a measurement should be
    prob = Gaussian2d([robot.x, robot.y], sigma, measurement)
    return prob

def copy_robot(src):
    result = robot(src.x, src.y, src.heading, src.turning, src.distance)
    result.set_noise(src.turning_noise, src.distance_noise, src.measurement_noise)
    return result

def resample(robots, measurement, num_results, sigma):
    num_robots = len(robots)
    w = []
    w_max = 0.
    for i in range(num_robots):
        w.append(measurement_prob(robots[i], measurement, sigma))
        w_max = max(w_max, w[i])
    # print "w = ", w, ", w_max = ", w_max

    result = []
    beta = 0.
    index = int(random.random() * num_robots)
    for i in range(num_results):
        beta += 2 * w_max * random.random()
        while beta > w[index]:
            beta -= w[index];
            index = (index + 1) % num_robots
        result.append(copy_robot(robots[index]))
        # print 'selecting robot at (%.5f, %.5f)' % (robots[index].x, robots[index].y)
    return result

def create_particles(count, loc, heading, turning, distance, loc_sigma, heading_sigma, turning_sigma, distance_sigma):

    TURNING_NOISE = 0.0
    SPEED_NOISE_FACTOR = 0.0
    MEASUREMENT_NOISE = 0.0

    result = []

    for i in range(count):
        x = random.gauss(loc[0], loc_sigma)
        y = random.gauss(loc[1], loc_sigma)
        h = random.gauss(heading, heading_sigma)
        t = random.gauss(turning, turning_sigma)
        d = random.gauss(distance, distance_sigma)
        p = robot(x, y, h, t, d)
        p.set_noise(TURNING_NOISE, distance * SPEED_NOISE_FACTOR, MEASUREMENT_NOISE)
        result.append(p)
        # print 'created robot: x=%.5f, y=%.5f, heading=%.5f, turning=%.5f, distance=%.5f' % (x, y, h, t, d)

    return result

def average_robot_location(robots):
    x_avg = 0.0 if len(robots)==0 else sum([r.x for r in robots]) / len(robots)
    y_avg = 0.0 if len(robots)==0 else sum([r.y for r in robots]) / len(robots)
    return [x_avg, y_avg]



class PfPredictor:
	"""A class for predicting robot positions based on a particle filter."""

	def __init__(self,noise_parameter=0):
		self.lines=[[]]
		self.noise=noise_parameter

	def within_collision_boundary(self, x, y, boundary):
		return self.minX + boundary > x or self.maxX - boundary < x or self.minY + boundary > y or self.maxY - boundary < y
	
	def get_robot_averages(self):
		"""Return averages of [x, y, speed, heading] across all robots"""
		count = len(self.particles)
		avg_x = sum([r.x for r in self.particles]) / count
		avg_y = sum([r.y for r in self.particles]) / count
		avg_speed = sum([r.distance for r in self.particles]) / count
		avg_heading = sum([r.heading for r in self.particles]) / count
		avg_turning = sum([r.turning for r in self.particles]) / count
		return [avg_x, avg_y, avg_speed, avg_heading, avg_turning]
		
	def predict(self, fromPoint, toPoint):
		"""Predict the datapoint at index 'toPoint'"""
		# NOTE: ignoring parameters and just predicting the next point
		for r in self.particles:
			r.move_in_circle()
		x, y, speed, heading, turning = self.get_robot_averages()
		print "predict: (%.1f, %.1f), speed=%.3f, heading=%.3f, turn_angle=%.3f" % (x, y, speed, heading, turning)
		return [x,y]

	def learn(self, num_points=None):
		PARTICLE_COUNT = 50
		PARTICLE_REMOVAL_FRACTION = 0.1
		RESAMPLE_SIGMA = 1.0
		START_LOCATION_NOISE = 0.5
		START_HEADING_NOISE = 0.02
		START_TURNING_NOISE = 0.02
		START_SPEED_NOISE = 0.05

		# First, find reasonable initial settings for the first robots:
		pt = 0
		self.robot_data = []
		while len(self.lines[pt]) < 6 or not self.lines[pt][2] or not self.lines[pt][4] or self.lines[pt][5]:
			self.robot_data.append([-1.0, -1.0, 0.0, 0.0])
			pt += 1
		x_i, y_i, s_i, h_i, ta_i, c_i = self.lines[pt]
		print "initial speed = %.3f, angle = %.3f" % (s_i, ta_i)

		# Create the initial particle fleet:
		self.particles = create_particles(PARTICLE_COUNT, [x_i, y_i], h_i, ta_i, s_i, START_LOCATION_NOISE, START_HEADING_NOISE, START_TURNING_NOISE, START_SPEED_NOISE)

		new_particle_count = int(PARTICLE_COUNT * PARTICLE_REMOVAL_FRACTION)
		keep_particle_count = PARTICLE_COUNT - new_particle_count

		if num_points == None:
			num_points = len(self.lines)
		num_points = min(num_points, len(self.lines))

		cum_speed = None	# cumulative speed estimate
		cum_turn_angle = None

		# Begin moving particles and learning:
		while pt < num_points:
			# Move particles
			for i in range(PARTICLE_COUNT):
				self.particles[i].move_in_circle()
				
			# Filter particles and create new ones to replace those removed
			# We resample and create new particles only if there's enough valid data at this point
			if len(self.lines) >= 6 and self.lines[pt][0] != -1.0 and self.lines[pt][4]:
				x_i, y_i, s_i, h_i, ta_i, c_i = self.lines[pt]
				
				# First, we update our cumulative speed and turn angle estimates:
				cum_speed = s_i if cum_speed == None else cum_speed * 0.9 + s_i * 0.1
				if cum_turn_angle == None:
					cum_turn_angle = ta_i
				elif not c_i:
					cum_turn_angle = cum_turn_angle * 0.8 + ta_i * 0.2
				
				# Now update the particle fleet:
				resampled_particles = resample(self.particles, [x_i, y_i], keep_particle_count, RESAMPLE_SIGMA)
				new_particles = create_particles(new_particle_count, [x_i, y_i], h_i, cum_turn_angle, cum_speed, START_LOCATION_NOISE, START_HEADING_NOISE, START_TURNING_NOISE, START_SPEED_NOISE)
				self.particles = resampled_particles + new_particles
			
			# Calculate average values for all particles
			robot_averages = self.get_robot_averages()
			self.robot_data.append(robot_averages)
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
	# p.read("testing_video-centroid_data")
	p.process()
	print "read %d lines, saw %d collisions" % (len(p.lines), len(p.collision_indices))
	print "extent is (%d, %d) to (%d, %d)" % (p.minX, p.minY, p.maxX, p.maxY)
	
	start_index = 440
	# start_index = 1378
	p.learn(start_index)
	
	vis = visualize.Visualizer(p)
	vis.visualize(start_index, 16, 64, True, True)

