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
#
# Usage:
#   python master.py
#
# Documentation:
#   Script to run tf model on the Pi
#
# Todo:
#   Check Trello board
#

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
from utils import label_map_util
from picamera.array import PiRGBArray
from utils import visualization_utils as vis_util

# Imports from local files
from motors import *
from remote import *
from hardware import *

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
    return
atexit.register(stopListen)

def printD(str):
    global args
    if args.debugCLA:
        print(str)
    return

# Relay variables
relayTimer = time.time()
relayOn = 0

# Init pygame for controller
pygame.init()
controllerLost = True

# Try to connect to controler
if controllerCount():
    j = pygame.joystick.Joystick(0)
    j.init()
    controllerLost = False
else:
    printD("pygame.joystick.get_count() returned 0")

# Object detection variables
THRESHOLD = 0.6
wideSpace = 200

# Movement detection (History)
movingForward = False

# Bools for operation statuses
started = False
waiting = False
auto    = False
manual  = False
printD("SLEEP")

# Set up camera constants, use smaller resolution for faster frame rates
IM_WIDTH = 1280
IM_HEIGHT = 720
#IM_WIDTH = 640
#IM_HEIGHT = 480
#IM_WIDTH = 304
#IM_HEIGHT = 304

# Default camera is picam
camera_type = 'picamera'

# File containing the model to use
################################ CHANGE ################################
MODEL_NAME = 'ssd_mobilenet_v2_coco_2018' # test card on mobile # Lower fps 1.0-1.2 2/4 0fp
#MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09' # Default
#MODEL_NAME = 'ssd_mobilenet_v1_coco_2018' # test card on mobile # Same speed as v2 but less acc
#MODEL_NAME = 'ssdlite' # test card on mobile # 0fp 0/4
#MODEL_NAME = 'card' # Able to get all 4, but with terrible fps
################################ CHANGE ################################

# Get file paths
CWD_PATH = os.getcwd()
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
################################ CHANGE ################################
PATH_TO_LABELS = os.path.join(CWD_PATH,'data', 'cardssd_labelmap.pbtxt')
#PATH_TO_LABELS = os.path.join(CWD_PATH,'data','mscoco_label_map.pbtxt')
#PATH_TO_LABELS = os.path.join(CWD_PATH,'data','labelmap.pbtxt')
################################ CHANGE ################################

# Number of classes the object detector can identify
################################ CHANGE ################################
NUM_CLASSES = 1
#NUM_CLASSES = 90 # Default
################################ CHANGE ################################

# Load labels.
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the tf model
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
    sess = tf.Session(graph=detection_graph)

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, classes, and num objects detected
detection_boxes   = detection_graph.get_tensor_by_name('detection_boxes:0')
detection_scores  = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
num_detections    = detection_graph.get_tensor_by_name('num_detections:0')

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# Initialize Picamera and grab reference to the raw capture
camera = PiCamera()
#camera.color_effects = (128,128)
camera.resolution = (IM_WIDTH,IM_HEIGHT)
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=(IM_WIDTH,IM_HEIGHT))
rawCapture.truncate(0)

# For each frame
frameCount = 0
for frame1 in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    # Get controller input
    ps4Switch = ps4(j)
    ud, lr = ps4Stick(j)

    # Change State
    if ps4Switch != 0 and not started:
        if ps4Switch == 1:
            printD("WAITING")
            started = True
            waiting = True
    elif ps4Switch != 0:
        if ps4Switch == 1 and not manual and not auto:
            printD("SLEEP")
            started = False
            waiting = False
        elif ps4Switch == 2:
            printD("MANUAL")
            waiting = False
            manual = True
            auto = False
        elif ps4Switch == 3:
            printD("AUTO")
            waiting = False
            manual = False
            auto = True
        elif ps4Switch == 4:
            printD("WAITING")
            waiting = True
            manual = False
            auto = False
        elif ps4Switch == 6 and waiting:
            printD("EXITING")
            started = False
            waiting = False
            manual = False
            auto = False
            break

    if ud != 0 or lr != 0 and manual:
       if ps4Switch == 5:
           printD("Relay")
           relay()
       else:
           printD("ud: " + str(ud) + " lr: " + str(lr))
           return
    # Check for controller disconnect
    if not controllerCount():
        if not controllerLost:
            printD("Lost Controller")
        waiting = False
        manual = False
        auto = True
        controllerLost = True

    # Check for controller reconnect
    if controllerLost and controllerCount():
        j = pygame.joystick.Joystick(0)
        j.init()
        controllerLost = False

    t1 = cv2.getTickCount()

    # Get frame from camera
    frame = np.copy(frame1.array)
    frame.setflags(write=1)
    frame_expanded = np.expand_dims(frame, axis=0)

    # Run the frame through the TF model
    if auto:
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: frame_expanded})

        # Draw the results of the detection (aka 'visulaize the results')
        vis_util.visualize_boxes_and_labels_on_image_array(
           frame,
           np.squeeze(boxes),
           np.squeeze(classes).astype(np.int32),
           np.squeeze(scores),
           category_index,
           use_normalized_coordinates=True,
           line_thickness=8,
           min_score_thresh=THRESHOLD)

        detectionCount = 0

        # For every box, find the center, draw a dot
        for index, box in enumerate(np.squeeze(boxes)):
           ymin = int((box[0]*IM_HEIGHT))
           xmin = int((box[1]*IM_WIDTH))
           ymax = int((box[2]*IM_HEIGHT))
           xmax = int((box[3]*IM_WIDTH))
           Result = np.array(frame[ymin:ymax,xmin:xmax])
           if(scores[0][index] >= THRESHOLD):
               detectionCount = detectionCount + 1
               cv2.circle(frame,(int((xmin + xmax)/2),int((ymin + ymax)/2)),5,(0,255,0),-1)

        # Get the 'primary' card's x value
        primaryx = int((boxes[0][0][1]*IM_WIDTH + boxes[0][0][3]*IM_WIDTH)/2)

        # Send instructions
        if primaryx > int(IM_WIDTH/2+wideSpace) and scores[0][0] >= THRESHOLD:
            right()
            printD('R')
            movingForward = False
        elif primaryx < int(IM_WIDTH/2-wideSpace) and scores[0][0] >= THRESHOLD:
            left()
            printD('L')
            movingForward = False
        elif primaryx > int(IM_WIDTH/2-wideSpace) and primaryx < int(IM_WIDTH/2+wideSpace) and scores[0][0] >= THRESHOLD:
            forward()
            printD('F')
            movingForward = True
        elif movingForward:
            printD('Relay & L')
            relayTimer = relay()
            relayOn = 1
            movingForward = False
        else:
            printD('I')
            idle()
            movingForward = False

    # Draw the center lines
    cv2.line(frame, (int(IM_WIDTH / 2 - wideSpace),0), (int(IM_WIDTH / 2 - wideSpace), int(IM_HEIGHT)), (0, 0, 255), 5) #left
    cv2.line(frame, (int(IM_WIDTH / 2 + wideSpace),0), (int(IM_WIDTH / 2 + wideSpace), int(IM_HEIGHT)), (0, 0, 255), 5) #right

    # Check to turn off relay
    elapsedTime = time.time() - relayTimer
    if elapsedTime > 5 and relayOn:
        relayTurnOff()
        LoadCell(hx)
        relayOn = 0

    # Check voltage every 60 frames (once a min)
    if frameCount % 60 == 0:
        voltage()
    frameCount = frameCount + 1

    # Calc Frame Rate
    t2 = cv2.getTickCount()
    time1 = (t2 - t1) / freq
    frame_rate_calc = 1 / time1

    # Display frame rate and draw to screen
    cv2.putText(frame, "FPS: {0:.2f}".format(frame_rate_calc), (30,50), font, 1, (255,255,0), 2, cv2.LINE_AA)
    cv2.imshow('Object detector', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

    rawCapture.truncate(0)

camera.close()
cv2.destroyAllWindows()
