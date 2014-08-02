#!/usr/bin/python
import math
import random
class Weight:
    def __init__(self, d):
        print "Init "+str(d)
        self.d=d
        self.w=[]
        for i in range(len(self.d)):
            if d[0][i]<.001:
                self.w.append(0)
            else:
                self.w.append(1.0/self.d[i])
        print "W="+str(self.w[0])
        #return self.w

    def __call__(self):
        print "Call-W "+str(self.w)
        print "Calling"
        return self.w
        
class Predictor:
    def inverse(d):
        w=[]
        for i in range(len(self.d)):
            if d[0][i]<.001:
                w.append(0)
            else:
                w.append(1.0/self.d[i])
        return w
        
    lines=[[]]
    norm_lines=[[]]
    knn_orig_x=[]
    knn_orig_y=[]
    knn_final_x=[]
    knn_final_y=[]
    allow_knn=True
    def predict(self,fromPoint, toPoint):
        return self.lines[toPoint]

    def predict_KNN(self,fromPoint, toPoint):
        remove_bot=fromPoint-100
        remove_top=toPoint+100
        from sklearn import preprocessing
        from sklearn.neighbors import KNeighborsRegressor
        neigh_x = KNeighborsRegressor(n_neighbors=7,algorithm='kd_tree')
        neigh_y = KNeighborsRegressor(n_neighbors=7,algorithm='kd_tree')
        Xorig=  self.knn_orig_x[0]
        print "toPoint, fromPoint "+str(toPoint)+" "+str(fromPoint)
        Xfinal=  self.knn_final_x[toPoint-fromPoint]
        
        Yorig= self.knn_orig_y[0]
        Yfinal=  self.knn_final_y[toPoint-fromPoint]
        neigh_x.fit(Xorig[:remove_bot], Xfinal[:remove_bot])
        neigh_y.fit(Yorig[:remove_bot], Yfinal[:remove_bot])
        predX=neigh_x.predict(self.norm_lines[fromPoint-1])[0]
        predY=neigh_y.predict(self.norm_lines[fromPoint-1])[0]
        toRet=self.denorm((self.norm_lines[fromPoint-1][0]+predX,self.norm_lines[fromPoint-1][1]+predY))#self.norm_lines[toPoint])
        print str(self.lines[fromPoint])+" "+str(self.norm_lines[fromPoint][2])+","+str(self.norm_lines[fromPoint][3])+"->"+str(toRet)+" After "+str(toPoint-fromPoint)+"steps"
        return toRet

    def denorm(self, p):
        newx=p[0]*self.dx+self.minX
        newy=p[1]*self.dy+self.minY
        return (newx, newy)

    def read(self,filename):
        f = open(filename)
        self.lines=[line.strip().replace('[','').replace(',','').replace(']','').split() for line in f.readlines()]
        for i in range (len(self.lines)):
            self.lines[i][0]=int(self.lines[i][0])
            self.lines[i][1]=int(self.lines[i][1])
        f.close()
        self.normalize()
        self.process()
    
    def process(self):
        import numpy
        print "Process"
        if self.allow_knn and len(self.knn_orig_x)==0:
            print "KNN allowed"
            for i in range(64):
                print "Running time "+str(i)
                self.knn_orig_x.append( numpy.array(self.norm_lines)[0:len(self.norm_lines)-64,0:4]  )#.tolist())
                self.knn_orig_y.append( numpy.array(self.norm_lines)[0:len(self.norm_lines)-64,0:4]  )#.tolist())
                self.knn_final_x.append(numpy.array(self.norm_lines)[i:len(self.norm_lines)-64+i,0]-numpy.array(self.norm_lines)[0:len(self.norm_lines)-64,0])#.tolist())
                self.knn_final_y.append(numpy.array(self.norm_lines)[i:len(self.norm_lines)-64+i,1]-numpy.array(self.norm_lines)[0:len(self.norm_lines)-64,1])#.tolist())
                #self.knn_final_x.append(numpy.array(self.norm_lines)[i:len(self.norm_lines)-64+i,0])#.tolist())
                #self.knn_final_y.append(numpy.array(self.norm_lines)[i:len(self.norm_lines)-64+i,1])#.tolist())
                self.weight_call=Weight
    
    def avg_missing_points(self):
        for i in range(len(self.lines)):
            if self.lines[i][0]==-1 or self.lines[i][1]==-1:
                count=0
                while(self.lines[i+count][0]==-1 or self.lines[i+count][1]==-1):
                    count=count+1
                dx=self.lines[i+count][0]-self.lines[i-1][0]
                dy=self.lines[i+count][1]-self.lines[i-1][1]
#                print "Averaging "+str(i)+" "+str(i+count)+" "+str(self.lines[i+count])+","+str(self.lines[i-1])
                for j in range (count):
#                    print "Moving "+str(i+j)+" from ("+str(self.lines[i+j][0])+","+str(self.lines[i+j][1])+") to ("+str(self.lines[i-1][0]+dx*(0.0+j)/count)+","+str(self.lines[i-1][1]+dy*(0.0+j)/count)+")"
                    self.lines[i+j][0]=self.lines[i-1][0]+dx*(0.0+j)/count
                    self.lines[i+j][1]=self.lines[i-1][1]+dy*(0.0+j)/count
                


    def normalize(self):
        if self.allow_knn and len(self.knn_orig_x)==0:
            self.avg_missing_points()
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

        MAX_DELTA = 40    # Delta larger than this for consecutive points implies a bad datapoint
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

class Predictor_KNN(Predictor):
    def predict(self, fromPoint,toPoint):
        return self.predict_KNN(fromPoint, toPoint)
