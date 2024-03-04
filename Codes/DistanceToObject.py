
import numpy as np
import pandas as pd
import math
import concurrent.futures
import warnings
import cv2
import time
import os
import pandas._libs.tslibs.base
import glob
warnings.filterwarnings('ignore')  # Suppress Matplotlib warnings
start= time.perf_counter()

def CalculateDistance(array, NovelObCentre, FamiliarObCenter, frame,pixle_to_cm_ratio):
    im_height, im_width, depth = frame.shape
    df = array.copy()
    final_distance=np.empty((0,5))
    # final_distance=np.array([0,0,0,0])
    for i in range(int(df["Frame"].iloc[1]),int(df["Frame"].iloc[-1])):
        # clear_output(wait=True)
        # print(i)
        try:
            row = df.loc[df["Frame"] == i]
            head = row.loc[df["class"] == 2]
            mouse = row.loc[df["class"] == 1]

            hx = (head["Left"] + head["Right"]) / 2 *im_width
            hy = (head["Up"] + head["Down"]) / 2 *im_height
            mx = (mouse["Left"] + mouse["Right"]) / 2 *im_width
            my = (mouse["Up"] + mouse["Down"]) / 2 *im_height

            distance_head_to_familiar= math.sqrt((hx-FamiliarObCenter[0])**2+(hy-FamiliarObCenter[1])**2)/pixle_to_cm_ratio
            distance_body_to_familiar= math.sqrt((mx-FamiliarObCenter[0])**2+(my-FamiliarObCenter[1])**2)/pixle_to_cm_ratio

            distance_head_to_novel=math.sqrt((hx-NovelObCentre[0])**2+(hy-NovelObCentre[1])**2)/pixle_to_cm_ratio
            distance_body_to_novel=math.sqrt((mx-NovelObCentre[0])**2+(my-NovelObCentre[1])**2)/pixle_to_cm_ratio

            frame_distance = np.array([i,distance_head_to_familiar,distance_body_to_familiar,distance_head_to_novel,distance_body_to_novel])
            final_distance= np.vstack((final_distance, frame_distance))

        except:
            continue
    return pd.DataFrame(final_distance, columns=["Frame","Head to Familiar (cm)", "Body to Familiar (cm)", "Head to Novel (cm)", "Body to Novel (cm)"])




def Distance(VIDEO_PATHS,final_array,Image_annotate,pixle_to_cm_ratio):


    video = cv2.VideoCapture(VIDEO_PATHS)
    success, frame = video.read()
    im_height, im_width, depth = frame.shape

    Image_annotate = Image_annotate[:2, :]
    Image_annotate[:, 1:3] = Image_annotate[:, 1:3] / im_width
    Image_annotate[:, 3:] = Image_annotate[:, 3:] / im_height

    NovelOb = np.array([Image_annotate[0,1], Image_annotate[0,2],  Image_annotate[0,4] ,Image_annotate[0,3] ])  # ObjectLeft, ObjectRight, ObjectUP, ObjectDown


    FamiliarOb = np.array([Image_annotate[1,1], Image_annotate[1,2],  Image_annotate[1,4] ,Image_annotate[1,3] ])  # ObjectLeft, ObjectRight, ObjectUP, ObjectDown


    NovelObCentre = np.array([(NovelOb[0]+NovelOb[1])/2 , (NovelOb[2]+NovelOb[3])/2])
    FamiliarObCenter = np.array([(FamiliarOb[0]+FamiliarOb[1])/2 , (FamiliarOb[2]+FamiliarOb[3])/2])

    Processes=50
    Instances = int(int(final_array["Frame"].iloc[-1])/Processes)*2

    data=pd.DataFrame([])
    futures=[]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for i in range (Processes):

            khar = executor.submit(CalculateDistance, final_array.iloc[i*Instances:(i+1)*Instances], NovelObCentre, FamiliarObCenter,frame,pixle_to_cm_ratio)
            futures.append(khar)



        for result in concurrent.futures.as_completed(futures):
            # print(concurrent.futures.as_completed(khar))
            concat = result.result()
            data= pd.concat([data, concat],ignore_index=True)
            # print(result.result())



    data.to_csv(os.path.join("fgasjbkdfji8723hbdfjhkjs.csv"), index=False)























