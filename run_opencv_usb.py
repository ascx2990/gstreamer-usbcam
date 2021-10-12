import numpy as np
import cv2

WINDOW_NAME = 'CameraDemo'
image_width=640
image_height=480

cap = cv2.VideoCapture(0)
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, image_width, image_height)
cv2.moveWindow(WINDOW_NAME, 0, 0)
cv2.setWindowTitle(WINDOW_NAME, WINDOW_NAME)
while(True):
  # 從攝影機擷取一張影像
  ret, frame = cap.read()

  # 顯示圖片
  cv2.imshow(WINDOW_NAME, frame)

  # 若按下 q 鍵則離開迴圈
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

# 釋放攝影機
cap.release()

# 關閉所有 OpenCV 視窗
cv2.destroyAllWindows()
