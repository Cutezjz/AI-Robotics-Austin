import math
import random
import robot

# Going to analyze all the points in the training video and look for collisions and determine the angle it hits the wall
# and the angle that it leaves the wall

# Need to consider the -1,-1 points, bad data points, and also when it gets stuck in a corner.

# I think I maybe able to predict future collisions based on its speed and how close it is to a wall/corner


def angle_trunc(a):
    """This maps all angles to a domain of [-pi, pi]"""
    while a < 0.0:
        a += math.pi * 2
    return ((a + math.pi) % (math.pi * 2)) - math.pi


class Analysis:

    def __init__(self):
        self.lines=[[]]
    
    def read(self,filename):
        f = open(filename)
        self.lines=[[float(d) for d in line.strip().replace('[','').replace(',','').replace(']','').split()] for line in f.readlines()]
        f.close()

    def sample(self, testlines = 0):
        # We want 1378 lines as a testcase
        s = [[]]
        legal_num = len(self.lines) - 1378 - 63
        self.index = random.randrange(1,legal_num)
        end_num = self.index + testlines
        s = self.lines[self.index:end_num]
        return s


    def boundingBox(self):
        # Find the bounding x and y points of our box
        self.maxX=-1
        self.minX = 10000000
        self.maxY = -1
        self.minY = 10000000

        MAX_DELTA = 40
        bad_lines = 0
        
        for i in range(len(self.lines)):
            # First we check for crazy datapoints; there's at least one in the training data.
	    # If we find one, convert it to [-1, -1]
            if i > 0 and self.lines[i][0] != -1:
                if abs(last_good_point[0] - self.lines[i][0]) > MAX_DELTA * (bad_lines+1) or abs(last_good_point[1] - self.lines[i][1]) > MAX_DELTA * (bad_lines+1):
                    print('Rejecting datapoint ', self.lines[i][0], self.lines[i][1])
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
        



    def analyze(self,testlines = 0):
        # We want the next 63 points after the testcase
        self.start = self.index
        self.end = self.start + testlines
        points = [[]]
        points = self.lines[self.start:self.end]

        angle = []
        speed = []
        collision_angles = []
        bounced_angle = []
        
        # Maybe I should save the two points with its calculated angle
        # I need to know where a collision happens so I can get the before and after angle
        # For now, I am going to assume the same angle without a turning angle and if the
        # extrapolated point goes past the boundary then I assume a collision and the next
        # point is the point after collision and I get the angle difference from it. 
        for i in range(2):
            # Find the angle between points
            # Adjust the angle based on its quadrant
            # Looking for movement toward 1st Quadrant
            y = points[i][1]
            x = points[i][0]
            y_next = points[i+1][1]
            x_next = points[i+1][0]

            # Let's determine if we are close to a wall
            heading = ['Quadrant1', 'Quadrant2', 'Quadrant3', 'Quadrant4']
            
            if x_next > x and y_next > y and x_next > 0 and x > 0:
                angle.append(math.atan2(y_next - y, x_next - x))
                speed.append(math.sqrt((x_next - x)**2 + (y_next + y)**2))
                direction = heading[0]

            # Looking for movement toward 2nd Quadrant
            elif x_next < x and y_next > y and x_next > 0 and x > 0:
                angle.append(math.atan2(y_next - y, x_next - x))
                speed.append(math.sqrt((x_next - x)**2 + (y_next + y)**2))
                direction = heading[1]

            # Looking for movement toward 3rd Quadrant
            elif x_next < x and y_next < y and x_next > 0 and x > 0:
                angle.append(math.atan2(y_next - y, x_next - x))
                speed.append(math.sqrt((x_next - x)**2 + (y_next + y)**2))
                direction = heading[2]

            # Looking for movement toward 4th Quadrant
            elif x_next > x and y_next < y and x_next > 0 and x > 0:
                angle.append(math.atan2(y_next - y, x_next - x))
                speed.append(math.sqrt((x_next - x)**2 + (y_next + y)**2))
                direction = heading[3]

            previous_direction = direction
            


        for i in range(2,len(points)-2):
            # Find the angle between points
            # Adjust the angle based on its quadrant
            # Looking for movement toward 1st Quadrant
            y = points[i][1]
            x = points[i][0]
            y_next = points[i+1][1]
            x_next = points[i+1][0]

            # Let's determine if we are close to a wall
            heading = ['Quadrant1', 'Quadrant2', 'Quadrant3', 'Quadrant4']
            
            if x_next > x and y_next > y and x_next > 0 and x > 0:
                angle.append(math.atan2(y_next - y, x_next - x))
                speed.append(math.sqrt((x_next - x)**2 + (y_next + y)**2))
                direction = heading[0]

            # Looking for movement toward 2nd Quadrant
            elif x_next < x and y_next > y and x_next > 0 and x > 0:
                angle.append(math.atan2(y_next - y, x_next - x))
                speed.append(math.sqrt((x_next - x)**2 + (y_next + y)**2))
                direction = heading[1]

            # Looking for movement toward 3rd Quadrant
            elif x_next < x and y_next < y and x_next > 0 and x > 0:
                angle.append(math.atan2(y_next - y, x_next - x))
                speed.append(math.sqrt((x_next - x)**2 + (y_next + y)**2))
                direction = heading[2]

            # Looking for movement toward 4th Quadrant
            elif x_next > x and y_next < y and x_next > 0 and x > 0:
                angle.append(math.atan2(y_next - y, x_next - x))
                speed.append(math.sqrt((x_next - x)**2 + (y_next + y)**2))
                direction = heading[3]

            if previous_direction == direction:
                #print('No direction change')
                previous_direction = direction
            else:
                print('Direction changed from ',previous_direction,' to ',direction)
                previous_direction = direction
                print(points[i-1][0],points[i-1][1], '  ',points[i][0],points[i][1], '  ', points[i+1][0], points[i+1][1])
                # Let's check to see if it is close to the bounding box
                if x - 5 < self.minX or x + 5 > self.maxX or y - 5 < self.minY or y + 5 > self.maxY:
                    x_next_next = points[i+2][0]
                    y_next_next = points[i+2][1]
                    # Let's calculate the new angle
                    new_angle = math.atan2(y_next_next - y_next, x_next_next - x_next)
                    new_angle = angle_trunc(new_angle)
                    # Let's put the before and after angles together
                    print('index = ', i)
                    #print('angle[i] = ', angle[i],' new_angle = ', new_angle)
                    print('length of angle = ', len(angle))
                    print('new_angle = ', new_angle)
                    collision_angles.append(angle[-1])
                    bounced_angle.append(new_angle)

            

            
        for j in range(len(angle)):
            angle[j] = angle_trunc(angle[j])

        return angle,collision_angles


testlines = 400
t = Analysis()
t.read('training_video1-centroid_data')
s = t.sample(testlines)
#print('s = ', s)
#print('angles = ', angles)
t.boundingBox()
print('Bounding Box of course is :\n'
      'minX = ', t.minX, '\n'
      'maxX = ', t.maxX, '\n'
      'minY = ', t.minY, '\n'
      'maxY = ', t.maxY, '\n')
angles,collisions = t.analyze(testlines)
print('Collision angles = ', collisions)
