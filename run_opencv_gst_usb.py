
import sys
import argparse
import subprocess

import cv2


WINDOW_NAME = 'CameraDemo'
image_width=640
image_height=480




def open_cam_usb(dev, width, height):
    gst_str = ('v4l2src device=/dev/video{} ! '
               'video/x-raw, width=(int){}, height=(int){} ! '
               'videoconvert ! appsink').format(dev, width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)





def open_window(width, height):
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, width, height)
    cv2.moveWindow(WINDOW_NAME, 0, 0)
    cv2.setWindowTitle(WINDOW_NAME, WINDOW_NAME)


def read_cam(cap):
    
    while True:
        if cv2.getWindowProperty(WINDOW_NAME, 0) < 0:
            break
        _, img = cap.read() 
        
        cv2.imshow(WINDOW_NAME, img)
        key = cv2.waitKey(10)
        if key == 27: # ESC key: quit program
            break


def main():
   
    print('OpenCV version: {}'.format(cv2.__version__))

   
    cap = open_cam_usb("0",
                       image_width,
                       image_height)

    if not cap.isOpened():
        sys.exit('Failed to open camera!')

    open_window(image_width, image_height)
    read_cam(cap)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
