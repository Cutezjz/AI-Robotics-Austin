#!/usr/bin/python
from predict import Predictor
from predict import Predictor_KNN
from pf_predict import PfPredictor
import math
class Scorer:
	def __init__(self, pred):
		self.p=pred

	#Calculate the average error per point from the initial point on.
	#For each point, sum the error predicting the next 63 points
	def error(self,initial_point=10, final_point=99999999):
		sum=0
		count=0
		for i in range(initial_point, min(len(self.p.lines)-64,final_point)):
			inner_sum=0
			for j in range(0,64):
				if(self.p.lines[i+j]!="-1"):
					count+=1
					inner_sum=Scorer.squared_err(self.p.predict(i,i+j),self.p.lines[i+j])		
				else:
					print "lines == -1"
			sum+=math.sqrt(inner_sum)
		return sum*64.0/(count)

	@staticmethod
	def squared_err(p1,p2):
		return (float(p1[0])-float(p2[0]))**2+(float(p1[1])-float(p2[1]))**2


	
for i in range (1,20):
	p_train=PfPredictor()
	p_train.read("training_video1-centroid_data")
	p_train.process()
	
	pf_pred=PfPredictor()
	pf_pred.read("training_video1-centroid_data")
	pf_pred.process(False)
	pf_pred.collision_database = p_train.collision_database
	print "read %d lines, saw %d collisions" % (len(pf_pred.lines), len(pf_pred.collision_database))
	print "extent is (%d, %d) to (%d, %d)" % (pf_pred.minX, pf_pred.minY, pf_pred.maxX, pf_pred.maxY)
	
	# start_index = 440
#	start_index = 1378 - 60
	start_index = i*1000+10000
	pf_pred.learn(start_index)
#	pf_pred=PfPredictor()
#	pf_pred.read("training_video1-centroid_data")
#	pf_pred.process()
#	start_index = i*1000+10000
#	pf_pred.learn(start_index)
	s_pred=Scorer(pf_pred)
	print "pf_pred"+str(math.sqrt(s_pred.error(i*1000+10000,(i*1000)+10200)))
	p_knn=Predictor_KNN()
	p_knn.read("training_video1-centroid_data")
	s_knn=Scorer(p_knn)
	print "p_knn"+str(math.sqrt(s_knn.error(i*1000+10000,(i*1000)+10200)))
