import turtle
import time
import math
from predict import Predictor
from predict import Predictor_KNN
#from pf_predict import PfPredictor

class Visualizer:
    """A class that displays actual and predicted data in a window."""

    WINDOW_WIDTH = 1024

    def __init__(self, predictor):
        self.predictor = predictor
        self.setup=False

    def visualize_many(self, start_index, count=1, old_points=16, num_visualizations=1, skip_between_visualizations=16):
        """Display actual and predicted data in a window, plotting predictions from multiple time points.

        Arguments:
        start_index -- the index at which prediction should start
        count -- the number of points to predict
        old_points -- the number of points leading up to start_index that should be displayed
        num_visualizations  -- The number of paths to visualize, meaning the number of times to call visualize
        skip_between_visualizations -- The number of time steps to skip between visualizations
        """
        for i in range(num_visualizations):
            self.visualize(start_index+(i*skip_between_visualizations), count, old_points,False)
        self.window.exitonclick()



    def visualize(self, start_index, count=1, old_points=16, wait_after_visualize=True, expect_robot_data=False):
        """Display actual and predicted data in a window.

        Arguments:
        start_index -- the index at which prediction should start
        count -- the number of points to predict
        old_points -- the number of points leading up to start_index that should be displayed
        wait_after_visualize -- Whether to wait for a mouseclick at the end of the function
        """
        pred = self.predictor
        if not self.setup:
            self.setup=True

            self.window = turtle.Screen()
            self.window.setup(self.WINDOW_WIDTH, self.WINDOW_WIDTH * pred.dy / pred.dx)
            self.window.bgcolor('black')
            self.window.setworldcoordinates(pred.minX, pred.minY+pred.dy, pred.minX+pred.dx, pred.minY)
            print 'minX=%d, minY=%d, dx=%d, dy=%d' % (pred.minX, pred.minY, pred.dx, pred.dy)
        real_data = pred.lines

        old_turtle = turtle.Turtle()
        old_turtle.shape('triangle')
        old_turtle.color('green')
        old_turtle.penup()
        old_turtle.shapesize(0.3, 0.3, 0.3)

        predict_turtle = turtle.Turtle()
        predict_turtle.shape('triangle')
        predict_turtle.color('orange')
        predict_turtle.penup()
        predict_turtle.shapesize(0.3, 0.3, 0.3)

        particle_turtle = turtle.Turtle()
        particle_turtle.shape('circle')
        particle_turtle.color('purple')
        particle_turtle.penup()
        particle_turtle.shapesize(0.3, 0.3, 0.3)

        actual_turtle = turtle.Turtle()
        actual_turtle.shape('circle')
        actual_turtle.color('light blue')
        actual_turtle.penup()
        actual_turtle.shapesize(0.3, 0.3, 0.3)

        missing_turtle = turtle.Turtle()
        missing_turtle.shape('circle')
        missing_turtle.color('white')
        missing_turtle.penup()
        missing_turtle.shapesize(0.3, 0.3, 0.3)
        missing_turtle.speed('fastest')

        old_points = min(old_points, start_index-1)

        old_turtle.speed('fastest')
        particle_turtle.speed('fastest')
        last_point = [0.0, 0.0]
        for i in range(old_points):
            point = real_data[start_index-old_points+i]
            if point[0] == -1.0:
                missing_turtle.goto(last_point[0], last_point[1])
                missing_turtle.stamp()
            else:
                old_turtle.goto(point[0], point[1])
                if len(point) >= 4 and point[3]:
                    old_turtle.setheading(point[3] * 180.0 / math.pi)
                if len(point) >= 6 and point[5]==True:
                    old_turtle.color('red')
                old_turtle.stamp()
                old_turtle.color('green')
                last_point = point
            old_turtle.speed('fast')
            old_turtle.pendown()    # (Remove this to get rid of the connecting lines)

            if expect_robot_data:
                robot_data = pred.robot_data[start_index-old_points+i]
                if robot_data[0] != -1.0:
                    particle_turtle.goto(robot_data[0], robot_data[1])
                    particle_turtle.stamp()

        predict_turtle.speed('fastest')
        actual_turtle.speed('fastest')

        # Start the "actual" trace at the last "old" point...
        actual_turtle.goto(old_turtle.xcor(), old_turtle.ycor())
        actual_turtle.pendown()

        last_point=[0.0, 0.0]
        last_prediction=[0.0, 0.0]
        for i in range(count):

            index = start_index + i
            if index < len(real_data):
                # Display actual data:
                point = real_data[index]
                if point[0] == -1.0:
                    missing_turtle.goto(last_point[0], last_point[1])
                    missing_turtle.stamp()
                else:
                    actual_turtle.goto(point[0], point[1])
                    if len(point) >= 4 and point[3]:
                        actual_turtle.setheading(point[3] * 180.0 / math.pi)  # radians -> degrees
                    actual_turtle.stamp()
                    last_point = point

            # Now display the prediction:
            if hasattr(pred, "predict_KNN") and callable(getattr(pred, "predict_KNN")):
                prediction = pred.predict_KNN(start_index-1, start_index+i)
            else:
                prediction = pred.predict(start_index-1, start_index+i)

            if prediction[0] == -1.0:
                missing_turtle.goto(last_prediction[0], last_prediction[1])
                missing_turtle.stamp()
            else:
                predict_turtle.goto(prediction[0], prediction[1])
                predict_turtle.stamp()
                last_prediction = prediction
            predict_turtle.speed('slow')
            actual_turtle.speed('slow')

        if wait_after_visualize:
            self.window.exitonclick()


# Run the code below only if this module is being directly executed
if __name__ == "__main__":
    p=Predictor_KNN()
    #p=PfPredictor()
    p.read("training_video1-centroid_data")
    p.process()
    #print "read %d lines, saw %d collisions" % (len(p.lines), len(p.collision_indices))
    #print "extent is (%d, %d) to (%d, %d)" % (p.minX, p.minY, p.maxX, p.maxY)
    
    start_index = 440
    # start_index = 1378
    #p.learn(start_index)
    vis = Visualizer(p)
    #vis.visualize_many(512, 16, 64,3,5)
    vis.visualize_many(440, 16, 64,3,5)
    #vis.visualize_many(2000, 16, 64,3,5)
