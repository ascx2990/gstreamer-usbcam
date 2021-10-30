import numpy as np
import cv2
from FPS import GETFPS

WINDOW_NAME = 'CameraDemo'
image_width=640
image_height=480
fps_streams={}
fps_streams[0]=GETFPS(0)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,image_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,image_height)
cap.set(cv2.CAP_PROP_FPS,30)
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, image_width, image_height)
cv2.moveWindow(WINDOW_NAME, 0, 0)
cv2.setWindowTitle(WINDOW_NAME, WINDOW_NAME)

while(True):
  
  ret, frame = cap.read()
  #frame = cv2.resize(frame, (1280, 480), interpolation=cv2.INTER_AREA)
  cv2.imshow(WINDOW_NAME, frame)
  fps_streams[0].get_fps()
  
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break


cap.release()


cv2.destroyAllWindows()
