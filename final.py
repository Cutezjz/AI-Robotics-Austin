#!/usr/bin/python
from predict import Predictor_KNN
import math
import argparse

"""
Final.py will read in the training data and testing data. It will then call the
KNN predictor to predict the next 64 points in the hex bug's path.
The output will be sent to the prediction.txt file in the required format
"""

# Setup the arguments for the training data and testing data
parser=argparse.ArgumentParser(description='Predict the position of the hexbug')
parser.add_argument("--training",help="Training data to use", default="training_video1-centroid_data")
parser.add_argument("--test",help="Test data to predict to the end", default="testing_video-centroid_data")
parser.add_argument("--out",help="Output file to write prediction to", default="prediction.txt")

# Assign the file names as arguments
args=parser.parse_args()

# Setup our predictor
p=Predictor_KNN()

# Read the training data
p.read(args.training)

# Read the test data
p.read_test_set(args.test)

# Add the predicted results to result list
result=[]
for i in range(64):
	result.append(p.predict_KNN(len(p.test_set_lines),len(p.test_set_lines)+1+i))

# Output predictions to predictions.txt file in required format
output = open(args.out, "w")
output.write('[')
for i in range(63):
        output.write(str(result[i]).replace('(','[').replace(')',']').replace(' ',''))
        output.write(',')
        output.write('\n')

for i in range(63, 64):
        output.write(str(result[i]).replace('(','[').replace(')',']'))
        output.write(']')

output.close()
