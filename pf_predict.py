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
    """Return the probability of x for a 2D (but circular) Gaussian with mean mu and var. sigma"""
    dist = sqrt((mu[0] - x[0]) ** 2 + (mu[1] - x[1]) ** 2)
    result = exp(- (dist ** 2) / (sigma ** 2) / 2.0) / sqrt(2.0 * pi * (sigma ** 2))
    # print 'Gaussian2d: dist = %.5f, sigma = %.5f, result = %.5f' % (dist, sigma, result)
    return result

def measurement_prob(robot, measurement, sigma):
    """Returns the likelihood of a measurement, assuming a circular Gaussian distribution."""
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

    result = []
    beta = 0.
    index = int(random.random() * num_robots)
    for i in range(num_results):
        beta += 2 * w_max * random.random()
        while beta > w[index]:
            beta -= w[index];
            index = (index + 1) % num_robots
        result.append(copy_robot(robots[index]))
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



class PfPredictor:
	"""A class for predicting robot positions based on a particle filter."""

	HEXBUG_LENGTH = 36		# Approximate hexbug length (in pixels)
	HEXBUG_WIDTH  = 10		# Approximate hexbug width (in pixels)

	COLLISION_REGION = 2	# Collision detection margin (in pixels)

	# Enumerated values for which wall causes a collision
	WALL_NONE = 0
	WALL_RIGHT = 1
	WALL_TOP = 2
	WALL_LEFT = 3
	WALL_BOTTOM = 4

	COLLISION_HISTORY_STEPS = 7		# Number of steps to play back from history after a collision

	def __init__(self,noise_parameter=0):
		self.lines=[[]]
		self.noise=noise_parameter
		self.steps_to_record = 0
		self.steps_to_playback = 0
		self.collision_database = []

	def get_hexbug_front(self, pos, heading, distance = 0.0):
		"""Return the rough location of the front center of the hexbug.
		
		pos - [x,y] coordinates of the bug's centroid
		heading - bug heading (in radians)
		distance - an additional distance to add (in the direction of 'heading')
		"""

		x_front = pos[0] + ((self.HEXBUG_LENGTH / 2.0) + distance) * cos(heading)
		y_front = pos[1] + ((self.HEXBUG_LENGTH / 2.0) + distance) * sin(heading)
		return [x_front, y_front]

	def find_nearest_collision_sequence(self, entry_angle):
		"""Search the collision database for the nearest entry and return it"""
		nearest_distance = 2.0 * math.pi
		nearest_index = None
		nearest_result = None
		for i in range(len(self.collision_database)):
			entry = self.collision_database[i]
			distance = abs(entry[0] - entry_angle)
			if distance < nearest_distance:
				nearest_result = entry[1]
				nearest_distance = distance
				nearest_index = i
		return nearest_result

	def predict_collision(self, loc, heading, speed, turn_angle):
		"""Will hexbug hit the wall in the NEXT time step?
		
		If so, return [WALL_xxx, near_corner?, entry_angle].
		If not, return [WALL_NONE, False, None]"""

		front_loc = self.get_hexbug_front(loc, heading, speed)
		wall = self.WALL_NONE
		near_corner = False
		entry_angle = None

		if (front_loc[0] + self.COLLISION_REGION >= self.maxX):
			wall = self.WALL_RIGHT
			entry_angle = math.pi / 2.0 + heading
		if (front_loc[1] - self.COLLISION_REGION <= self.minY):
			if wall != self.WALL_NONE:
				near_corner = True
			wall = self.WALL_TOP
			entry_angle = math.pi + heading
		if (front_loc[0] - self.COLLISION_REGION <= self.minX):
			if wall != self.WALL_NONE:
				near_corner = True
			wall = self.WALL_LEFT
			entry_angle = 3.0 * math.pi / 2.0 + heading
		if (front_loc[1] + self.COLLISION_REGION >= self.maxY):
			if wall != self.WALL_NONE:
				near_corner = True
			wall = self.WALL_BOTTOM
			entry_angle = heading

		if entry_angle != None:
			entry_angle = angle_trunc(entry_angle)
			# print "Collision predicted at wall %d: (%.1f, %.1f) hdg %.3f speed %.1f angle %.3f" % (wall, front_loc[0], front_loc[1], heading, speed, entry_angle)

		return [wall, near_corner, entry_angle]

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

		x, y, speed, heading, turning = self.get_robot_averages()

		if self.steps_to_playback > 0:
			heading_delta, playback_speed = self.collision_steps[-self.steps_to_playback]
			new_heading = angle_trunc(heading + heading_delta)
			x_delta = playback_speed * cos(new_heading)
			y_delta = playback_speed * sin(new_heading)
			for r in self.particles:
				r.x += x_delta
				r.y += y_delta
				r.heading = angle_trunc(r.heading + heading_delta)
			self.steps_to_playback -= 1

		else:
			wall, near_corner, entry_angle = self.predict_collision([x,y], heading, speed, turning)
			if wall == self.WALL_NONE:
				# No collision predicted; just move normally
				for r in self.particles:
					r.move_in_circle()
			else:
				# Collision predicted; find replay sequence and begin replay:
				self.collision_steps = self.find_nearest_collision_sequence(entry_angle)
				self.steps_to_playback = len(self.collision_steps)

				# Recursively call this (now in playback mode):
				return self.predict(fromPoint, toPoint)

		x, y, speed, heading, turning = self.get_robot_averages()
		# print "predict: (%.1f, %.1f), speed=%.3f, heading=%.3f, turn_angle=%.3f" % (x, y, speed, heading, turning)
		return [x,y]

	def learn(self, num_points=None):
		PARTICLE_COUNT = 50
		PARTICLE_REMOVAL_FRACTION = 0.1
		RESAMPLE_SIGMA = 1.0
		START_LOCATION_NOISE = 0.5
		START_HEADING_NOISE = 0.02
		START_TURNING_NOISE = 0.01
		START_SPEED_NOISE = 0.05

		# First, find reasonable initial settings for the first robots:
		pt = 0
		self.robot_data = []
		while len(self.lines[pt]) < 6 or not self.lines[pt][2] or not self.lines[pt][4] or self.lines[pt][5]:
			self.robot_data.append([-1.0, -1.0, 0.0, 0.0])
			pt += 1
		x_i, y_i, s_i, h_i, ta_i, c_i = self.lines[pt]
		# print "initial speed = %.3f, angle = %.3f" % (s_i, ta_i)

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
			self.predict(0, 0)
				
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
	def read_test_set(self,filename):
		f = open(filename)
		self.test_set_lines=[[float(d) for d in line.strip().replace('[','').replace(',','').replace(']','').split()] for line in f.readlines()]
		f.close()
		
	def read(self,filename):
		f = open(filename)
		self.lines=[[float(d) for d in line.strip().replace('[','').replace(',','').replace(']','').split()] for line in f.readlines()]
		f.close()

	def process(self, create_collision_database=True):
		"""Prepare the data for use.

		This involves:
		- Finding the min and max X and Y values in the data
		- Filtering out stray datapoints
		- Annotating each datapoint with speed and angle
		- Creating a collision database (if requested)
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
					# print 'Rejecting datapoint [%d, %d]' % (self.lines[i][0], self.lines[i][1])
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
		self.collision_database = []

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
					if self.steps_to_record > 0:
						self.collision_steps.append([turn_angle, speed])
						self.steps_to_record -= 1
						if self.steps_to_record == 0:
							self.collision_database.append([self.collision_entry_angle, self.collision_steps])
							self.collision_entry_angle = None
							self.collision_steps = None
						self.lines[i].append(False)
					else:
						wall, near_corner, entry_angle = self.predict_collision([x_curr, y_curr], heading, speed, turn_angle)
						if wall != self.WALL_NONE:
							# We assume that the next step will be a collision...
							self.lines[i].append(True)
							if create_collision_database and not near_corner:
								self.steps_to_record = self.COLLISION_HISTORY_STEPS
								self.collision_steps = []
								self.collision_entry_angle = entry_angle
						else:
							self.lines[i].append(False)
				else:
					self.lines[i] += [None, None]
				prev_heading = heading
			else:
				prev_heading = None
				self.lines[i] += [None, None, None, None]
				self.steps_to_record = 0	# A [-1, -1] terminates collision recording

		# print "Sorting collision database of %d entries" % (len(self.collision_database))
		sorted_database = sorted(self.collision_database, key=lambda collision: collision[0])
		self.collision_database = sorted_database
		# print "Collision database:"
		# for c in self.collision_database:
		# 	print c

def make_pf_predictor(training_file_name, test_file_name):
	"""Create a PfPredictor that is ready to learn on test file data."""
	p_train = PfPredictor()
	p_train.read(training_file_name)
	p_train.process()

	p_test = PfPredictor()
	p_test.read(test_file_name)
	p_test.process(False)
	p_test.collision_database = p_train.collision_database
	# print "read %d lines, saw %d collisions" % (len(p_test.lines), len(p_test.collision_database))
	# print "extent is (%d, %d) to (%d, %d)" % (p_test.minX, p_test.minY, p_test.maxX, p_test.maxY)

	return p_test

# Run the code below only if this module is being directly executed
if __name__ == "__main__":
	p = make_pf_predictor("training_video1-centroid_data", "testing_video-centroid_data")
	# p = make_pf_predictor("training_video1-centroid_data", "training_video1-centroid_data")

	# start_index = 440
	start_index = 1378
	p.learn(start_index)

	vis = visualize.Visualizer(p)
	vis.visualize(start_index, 63, 64, True, True)
