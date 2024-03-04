
import concurrent.futures
from sympy.geometry import *
import numpy as np
import warnings
import cv2
import sympy as sym
import pandas as pd
import math

warnings.filterwarnings('ignore')  # Suppress Matplotlib warnings
import time

start = time.perf_counter()



def CkeckLocation(ObjectLeft, ObjectRight, ObjectUP, ObjectDown, headCentre, Sight,explore_def,object_stand,O_Explore):
    #O_Explore: ObjectLeft, ObjectRight, ObjectUP, ObjectDown
    #headCentre: X, Y

    # TODO: on top of the object can be changed to centre of the body
    #check if the rodent is standing on the object
    if ObjectLeft <= headCentre[0] <= ObjectRight and ObjectDown <= headCentre[1] <= ObjectUP:
        if object_stand==1:

            return True
        else:
            return False

    # check if the rodent is in the exploration zone
    if O_Explore[0]<= headCentre[0] <=O_Explore[1] and O_Explore[3]<=headCentre[1]<=O_Explore[2]:
        # if direction is not important:
        if explore_def == 0:
            return True
        else:

            # Calculates whether the line of sight intersects the object
            S1 = Segment(Point(ObjectLeft, ObjectUP), Point(ObjectRight, ObjectDown))
            S2 = Segment(Point(ObjectRight, ObjectUP), Point(ObjectLeft, ObjectDown))

            solution1 = sym.intersection(S1, Sight)
            solution2 = sym.intersection(S2, Sight)
            if not solution1 and not solution2:
                return False
            else:
                return True

    else:
        return False




def CalculateTime (final_array, NovelOb, FamiliarOb,explore_def,object_stand,N_O_explore,  F_O_Explore):


    fObjectLeft, fObjectRight, fObjectUP, fObjectDown = FamiliarOb[:]
    nObjectLeft, nObjectRight, nObjectUP, nObjectDown = NovelOb[:]
    FrameNumber = np.array([])
    NovelFrames = np.array([])
    FamiliarFrames = np.array([])

    df = final_array.copy()  # pd.DataFrame(data=final_array, columns=['Frame', "Object", 'Left', 'right', "Up", "Down"] )

    for i in range(int(df["Frame"].iloc[1]), int(df["Frame"].iloc[-1])):

        # print(i)
        try:
            row = df.loc[df["Frame"] == i]
            head = row.loc[df["class"] == 2]
            mouse = row.loc[df["class"] == 1]

            hx = (head["Left"] + head["Right"]) / 2
            hy = (head["Up"] + head["Down"]) / 2
            mx = (mouse["Left"] + mouse["Right"]) / 2
            my = (mouse["Up"] + mouse["Down"]) / 2
            headCentre = np.array([hx.to_numpy(), hy.to_numpy()]).reshape(2, ) # X , Y
            mouseCentre = np.array([mx.to_numpy(), my.to_numpy()]).reshape(2, ) # X , Y

            degreeOfHeadImportance = 2
            bodyCentre = np.array([
                (degreeOfHeadImportance * headCentre[0] + mouseCentre[0]) / (degreeOfHeadImportance + 1),  # This is x
                (degreeOfHeadImportance * headCentre[1] + mouseCentre[1]) / (degreeOfHeadImportance + 1)  # This is Y
            ])
            # Creat the sight and send it to ckecker
            a, b = Point(mouseCentre[0], mouseCentre[1]), Point(headCentre[0], headCentre[1])
            Sight = Ray(a,b)

            NovelOb = CkeckLocation(nObjectLeft, nObjectRight, nObjectUP, nObjectDown, headCentre, Sight,explore_def,object_stand,N_O_explore)

            FamiliarOb = CkeckLocation(fObjectLeft, fObjectRight, fObjectUP, fObjectDown, headCentre, Sight,explore_def,object_stand,F_O_Explore)
            FrameNumber = np.append(FrameNumber, i)

            if NovelOb:
                # TotalFrame=TotalFrame +1
                FamiliarFrames = np.append(FamiliarFrames, 0)
                NovelFrames = np.append(NovelFrames, 1)

            elif FamiliarOb:
                # TotalFrame = TotalFrame + 1
                NovelFrames = np.append(NovelFrames, 0)
                FamiliarFrames = np.append(FamiliarFrames, 1)

            else:
                NovelFrames = np.append(NovelFrames, 0)
                FamiliarFrames = np.append(FamiliarFrames, 0)

        except:
            # print("error")
            continue

    FrameNumber = FrameNumber.reshape(FrameNumber.shape[0], 1)
    FamiliarFrames = FamiliarFrames.reshape(FamiliarFrames.shape[0], 1)
    NovelFrames = NovelFrames.reshape(NovelFrames.shape[0], 1)
    concat_data = pd.concat(
        [pd.DataFrame(FrameNumber, columns=["Frame Number"]), pd.DataFrame(FamiliarFrames, columns=["Familiar"]),
         pd.DataFrame(NovelFrames, columns=["Novel"])], axis=1)
    return concat_data





def Explore(VIDEO_PATHS, final_array, Video_annotate,explore_d,exp_dis , pixle_to_cm_ratio,object_standing,Exp_queue):

    explore_def = explore_d


    object_stand= object_standing

    video = cv2.VideoCapture(VIDEO_PATHS)
    success, frame = video.read()
    im_height, im_width, depth = frame.shape

    #Calculate the object location
    NovelOb = np.array([Video_annotate[0,1] / im_width, Video_annotate[0,2] / im_width, Video_annotate[0,4] / im_height, Video_annotate[0,3] / im_height])  # ObjectLeft, ObjectRight, ObjectUP, ObjectDown

    FamiliarOb = np.array([Video_annotate[1,1] / im_width, Video_annotate[1,2] / im_width, Video_annotate[1,4] / im_height,Video_annotate[1,3] / im_height])  # ObjectLeft, ObjectRight, ObjectUP, ObjectDown

    # Calculate the area of exploration

    y_exp_distance = exp_dis*pixle_to_cm_ratio/im_height
    x_exp_distance = exp_dis*pixle_to_cm_ratio/im_width

    N_O_explore = np.array([NovelOb[0]-x_exp_distance, NovelOb[1]+x_exp_distance, NovelOb[2]+y_exp_distance, NovelOb[3]-y_exp_distance]) # ObjectLeft, ObjectRight, ObjectUP, ObjectDown
    F_O_Explore = np.array([FamiliarOb[0]-x_exp_distance, FamiliarOb[1]+x_exp_distance, FamiliarOb[2]+y_exp_distance, FamiliarOb[3]-y_exp_distance]) # ObjectLeft, ObjectRight, ObjectUP, ObjectDown

    Processes = 50
    Instances = math.ceil(int(final_array["Frame"].iloc[-1]) / Processes) * 2


    data = pd.DataFrame([])
    futures = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for i in range(Processes):
            # print(i)
            khar = executor.submit(CalculateTime, final_array.iloc[i * Instances:(i + 1) * Instances], NovelOb,
                                   FamiliarOb,explore_def,object_stand,N_O_explore,  F_O_Explore )
            futures.append(khar)

        for result in concurrent.futures.as_completed(futures):
            # print(concurrent.futures.as_completed(khar))
            concat = result.result()
            data = pd.concat([data, concat], ignore_index=True)

    data.to_csv("dfjsdjhf5623jshdafjha.csv", index=False)



































