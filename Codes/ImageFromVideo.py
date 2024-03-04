from IPython.display import clear_output
import threading
from PIL import Image


import cv2
cap = cv2.VideoCapture("C:/Users/Connor Lab/Desktop/Neuroscience/Data/videos/Connor/training/male/Video/IMG_4778.MOV")

i=0
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # cv2.imwrite("C:/Users/Connor Lab/Desktop/Neuroscience/Data/videos/Connor/training/sample_image2.JPG", frame)
    cv2.namedWindow("Object Detector", cv2.WINDOW_NORMAL)  # Create window with freedom of dimensions

    cv2.imwrite("image_with_detections.jpg", frame)
    cv2.imshow('Object Detector', frame)
    # CLOSES WINDOW ONCE KEY IS PRESSED
    cv2.waitKey(0)
    # CLEANUP
    cv2.destroyAllWindows()
    i+=1
    if i==10:
        break


        # Our operations on the frame come here
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #
    # # Display the resulting frame
    # cv2.imshow('frame',gray)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    # break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()


