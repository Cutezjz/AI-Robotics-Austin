import math
import random
import robot

# Used to create testcases for our predictor

# It reads ~57.5 seconds(1378 poins) of data from the training file and then
# another ~2.5 seconds or 63 points and uses those 63 points to determine how
# close our prediction is.

# Need to read in 1378 lines from the training video file and then the next 63 liens.

# Need to make it as ramdon as possible.

class Testcases:

    def __init__(self):
        self.lines=[[]]
    
    def read(self,filename):
        f = open(filename)
        self.lines=[[float(d) for d in line.strip().replace('[','').replace(',','').replace(']','').split()] for line in f.readlines()]
        f.close()

    def sample(self):
        # We want 1378 lines as a testcase
        s = [[]]
        legal_num = len(self.lines) - 1378 - 63
        self.index = random.randrange(1,legal_num)
        end_num = self.index + 1378
        s = self.lines[self.index:end_num]
        return s
        

    def answer(self):
        # We want the next 63 points after the testcase
        self.answerstart = self.index + 1378
        self.answerend = self.answerstart + 63
        solution = [[]]
        solution = self.lines[self.answerstart:self.answerend]
        return solution

t = Testcases()
t.read('training_video1-centroid_data')
s = t.sample()
print('s = ', s)
solution = t.answer()
print('solution = ', solution)
