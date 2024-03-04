import random
import numpy as np

import concurrent.futures
import pandas as pd
import numpy as np
from PIL import Image

import numpy as np
from PIL import Image
import os
import glob
import warnings
import cv2
import pandas as pd
import math
import pandas._libs.tslibs.base
warnings.filterwarnings('ignore')  # Suppress Matplotlib warnings
import time



def CalculateDistance(array, corners):

    df = array.copy()
    final_distance=np.empty((0,2))

    # final_distance=np.array([0,0,0,0])
    for i in range(int(df["Frame"].iloc[1]),int(df["Frame"].iloc[-1])):
        # clear_output(wait=True)
        # print(i)
        try:
            in_corner = 0


            row = df.loc[df["Frame"] == i]
            mouse = row.loc[df["class"] == 1]
            mx = float((mouse["Left"] + mouse["Right"]) / 2)
            my = float((mouse["Up"] + mouse["Down"]) / 2)

            for corner in corners:
                if corner[1] <= mx <= corner[2] and corner[3] <= my <= corner[4]:
                    in_corner = 1
                    break

            frame_in_corner = np.array([i,in_corner])
            final_distance= np.vstack((final_distance, frame_in_corner))

        except:

            continue
    return pd.DataFrame(final_distance, columns=["Frame Number","Inside Given Area"])



def stress(final_array,Image_annotate,VIDEO_PATHS):


    video = cv2.VideoCapture(VIDEO_PATHS)
    success, frame = video.read()
    im_height, im_width, depth = frame.shape

    Image_annotate = Image_annotate[2:,:]
    Image_annotate[:,1:3] = Image_annotate[:,1:3] / im_width
    Image_annotate[:, 3:] = Image_annotate[:, 3:] / im_height




    Processes=50
    Instances = int(int(final_array["Frame"].iloc[-1])/Processes)*2

    data=pd.DataFrame([])
    futures=[]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for i in range (Processes):
            # print(i)
            khar = executor.submit(CalculateDistance, final_array.iloc[i*Instances:(i+1)*Instances], Image_annotate)
            futures.append(khar)



        for result in concurrent.futures.as_completed(futures):
            # print(concurrent.futures.as_completed(khar))
            concat = result.result()
            data= pd.concat([data, concat],ignore_index=True)
            # print(result.result())

        data.to_csv(os.path.join("dfjhdfkjb3i746sdhfjshdfk.csv"), index=False)



