import turtle
import time
import math
from predict import Predictor2

class Visualizer:
    """A class that displays actual and predicted data in a window."""

    WINDOW_WIDTH = 1024

    def __init__(self, predictor):
        self.predictor = predictor

    def visualize(self, start_index, count=1, old_points=16):
        """Display actual and predicted data in a window.

        Arguments:
        start_index -- the index at which prediction should start
        count -- the number of points to predict
        old_points -- the number of points leading up to start_index that should be displayed
        """

        pred = self.predictor
        real_data = pred.lines

        window = turtle.Screen()
        window.setup(self.WINDOW_WIDTH, self.WINDOW_WIDTH * pred.dy / pred.dx)
        window.bgcolor('black')
        window.setworldcoordinates(pred.minX, pred.minY+pred.dy, pred.minX+pred.dx, pred.minY)
        print 'minX=%d, minY=%d, dx=%d, dy=%d' % (pred.minX, pred.minY, pred.dx, pred.dy)

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

        actual_turtle = turtle.Turtle()
        actual_turtle.shape('circle')
        actual_turtle.color('light blue')
        actual_turtle.penup()
        actual_turtle.shapesize(0.3, 0.3, 0.3)

        missing_turtle = turtle.Turtle()
        missing_turtle.shape('circle')
        missing_turtle.color('red')
        missing_turtle.penup()
        missing_turtle.shapesize(0.3, 0.3, 0.3)
        missing_turtle.speed('fastest')

        old_points = min(old_points, start_index-1)

        old_turtle.speed('fastest')
        last_point = [0.0, 0.0]
        for i in range(old_points):
            point = real_data[start_index-old_points+i]
            if point[0] == -1.0:
                missing_turtle.goto(last_point[0], last_point[1])
                missing_turtle.stamp()
            else:
                old_turtle.goto(point[0], point[1])
                if len(point) >= 4:
                    old_turtle.setheading(point[3] * 180.0 / math.pi)
                old_turtle.stamp()
                last_point = point
            old_turtle.speed('fast')
            old_turtle.pendown()    # (Remove this to get rid of the connecting lines)

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
                    if len(point) >= 4:
                        actual_turtle.setheading(point[3] * 180.0 / math.pi)  # radians -> degrees
                    actual_turtle.stamp()
                    last_point = point

            # Now display the prediction:
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

        window.exitonclick()

p=Predictor2()
p.read("training_video1-centroid_data")
p.process()
vis = Visualizer(p)
vis.visualize(512, 16, 64)
