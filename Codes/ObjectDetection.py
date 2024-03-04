
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging (1)
import tensorflow as tf
import cv2
import pandas as pd
import pandas._libs.tslibs.base
import multiprocessing
import numpy as np
from PIL import Image
import warnings

# tf.config.set_visible_devices([], 'GPU')

# my_devices = tf.config.experimental.list_physical_devices(device_type='CPU')
# tf.config.experimental.set_visible_devices(devices= my_devices, device_type='CPU')

#
multiprocessing.set_start_method("spawn",force=True)
tf.get_logger().setLevel('ERROR')  # Suppress TensorFlow logging (2)
# Enable GPU dynamic memory allocation
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

warnings.filterwarnings('ignore')  # Suppress Matplotlib warnings


def load_image_into_numpy_array(path):
    """Load an image from file into a numpy array.

    Puts image into numpy array to feed into tensorflow graph.
    Note that by convention we put it into a numpy array with shape
    (height, width, channels), where channels=3 for RGB.

    Args:
      path: the file path to the image

    Returns:
      uint8 numpy array with shape (img_height, img_width, 3)
    """
    return np.array(Image.open(path))



def create_final_data(detections, Frame_number):
    det_frame = pd.DataFrame(data=np.ones([100, 1]) * Frame_number, columns=["Frame"])
    det_box = pd.DataFrame(data=detections["detection_boxes"], columns=["Down", "Left", "Up", "Right"])
    det_score = pd.DataFrame(data=detections["detection_scores"], columns=["score"])
    det_class = pd.DataFrame(data=detections["detection_classes"], columns=["class"])
    det = pd.concat([det_frame, det_box, det_score, det_class], axis=1)
    df = det.iloc[[0]]
    for index, row in det.iterrows():
        if det.iloc[index]["class"] != det.iloc[0]["class"]:
            df = df.append(det.iloc[index])

            break

    return df


def creat_array(VIDEO_PATHS,detect_fn, video_cap, fps, queue):

    video = cv2.VideoCapture(VIDEO_PATHS)


    rate = round(video.get(cv2.CAP_PROP_FPS)/fps)

    if video_cap[0] ==1:

        video.set(cv2.CAP_PROP_POS_FRAMES, int(video.get(cv2.CAP_PROP_FRAME_COUNT) *video_cap[1]/100))
        end = video.get(cv2.CAP_PROP_FRAME_COUNT)- video.get(cv2.CAP_PROP_FRAME_COUNT) * int(video_cap[2]/100)
    elif video_cap[0]==2:
        video.set(cv2.CAP_PROP_POS_FRAMES, int(video.get(cv2.CAP_PROP_FPS)*(video_cap[3]*60+video_cap[5])) )
        end = video.get(cv2.CAP_PROP_FRAME_COUNT) - int(video.get(cv2.CAP_PROP_FPS)*(video_cap[4]*60+video_cap[6]))
    else:
        end = 1000000000


    # Read video & Set the Frame_number
    success, frame = video.read()
    Frame_number = 0
    final_array = np.array([])
    x = 0
    while success:
        if x>= end:
            break
        if x % rate == 0:

            # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
            # i.e. a single-column array, where each item in the column has the pixel RGB value

            # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # frame_expanded = np.expand_dims(frame_rgb, axis=0)

            # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
            input_tensor = tf.convert_to_tensor(frame)
            # The model expects a batch of images, so add an axis with `tf.newaxis`.
            input_tensor = input_tensor[tf.newaxis, ...]

            # input_tensor = np.expand_dims(image_np, 0)
            detections = detect_fn(input_tensor)

            # All outputs are batches tensors.
            # Convert to numpy arrays, and take index [0] to remove the batch dimension.
            # We're only interested in the first num_detections.
            num_detections = int(detections.pop('num_detections'))
            detections = {key: value[0, :num_detections].numpy()
                          for key, value in detections.items()}
            detections['num_detections'] = num_detections

            # detection_classes should be ints.
            detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
            result = create_final_data(detections, Frame_number)

            if Frame_number == 0:
                final_result = result.copy()
            else:
                final_result = final_result.append(result, ignore_index=True)
                # clear_output(wait=True)
                # print(Frame_number)


            success, frame = video.read()
            Frame_number = Frame_number + 1
            x += 1

        else:
            success, frame = video.read()
            x += 1
        # if x==20:
        #     break
    pd.DataFrame(final_result).to_csv("testing_again.csv", index=False)

    queue.put(final_result)

    # return final_result




