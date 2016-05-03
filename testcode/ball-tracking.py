# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import Queue
import time
from servo import*

sv = ServoManager()
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29,150, 30)
greenUpper = (64, 255, 255)
pts = deque(maxlen=args["buffer"])
 
# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture(0)
 
# otherwise, grab a reference to the video file
else:
    camera = cv2.VideoCapture(args["video"])

# keep looping
count = 0
sum_cnt = 0
angle = 90
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()
     
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if args.get("video") and not grabbed:
        break
     
    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600,height = 400)
    
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     
    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
     
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c,False)
	x_center = (int(M["m10"] / M["m00"]),240)
	
#        print angle,"\n"
#	servo.servoturn(angle)
#	time.sleep(0.5)
        # only proceed if the radius meets a minimum size
        if radius > 5:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 255,0), -1,8,0)
##            if count == 3:
##                while not q.empty():
##                    qget = q.get()
##                    sum_cnt = sum_cnt + qget
##                x_cnt_avg = sum_cnt/10.0
           
            
            if x_center[0] > 330:
                angle = max((angle -1),60) 
            elif x_center[0] < 250: 
                angle = min((angle + 1),120)
            else:
                angle = angle
               
            count  = 0
            sum_cnt = 0
            sv.servoturn(angle)            
                
    # show the frame to our screen
    #cv2.imshow("Frame", mask)
    cv2.imshow("Frame1",frame)
    key = cv2.waitKey(1) & 0xFF
     
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
#cv2.destroyAllWindows()
