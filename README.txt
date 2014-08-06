======================================================
Final Project
Brad Cain, Taylor Phebus, Emiliano Lozano
======================================================

The robot motion predictor we developed is based on the K nearest neighbors 
prediction method. Upon receiving noisy XY coordinates as training data 
(Possibly the same as the testing data), the KNN predictor shall:

Preprocess the data, replacing missing points with intermediate points
Normalize each data point to relative coordinates within the box
Calculate the velocity and angle from each point to the previous point
Set a KNN mapping from each 4D, normalized point to each X and Y coordinate for the next 63 points

Upon receiving the training data, the KNN predictor shall:

Preprocess and calculate the training data with the box size determined by the 
training data
From the final 4D normalized point, compute the 7 most similar points in the 
training data.
Compute the mean change in X and Y for those 7 points for each of their next
63 points.
Add that mean offset to the final training point
Return 63 denormalized XY coordinates from that offset final point.

======================================================
Command line arguments
======================================================

python final.py -h, --help Show command line options

python final.py --training <training data file> --test <test data file> --out <output file>

The data file arguments are optional, and default as follows:

Training data file: training_video1-centroid_data

Test data file: testing_video-centroid_data

Output file: predict.txt


======================================================
Required Libraries
======================================================

Python 2.7.0+
Numpy 1.6.1+
Scipy 0.9+

Scikit-learn 0.15.0+
http://scikit-learn.org/stable/install.html
Common installation command for scikit-learn:
pip install --user --install-option="--prefix=" -U scikit-learn

On ubuntu:
sudo apt-get install python-sklearn

======================================================
Measured Results
======================================================
L2 Error
Measured over predictions from each of training points 300-1300
Predictions to each of the next 64 points
Trained without reference to test data.


** average  874.5 
** std_dev  538.2
** min      161.6
** max      4402.2

======================================================
Design Decisions
======================================================

The KNN predictor was chosen after careful consideration and comparison with a variety of predictors.

Among the alternatives considered:

* Particle filter with collision predictor and collision result predictor
** Heavily pursued and tuned, included in release. 
** Rejected in the final stage due to higher average L2 error
** average  1398.8
** std_dev  690.6
** min      145.2
** max      4220.0

* Neural Network
** Trained via weka on training data, validated via cross validation 
** Rejected due to long training time, increased complexity and higher cross validation error compared to KNN


* Linear regression
** Trained via weka on training data, validated via cross validation 
** Input parameters: normalized x, normalized y, angle, velocity
** Rejected due to extremely high cross validation error

Choices made within KNN Predictor:

* Number of neighbors
** 7 chosen through trial and error, 7 produced the lowest cross validation error

* Weighting for neighbors
** Typical choices are weighting by inverse distance and weighting uniformly
** Uniform weight chosen because inverse distance weighting did not decrease L2 error

* Handling missing points
** Decided to assume missing points are actually intemediate between the known points before and after
** Have to also handle groups of missing points


======================================================
Important files
======================================================

All files are documented internally via docstrings. To view in depth file documentation run

pydoc <file>

predict.py
The predict.py class includes the KNN predictor and various utility functions for predictors

pf_predict.py
The pf_predict.py class includes the particle filter predictor

score.py
Calculates the average L2 error from each point in the testing data

