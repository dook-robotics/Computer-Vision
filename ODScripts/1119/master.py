## master.py ##
## Master scripts for OD and Motors ##
#
# Authors:
#   Mikian Musser      - https://github.com/mm909
#   Eric Becerril-Blas - https://github.com/lordbecerril
#   Zoyla Orellana     - https://github.com/ZoylaO
#   Austin Janushan    - https://github.com/Janushan-Austin
#   Giovanny Vazquez   - https://github.com/giovannyVazquez
#   Ameera Essaqi      - https://github.com/AmeeraE
#   Brandon Herrera    - herrer10@unlv.nevada.edu
#   Esdras Morales     - morale2@unlv.nevada.edu
#
# Organization:
#   Dook Robotics - https://github.com/dook-robotics

# Imports
import os
import cv2
import sys
import time
import errno
import pygame
import atexit
import argparse
import numpy as np
import tensorflow as tf
import RPi.GPIO as GPIO
from hx711 import HX711
from picamera import PiCamera
# from firebase import firebase
from utils import label_map_util
from picamera.array import PiRGBArray
from utils import visualization_utils as vis_util

# Imports from local files
from motors import *
from remote import *
from hardware import *

# This defines where our database is online
#firebase = firebase.FirebaseApplication('https://dook-726e9.firebaseio.com/')

# Clear imports
os.system("clear")

# Add command line arguments
parser = argparse.ArgumentParser(
                                 description = 'Dook Robotics - Object Detection Master Script',
                                 epilog = "Dook Robotics - https://github.com/dook-robotics"
                                )

parser.add_argument(
                               '--debug',
                     dest    = 'debugCLA',
                     action  = 'store_true',
                     default = 'False',
                     help    = 'Prints out all debug messages.'
                    )

parser.add_argument(
                               '--hardware',
                     choices = ['True', 'False'],
                     dest    = 'hardwareCLA',
                     default = 'False',
                     help    = 'Allows hardware to be called.'
                    )

args = parser.parse_args()

# Cleanup Function
def stopListen():
    GPIO.cleanup()
    # Post to firebase?
    return
atexit.register(stopListen)

# Relay variables
relayTimer = time.time()
relayOn    = 0

# Init pygame for controller
pygame.init()
controllerLost = True

# Try to connect to controler
if controllerCount():
    print("Controller Detected")
    j = pygame.joystick.Joystick(0)
    j.init()
    controllerLost = False
    print("Controller Connected")
else:
    print("pygame.joystick.get_count() returned 0")

# Object detection variables
THRESHOLD = 0.6
wideSpace = 10

# Movement detection (History)
movingForward = False

# Bools for operation statuses
started = False
waiting = False
auto    = False
manual  = False
print("Starting in SLEEP state")

# Stop all motors
stop()

# Set up camera constants, use smaller resolution for faster frame rates
IM_WIDTH  = 889 #1280
IM_HEIGHT = 500 #720

# Default camera is picam
camera_type = 'picamera'

# File containing the model to use
################################ CHANGE ################################
MODEL_NAME = 'ssd_mobilenet_v2.2.5'
################################ CHANGE ################################

# Get file paths
CWD_PATH = os.getcwd()
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME, 'frozen_inference_graph.pb')

# Path to label map file
################################ CHANGE ################################
PATH_TO_LABELS = os.path.join(CWD_PATH, 'data', 'poop.pbtxt')
################################ CHANGE ################################

# Number of classes the object detector can identify
################################ CHANGE ################################
NUM_CLASSES = 1
################################ CHANGE ################################

# Load labels.
label_map      = label_map_util.load_labelmap(PATH_TO_LABELS)
categories     = label_map_util.convert_label_map_to_categories(label_map, max_num_classes = NUM_CLASSES, use_display_name = True)
category_index = label_map_util.create_category_index(categories)

# Load the tf model
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name = '')
    sess = tf.Session(graph = detection_graph)

# Input tensor is the image
image_tensor      = detection_graph.get_tensor_by_name(   'image_tensor:0'  )

# Output tensors are the detection boxes, scores, classes, and num objects detected
detection_boxes   = detection_graph.get_tensor_by_name( 'detection_boxes:0' )
detection_scores  = detection_graph.get_tensor_by_name('detection_scores:0' )
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
num_detections    = detection_graph.get_tensor_by_name(  'num_detections:0' )

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# Initialize Picamera and grab reference to the raw capture
camera = PiCamera()
# camera.color_effects = (128,128)
camera.resolution = (IM_WIDTH,IM_HEIGHT)
camera.framerate  = 10
rawCapture        = PiRGBArray(camera, size = (IM_WIDTH,IM_HEIGHT))
rawCapture.truncate(0)

# For each frame
frameCount = 0
t1         = cv2.getTickCount()
averageFPS = 0.0
sumFPS     = 0.0

motorTime     = 0
runningMotors = 0
forwardTime   = 4

ud = 0
lr = 0

for frame1 in camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True):
    # Check voltage every 60 frames (once a min)
    #if frameCount % 60 == 0:
      #v,m1, m2 = voltage()
    '''
    result = firebase.post('https://dook-726e9.firebaseio.com/',{'motor1':m1})
    if result > 299:
	print("bad")
    result = firebase.post('https://dook-726e9.firebaseio.com/',{'motor2':m2})
    if result > 299:
	print("bad")
    result = firebase.post('https://dook-726e9.firebaseio.com/',{'voltage':v})
    if result > 299:
	print("bad")
    '''
    frameCount = frameCount + 1

    # Calc Frame Rate
    t2 = cv2.getTickCount()
    time1 = (t2 - t1) / freq
    frame_rate_calc = 1 / time1

    #Calc average FPS
    sumFPS     = sumFPS + frame_rate_calc
    averageFPS = sumFPS / frameCount

    # Get controller input
    if not controllerLost:
        ps4Switch, ps4Stick = ps4(j)

        if 1 in ps4Stick:
            ud = ps4Stick[1]
        if 0 in ps4Stick:
            lr = ps4Stick[0]

        #print("ud: " + str(ud) + " lr: " + str(lr))

        # Change State
        if ps4Switch != 0 and not started:
            if ps4Switch == 1:
                print("WAITING")
                started = True
                waiting = True
                stop()
        elif ps4Switch != 0:
            if ps4Switch == 1 and not manual and not auto:
                print("SLEEP")
                started = False
                waiting = False
                stop()
            elif ps4Switch == 2:
                print("MANUAL")
                waiting = False
                manual  = True
                auto    = False
                stop()
            elif ps4Switch == 3:
                print("AUTO")
                waiting = False
                manual  = False
                auto    = True
                stop()
            elif ps4Switch == 4:
                print("WAITING")
                waiting = True
                manual  = False
                auto    = False
                stop()
            elif ps4Switch == 7:
                #down
                #servo(-1)
                print("servo down")
            elif ps4Switch == 8:
                #up
                #servo(1)
                print("servo up")
            elif ps4Switch == 6 and waiting:
                print("EXITING")
                started = False
                waiting = False
                manual  = False
                auto    = False
                stop()
                break

        if not started and ps4Switch == 6:
            exit()

        if manual:
            manMotors(ud,lr)

        if manual and ps4Switch == 5:
           print("Relay")
           #relayTimer = relay()
           #relayOn = 1
           #else:
           #    print("ud: " + str(ud) + " lr: " + str(lr))
           #    continue

    # Check for controller disconnect
    if not controllerCount():
        print("Lost Controller")
        print("Setting auto")
        waiting        = False
        manual         = False
        auto           = True
        controllerLost = True

    # Check for controller reconnect
    if controllerLost and controllerCount():
        print("reconnecting")
        j = pygame.joystick.Joystick(0)
        j.init()
        controllerLost = False

    t1 = cv2.getTickCount()

    # Get frame from camera
    frame = np.copy(frame1.array)
    frame.setflags(write = 1)
    frame_expanded = np.expand_dims(frame, axis = 0)

    # Run the frame through the TF model
    if auto:
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict = {image_tensor: frame_expanded})

        # Draw the results of the detection (aka 'visulaize the results')
        vis_util.visualize_boxes_and_labels_on_image_array(
           frame,
           np.squeeze(boxes),
           np.squeeze(classes).astype(np.int32),
           np.squeeze(scores),
           category_index,
           use_normalized_coordinates = True,
           line_thickness             = 8,
           min_score_thresh           = THRESHOLD
        )

        detectionCount = 0

        # For every box, find the center, draw a dot
        for index, box in enumerate(np.squeeze(boxes)):
           ymin   = int((box[0] * IM_HEIGHT))
           xmin   = int((box[1] * IM_WIDTH ))
           ymax   = int((box[2] * IM_HEIGHT))
           xmax   = int((box[3] * IM_WIDTH ))
           Result = np.array(frame[ymin:ymax, xmin:xmax])
           if(scores[0][index] >= THRESHOLD):
               detectionCount = detectionCount + 1
               cv2.circle(frame,(int((xmin + xmax) / 2),int((ymin + ymax) / 2)), 5, (0,255,0), -1)

        # Get the 'primary' card's x value
        primaryx = int((boxes[0][0][1] * IM_WIDTH  + boxes[0][0][3] * IM_WIDTH ) / 2)
        primaryy = int((boxes[0][0][0] * IM_HEIGHT + boxes[0][0][2] * IM_HEIGHT) / 2)

        #stops object detection from moving if we are currently picking up poop
        if not relayOn:
            # Send instructions
            if primaryx > int(IM_WIDTH / 2 + wideSpace) and scores[0][0] >= THRESHOLD:
                print('R')
                right()
                movingForward = False
            elif primaryx < int(IM_WIDTH / 2 - wideSpace) and scores[0][0] >= THRESHOLD:
                print('L')
                left()
                movingForward = False
            elif primaryx > int(IM_WIDTH / 2 - wideSpace) and primaryx < int(IM_WIDTH / 2 + wideSpace) and scores[0][0] >= THRESHOLD:
                print('F')
                forward()
                if primaryy > IM_HEIGHT * 0.9:
                    movingForward = True
            elif movingForward:
                print('Relay & L')
                movingForward = False
                # print("Running motors for " + str(forwardTime) + " seconds.")
                # motorTime     = runMotorsNonBlocking()
                # runningMotors = 1
                runMotors(forwardTime)

                #relayTimer = relay()
                #relayOn = 1
            else:
                print('I')
                idle()
                movingForward = False

    # if((time.time() - motorTime >= forwardTime) and runningMotors):
    #     stop()
    #     runningMotors = 0

    # Draw the center lines
    cv2.line(frame, (int(IM_WIDTH / 2 - wideSpace), 0), (int(IM_WIDTH / 2 - wideSpace), int(IM_HEIGHT)), (0, 0, 255), 5) #left
    cv2.line(frame, (int(IM_WIDTH / 2 + wideSpace), 0), (int(IM_WIDTH / 2 + wideSpace), int(IM_HEIGHT)), (0, 0, 255), 5) #right

    # Check to turn off relay
    elapsedTime = time.time() - relayTimer
    if elapsedTime > 25 and relayOn:
        relayTurnOff()
        relayOn = 0
        #lc = LoadCell(hx)
    	#result = firebase.post('https://dook-726e9.firebaseio.com/',{'loadSensor':int(lc)})
    	#if result > 299:
    	#	print ("bad)

    # Display frame rate and draw to screen
    cv2.putText(frame, "FPS: {0:.2f}".format(frame_rate_calc),    (30,  50), font, 1, (255,255,0), 2, cv2.LINE_AA)
    cv2.putText(frame, "Average FPS: {0:.2f}".format(averageFPS), (30, 150), font, 1, (255,255,0), 2, cv2.LINE_AA)

    cv2.imshow('Object detector', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

    rawCapture.truncate(0)

camera.close()
cv2.destroyAllWindows()
