#!/usr/bin/python
from predict import Predictor
import math
import argparse

parser=argparse.ArgumentParser(description='Predict the position of the hexbug')
parser.add_argument("--training",help="Training data to use", default="training_video1-centroid_data")
parser.add_argument("--test",help="Test data to predict to the end", default="training_video1-centroid_data")

args=parser.parse_args()
p=Predictor()
p.read(args.training)

print (p.predict_KNN(len(p.lines),len(p.lines)+1))
result=[]
for i in range(64):
	result.append(p.predict_KNN(len(p.lines),len(p.lines)+i))
print result
