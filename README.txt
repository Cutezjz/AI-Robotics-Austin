The general idea is that the Predictor class will read in a files in the format posted online. It can be normalized, which will convert the X,Y coordinates of the points into a pair of floats scaled by the size of the box. Hopefully one corner of the box will be 0,0, the opposite corner will be 1,1. It also has the speed and angle of each point relative to the previous point, if available.

The most important part of the predictor class is the predict function, which should predict the value of the toPoint using information up the the fromPoint. The predictor I included just cheats and looks up  the correct value. 

The scorer class evaluates the average accuracy of a predictor by asking the predictor to predict from every time step the value of the following 63 time steps. Because a real learning probably needs a few steps of data to warm up, the scorer can skip to initial_point before asking for predictions.
