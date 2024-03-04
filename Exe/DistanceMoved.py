
import numpy as np
import cv2


def calculate_distance(df, VIDEO_PATHS):
    video = cv2.VideoCapture(VIDEO_PATHS)
    success, frame = video.read()
    im_height, im_width, depth = frame.shape


    df = df[df["class"] == 1]
    x = df["Left"].values
    y = df["Up"].values
    x_distance =0
    y_distance =0
    len = x.__len__()
    for i in range (len-1):
        x_distance = x_distance +np.abs(x[i+1]-x[i])
        y_distance = y_distance +np.abs(y[i+1]-y[i])
    x_distance = x_distance*im_width
    y_distance = y_distance*im_height
    d = np.sqrt(x_distance**2+y_distance**2)
    return d



