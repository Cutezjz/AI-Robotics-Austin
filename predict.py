#!/usr/bin/python
import math
import random
#import visualize

class Predictor:
    """
    The core predictor class

    Includes utility functions like reading files and normalizing datasets, as well as the main KNN predictor
    The KNN predictor shall:
    Read in a training file
    Process that training file:
        Average groups of missing points with the points before and after the missing groups
        Convert the X and Y coordinates to fraction of box width and height respectively
        Calculate the velocity and angle from each point to the point before it
        Create 64 vectors of points, knn_final_x and knn_final_y, with knn_final_x[a][b] representing the change in the normalized X coordinate of the robot "a" time steps after "b"
        Set knn_orig to be the normalized points from the training set, less the final 64 points
    Read a test file
    Normalize the test file as above
    When predict_KNN is called, fit a KNN predictor from knn_orig to knn_final_x and knn_final_y, using the 7 nearest neighbors
    Estimate the normalized Dx and Dy from those 7 nearest neighbors
    Return the denormalized current point plus offset Dx and Dy
    """
    lines=[]
    test_set_lines=[]
    norm_lines=[]
    norm_test_lines=[]
    knn_orig=[]
    knn_final_x=[]
    knn_final_y=[]
    allow_knn=True
    def predict(self,fromPoint, toPoint):
        """Return a perfect prediction 

        This function is useful for testing purposes, but will fail if asked to predict data that hasn't be presented.
        """
        return self.test_set_lines[toPoint]

    def predict_KNN(self,fromPoint, toPoint):
        """Return a prediction based on the dx and dy of the 7 most similar points to fromPoint"""
        from sklearn import preprocessing
        from sklearn.neighbors import KNeighborsRegressor
        
        neigh_x = KNeighborsRegressor(n_neighbors=7,algorithm='kd_tree')
        neigh_y = KNeighborsRegressor(n_neighbors=7,algorithm='kd_tree')
        Xorig=  self.knn_orig
        Xfinal=  self.knn_final_x[toPoint-fromPoint]
        Yorig= self.knn_orig
        Yfinal=  self.knn_final_y[toPoint-fromPoint]
        
        neigh_x.fit(Xorig, Xfinal)
        neigh_y.fit(Yorig, Yfinal)
        predX=neigh_x.predict(self.norm_test_lines[fromPoint-1])[0]
        predY=neigh_y.predict(self.norm_test_lines[fromPoint-1])[0]
        toRet=self.denorm((self.norm_test_lines[fromPoint-1][0]+predX,self.norm_test_lines[fromPoint-1][1]+predY))
        return toRet

    def denorm(self, p):
        """Convert a point from a normalized point to a normal point, using the instances normalization parameters"""
        newx=p[0]*self.dx+self.minX
        newy=p[1]*self.dy+self.minY
        return (newx, newy)
    

    def read_test_set(self,filename):
        """Read and normalize the test data from file filename"""
        f = open(filename)
        self.test_set_lines=[[float(d) for d in line.strip().replace('[','').replace(',','').replace(']','').split()] for line in f.readlines()]
        f.close()
        self.norm_test_lines=self.normalize(self.test_set_lines)

    def read(self,filename):
        """Read and normalize the training data from file filename"""
        f = open(filename)
        self.lines=[line.strip().replace('[','').replace(',','').replace(']','').split() for line in f.readlines()]
        for i in range (len(self.lines)):
            self.lines[i][0]=int(self.lines[i][0])
            self.lines[i][1]=int(self.lines[i][1])
        f.close()
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
        self.norm_lines=self.normalize(self.lines)
        self.process()
    
    def process(self):
        """If KNN is enabled for this predictor, set up the 64 vectors associated with the coordinates up to 64 time steps from each known coordinate"""
        import numpy
        print "Process"
        if self.allow_knn and len(self.knn_orig)==0:
            self.knn_orig= numpy.array(self.norm_lines)[0:len(self.norm_lines)-64,0:4]
            for i in range(64):
                self.knn_final_x.append(numpy.array(self.norm_lines)[i:len(self.norm_lines)-64+i,0]-numpy.array(self.norm_lines)[0:len(self.norm_lines)-64,0])
                self.knn_final_y.append(numpy.array(self.norm_lines)[i:len(self.norm_lines)-64+i,1]-numpy.array(self.norm_lines)[0:len(self.norm_lines)-64,1])
    
    def avg_missing_points(self,lines):
        """If a point or group of points is missing, assume those missing points were in between the known points before and after the missing points"""
        for i in range(len(lines)):
            if lines[i][0]==-1 or lines[i][1]==-1:
                count=0
                while(lines[i+count][0]==-1 or lines[i+count][1]==-1):
                    count=count+1
                dx=lines[i+count][0]-lines[i-1][0]
                dy=lines[i+count][1]-lines[i-1][1]
                for j in range (count):
                    lines[i+j][0]=lines[i-1][0]+dx*(0.0+j)/count
                    lines[i+j][1]=lines[i-1][1]+dy*(0.0+j)/count
        return lines
                


    def normalize(self,lines):
        """Compute the min and max X and Y coordinates, and normalize all points to the range ([0,1],[0,1]) where 0 represents min and 1 represents max

        Then compute the angles and velocity associated with each point to the point before it"""
        norm_lines=[]
        if self.allow_knn and len(self.knn_orig)==0:
            lines=self.avg_missing_points(lines)
        for i in range(0,len(lines)):
            if(lines[i][0] == "-1" or lines[i][1]== "-1"):
                norm_lines.append([-1,-1,-1,-1])
            else:
                toAdd=[((float(lines[i][0])-self.minX)/self.dx),((float(lines[i][1])-self.minY)/self.dy),-1.,-1.]
                #If there is a previous point, calculate the angle and speed
                if i>0 and lines[i-1][0]!="-1":
                    toAdd[2]=math.sqrt((toAdd[0]-norm_lines[-1][0])**2+(toAdd[1]-norm_lines[-1][1])**2)
                    toAdd[3]=math.atan2(-1*(toAdd[1]-norm_lines[-1][1]),(toAdd[0]-norm_lines[-1][0]))

                norm_lines.append(toAdd)
        return norm_lines

class Predictor_KNN(Predictor):
    """A utility class which inherits a complete KNN predictor from Predictor

    Overrides the predict function with the Predictor.predict_knn function
    """
    def predict(self, fromPoint,toPoint):
        """Call the Predictor.predict_knn function"""
        return self.predict_KNN(fromPoint, toPoint)

if __name__ == "__main__":
    p = Predictor_KNN()
    p.read("testing_video-centroid_data")

    start_index = 1378

    vis = visualize.Visualizer(p)
    vis.visualize(start_index, 63, 64, True, False)
