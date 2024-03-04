# from tkinter import *
from tkdocviewer import *
import cv2
# Create a root window
from Exploration import Explore

import pandas as pd
from sympy.geometry import *
import sympy as sym
import numpy as np


import math
final_array= pd.read_csv("C:/PycharmProjects/pythonProject/Thesis/Software/testing_again.csv")



def test(df):
    for i in range(int(df["Frame"].iloc[1]), int(df["Frame"].iloc[-1])):
        pass


Processes=50
Instances = math.ceil(int(final_array["Frame"].iloc[-1]) / Processes*2)

if (Processes-1)*Instances > int((final_array["Frame"].iloc[-1])*2) :
    Instances = Instances-1


for i in range(Processes):
    print(i)
    test(final_array.iloc[i * Instances:(i + 1) * Instances])




#%% test the direction
import math
import time
s=time.perf_counter()

# Img_ann= pd.read_csv("C:/PycharmProjects/pythonProject/Thesis/Software/output/Image_annotations.csv")


for i in range (10000):
    x1=512.5
    y1=816.8
    x2=718.65
    y2=213.64


    # ph, pb,= Point(x1,y1), Point(x2,y2)
    # distance_head_to_novel=ph.distance(pb).evalf()

    d= math.sqrt((x1-x2)**2+(y1-y2)**2)


e=time.perf_counter()
print(e-s)
d

#%%
VIDEO_PATHS="C:/PycharmProjects/pythonProject/Thesis/Software/IMG_4582.MOV"
df= pd.read_csv("C:/PycharmProjects/pythonProject/Thesis/Software/output/IMG_4582.MOV_exploration_signal.csv")
video = cv2.VideoCapture(VIDEO_PATHS)
im_width = 1280
im_height=720



from tkinter import *
from tkinter import messagebox as mb
root=Tk()

global ra
def khar():
    global ra
    ra=56


def ass():

    print(ra)

khar()
print(ra)
root.mainloop()

ass()



















