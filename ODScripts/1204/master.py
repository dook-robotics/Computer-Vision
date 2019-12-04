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
import datetime
import numpy as np
import tensorflow as tf
import RPi.GPIO as GPIO
from hx711 import HX711
from picamera import PiCamera
from firebase import firebase
from utils import label_map_util
from picamera.array import PiRGBArray
from utils import visualization_utils as vis_util

# Imports from local files
from motors import *
from remote import *
from hardware import *


# This defines where our database is online
firebase = firebase.FirebaseApplication('https://dook-726e9.firebaseio.com/')

# ---------- Add command line arguments ----------
parser = argparse.ArgumentParser(
                                 description = 'Dook Robotics - Object Detection Master Script',
                                 epilog = "Dook Robotics - https://github.com/dook-robotics"
                                )

parser.add_argument(
                               '--debug',
                     dest    = 'debugCLA',
                     action  = 'store_true',
                     default = False,
                     help    = 'Prints out all debug messages.'
                    )

parser.add_argument(
                               '--hardwareOff',
                     dest    = 'hardwareCLA',
                     action  = 'store_true',
                     default = False,
                     help    = 'Allows hardware to be called.'
                    )

parser.add_argument(
                               '--battery',
                     dest    = 'batteryNumCLA',
                     required = True,
                     help    = 'Battery number.'
                    )

parser.add_argument(
                               '--newBattery',
                     dest    = 'newBatteryCLA',
                     action  = 'store_true',
                     default = False,
                     help    = 'If battery is recharged.'
                    )

args = parser.parse_args()

# Clear imports
os.system("clear")

print("\n ===================================")
print(" ========== Dook Robotics ==========")
print(" ==========  Version 1.0  ==========")
print(" ===================================\n")


def dprint(message):
    if args.debugCLA:
        print(message)

# Cleanup Function
def stopListen():
    GPIO.cleanup()
    firebase.put('PowerButton/Machine/','power',0)
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
THRESHOLD     = 0.3
ROPETHRESHOLD = 0.6
wideSpaceRatio = 0.15#0.19
pickUpThresh = 0.5
anitGLZone = 0.9

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
IM_WIDTH  = 896#1200#896 #1200 #300
IM_HEIGHT = 512#720#512 #720 #300

wideSpace     = (int)(IM_WIDTH * wideSpaceRatio)
# Default camera is picam
camera_type = 'picamera'

# File containing the model to use
################################ CHANGE ################################

                # ==== Total - v2.1.0 - 0.50 ====
                # Detections               : 748
                # Total False Detections   : 0
                # Successful Detections    : 748
                # Total objects            : 767
                # True Accuracy            : 0.98
                # Effective Accuracy       : 0.98
                # ===============================
#MODEL_NAME = 'ssd_mobilenet_v2.1.0' # Poop

                # ===== SSD - v2.2.5 - 0.25 =====
                # Detections               : 1359
                # Total False Detections   : 18
                # Successful Detections    : 1341
                # Total objects            : 1365
                # True Accuracy            : 0.98
                # Effective Accuracy       : 0.97
                # ========== Data - v2 ==========
MODEL_NAME = 'ssd_mobilenet_v2.2.5' # Poop and rocks

                # ===== SSD - v2.5.5 - 0.30 =====
                # Detections               : 2368
                # Total False Detections   : 119
                # Successful Detections    : 2249
                # Total objects            : 2349
                # True Accuracy            : 0.96
                # Effective Accuracy       : 0.91
                # ====== Data - All Images ======
#MODEL_NAME = 'ssd_mobilenet_v2.5.5' # Poop and rope

################################ CHANGE ################################

# Get file paths
CWD_PATH = os.getcwd()
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME, 'frozen_inference_graph.pb')

# Path to label map file
################################ CHANGE ################################
PATH_TO_LABELS = os.path.join(CWD_PATH, 'data', 'poop.pbtxt')
#PATH_TO_LABELS = os.path.join(CWD_PATH, 'data', 'ropePoop.pbtxt')
################################ CHANGE ################################

# Number of classes the object detector can identify
################################ CHANGE ################################
NUM_CLASSES = 1
#NUM_CLASSES = 2
################################ CHANGE ################################

''' Start building tensorflow '''

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

''' Finish building tensorflow '''

# This gets the weightOffSet
weightOffSet = firebase.get('Pi/loadCell/',None)
if weightOffSet == -1:
    weightOffSet = 0
    try:
        data = firebase.put('Pi/','loadCell',weightOffSet)
    except:
        print("Error update load cell data")
      

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# Initialize Picamera and grab reference to the raw capture
camera = PiCamera()
camera.resolution = (IM_WIDTH,IM_HEIGHT)
camera.framerate  = 100
rawCapture        = PiRGBArray(camera, size = (IM_WIDTH,IM_HEIGHT))
rawCapture.truncate(0)

# For each frame
frameCount = 0
t1         = cv2.getTickCount()
averageFPS = 0.0
sumFPS     = 0.0

motorTime     = 0
runningMotors = 0
forwardTime   = 3

ud = 0
lr = 0

checkVoltageInt = 60
lowVoltage    = 34
exitVoltage   = 33
voltageStatus =  1
fanTime       = 20#15
maxWeight     = 70

voltageHistoryFile = open("voltageHistory" + args.batteryNumCLA  + ".txt", "a")
value = datetime.datetime.fromtimestamp(time.time())
if args.newBatteryCLA:
    voltageHistoryFile.write("\n========== " + value.strftime('%Y-%m-%d %H:%M:%S') + " ========== (N)\n\n")
else:
    voltageHistoryFile.write("\n========== " + value.strftime('%Y-%m-%d %H:%M:%S') + " ==========\n\n")
v, m1, m2, voltageTime = voltage()

try:
    firebase.put('Pi/','Voltage', v)
except:
    print("Error updating voltage")
    
value = datetime.datetime.fromtimestamp(time.time())
voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Battery: " + args.batteryNumCLA + ") | " + str(v) + "v\n")
#voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor1)     | " + str(m1) + " amps\n")
#voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor2)     | " + str(m2) + " amps\n")
#voltageHistoryFile.write("\n")

print("Starting Voltage: " + str(v))

currentState = False
#currentState = 1

IdleTurnStatus = 0

GraceFrameCount = 10
PooplessFrameCount = 0

for frame1 in camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True):

    frameCount = frameCount + 1

    # Calc Frame Rate
    t2 = cv2.getTickCount()
    time1 = (t2 - t1) / freq
    frame_rate_calc = 1 / time1

    #Calc average FPS
    sumFPS     = sumFPS + frame_rate_calc
    averageFPS = sumFPS / frameCount

    #GET the current state according to the app. Get dook-777
    if frameCount % 10 == 0 and not auto and not manual:
        currentState = firebase.get('PowerButton/Machine/power',None)
        print(currentState)
    if currentState == 1 and not manual and not auto:
        print("App starting Waiting")
        waiting = True
        started = True
        manual  = False
        auto    = False
        stop()
    elif currentState == 0:
        print("App starting SLEEP")
        started = False
        waiting = False
        manual  = False
        auto    = False
        stop()


    # Get controller input
    if not controllerLost:
        ps4Switch, ps4Stick = ps4(j)

        if 1 in ps4Stick:
            ud = ps4Stick[1]
        if 0 in ps4Stick:
            lr = ps4Stick[0]

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
                if relayOn:
                    relayTurnOff()
                    relayOn = 0
                runningMotors = 0
                stop()
            elif ps4Switch == 3:
                print("AUTO")
                waiting = False
                manual  = False
                auto    = True
                stop()
                PooplessFrameCount = 0
            elif ps4Switch == 4:
                print("WAITING")
                waiting = True
                manual  = False
                auto    = False
                stop()
            #elif ps4Switch == 7:
            #    #down
            #    #servo(-1)
            #    print("servo down")
            #elif ps4Switch == 8:
            #    #up
            #    #servo(1)
            #    print("servo up")
            elif ps4Switch == 7:
                setMotors(0, 60, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)
            elif ps4Switch == 8:
                setMotors(60, 0, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.LOW)
            elif ps4Switch == 9:
                setMotors(60, 60, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.LOW)
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
           relayTimer = relay()
           relayOn = 1

           # Query data for loadcell 
           data = 0
           try:
                data = firebase.get('Pi/loadCell/',None)
           except:
                print("Error getting load cell data")
           
           if data == -1:
                weightOffSet = 0
                hx = LoadCellInit()
                
           lcWeight = LoadCell(hx, weightOffSet)
           # post new value to firebase
           try:
                firebase.put('Pi/','loadCell',lcWeight)
           except:
                print("Error posting load cell data to firebase")
           if lcWeight > maxWeight:
                print("SLEEP because im full")
                started = False
                waiting = False
                auto = False
                manual = False
                stop()

    # Check for controller disconnect
    if not controllerCount():
        print("Lost Controller")
        print("Setting auto")
        waiting        = False
        manual         = False
        auto           = True
        controllerLost = True

    t1 = cv2.getTickCount()

    # Get frame from camera
    frame = np.copy(frame1.array)
    frame.setflags(write = 1)
    frame_expanded = np.expand_dims(frame, axis = 0)

    # Run the frame through the TF model
    currTime = time.time()
    ableToCheckVoltage = True
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

        primaryx = -1
        primaryy = -1
        poopMax  =  0
        primaryXMin = 0
        primaryXMax = 0
        primaryYMin = 0
        primaryYMax = 0
        
        # For every box, find the center, draw a dot
        for index, box in enumerate(np.squeeze(boxes)):
           poopDetection = False
           ropeDetection = False
           if scores[0][index] < THRESHOLD:
               break
           if np.squeeze(classes)[index] == 1:
               poopDetection = scores[0][index] >= THRESHOLD
           if np.squeeze(classes)[index] == 2:
               ropeDetection = scores[0][index] >= ROPETHRESHOLD
           if poopDetection or ropeDetection:
               ableToCheckVoltage = False
               PooplessFrameCount = 0
               ymin   = int((box[0] * IM_HEIGHT))
               xmin   = int((box[1] * IM_WIDTH ))
               ymax   = int((box[2] * IM_HEIGHT))
               xmax   = int((box[3] * IM_WIDTH ))
               cv2.circle(frame, (int((xmin + xmax) / 2), int((ymin + ymax) / 2)), 5, (0,255,0), -1)
               # Get the 'primary' poop's x and y value
               
               if(np.squeeze(classes)[index] == 1 and scores[0][index] > poopMax):
                   poopMax  = scores[0][index]
                   primaryXMin = xmin
                   primaryXMax = xmax
                   primaryYMin = ymin
                   primaryYMax = ymax
                   primaryx = int((boxes[0][index][1] * IM_WIDTH  + boxes[0][index][3] * IM_WIDTH ) / 2)
                   primaryy = int((boxes[0][index][0] * IM_HEIGHT + boxes[0][index][2] * IM_HEIGHT) / 2)
               # if(np.squeeze(classes)[index] == 2):
               #     # run
               #     continue

        #stops object detection from moving if we are currently picking up poop
        if not relayOn and not runningMotors:
            # Send instructions
            if primaryYMax > (IM_HEIGHT * anitGLZone) and (primaryXMin < int(IM_WIDTH / 2 - wideSpace) or  primaryXMax > int(IM_WIDTH / 2 + wideSpace)) and scores[0][0] >= THRESHOLD:
                print("AGLZ: Backing up")
                back()
                movingForward = False                
            elif movingForward and primaryXMin == 0 and primaryXMax == 0:
                movingForward = False
                print('Starting Goldielocks pickup')
                print("Tripped Relay")
                relayTimer = relay()
                relayOn = 1
                print("Running motors for " + str(forwardTime) + " seconds.")
                motorTime = runMotorsNonBlocking()
                runningMotors = 1
                #runMotors(forwardTime)

            elif primaryXMax > int(IM_WIDTH / 2 + wideSpace) and scores[0][0] >= THRESHOLD:
                print('R')
                right()
                movingForward = False
            elif primaryXMin < int(IM_WIDTH / 2 - wideSpace) and scores[0][0] >= THRESHOLD and primaryx != -1:
                print('L')
                left()
                movingForward = False
            elif primaryXMin > int(IM_WIDTH / 2 - wideSpace) and primaryXMax < int(IM_WIDTH / 2 + wideSpace) and scores[0][0] >= THRESHOLD:
                print('F')
                forward()
                if primaryy > IM_HEIGHT * pickUpThresh:
                    movingForward = True
            elif time.time() - IdleTurnStatus < 2.5:
                print("idle NonBlocking Right")
                right(5)
            else:
                if PooplessFrameCount < GraceFrameCount:
                    PooplessFrameCount += 1
                    print("waiting to idle " + str(PooplessFrameCount))
                    stop()
                else:
                    print('I')
                    IdleTurnStatus = idle()
                    movingForward = False
                    #stop()

        if((currTime - motorTime >= forwardTime) and runningMotors):
            stop()
            runningMotors = 0
        elif runningMotors:
            print("Running Motors for:" + str(currTime - motorTime))

    # Check voltage every 60 frames (once a min)
    # if frameCount % 5 == 0:
    if time.time() - voltageTime > checkVoltageInt and ableToCheckVoltage and not auto and not manual:
        print("Checking Voltage")
        oldv = v
        oldm1 = m1
        oldm2 = m2
        v, m1, m2, voltageTime = voltage()
        if v == -1:
            v = oldv
            m1 = oldm1
            m2 = oldm2
        if v < exitVoltage:
            voltageStatus = -1
        elif v < lowVoltage:
            voltageStatus = 0
        else:
            voltageStatus = 1
        # print("Battery: " + str(v)  + "v")
        # print("Motor1 : " + str(m1) + "v")
        # print("Motor2 : " + str(m2) + "v")
        value = datetime.datetime.fromtimestamp(time.time())
        voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Battery: " + args.batteryNumCLA + ") | " + str(v) + "v\n")
        #voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor1)     | " + str(m1) + " amps\n")
        #voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Motor2)     | " + str(m2) + " amps\n")
        #voltageHistoryFile.write("\n")
        try:
            firebase.put('Pi/','Voltage', v)
        except:
            print("Error updating voltage")

    if voltageStatus == lowVoltage:
        print("WARNING: Low Voltage" + str(v))
        voltageHistoryFile.write("WARNING: Low Voltage" + str(v) + "\n")
    if voltageStatus == exitVoltage:
        print("CRITICAL: Voltage too low " + str(v))
        voltageHistoryFile.write("CRITICAL: Voltage too low " + str(v) + "\n")
        voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + " (Battery): " + str(v) + "v\n")
        voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + "  (Motor1): " + str(m1) + "v\n")
        voltageHistoryFile.write(value.strftime('%Y-%m-%d %H:%M:%S') + "  (Motor2): " + str(m2) + "v\n")
        voltageHistoryFile.write("\n")
        print("Exiting now.")
        exit()

    # Draw the center lines
    cv2.line(frame, (int(IM_WIDTH / 2 - wideSpace), 0), (int(IM_WIDTH / 2 - wideSpace), int(IM_HEIGHT)), (255, 255, 255), 5) #left
    cv2.line(frame, (int(IM_WIDTH / 2 + wideSpace), 0), (int(IM_WIDTH / 2 + wideSpace), int(IM_HEIGHT)), (255, 255, 255), 5) #right
    cv2.line(frame, (int(IM_WIDTH / 2 - wideSpace), int(IM_HEIGHT * pickUpThresh)), (int(IM_WIDTH / 2 + wideSpace), int(IM_HEIGHT * pickUpThresh)), (0, 255, 0), 5) #right
    cv2.line(frame, (int(IM_WIDTH / 2 - wideSpace), int(IM_HEIGHT * anitGLZone)), (0, int(IM_HEIGHT * anitGLZone)), (0, 0, 255), 5) #right
    cv2.line(frame, (int(IM_WIDTH / 2 + wideSpace), int(IM_HEIGHT * anitGLZone)), (IM_WIDTH, int(IM_HEIGHT * anitGLZone)), (0, 0, 255), 5) #right
    
    # Check to turn off relay
    elapsedTime = currTime - relayTimer
    if elapsedTime > fanTime and relayOn:
        relayTurnOff()
        relayOn = 0
        time.sleep(10)
        # Query data for loadcell 
        data = 0
        try:
            data = firebase.get('Pi/loadCell/',None)
        except:
             print("Error getting load cell data")
           
        if data == -1:
             weightOffSet = 0
             hx = LoadCellInit()
        print("Checking weight with offset", weightOffSet)
        lcWeight = LoadCell(hx, weightOffSet)
        # post new value to firebase
        try:
             firebase.put('Pi/','loadCell',lcWeight)
        except:
             print("Error posting load cell data to firebase")
        if lcWeight > maxWeight:
             print("SLEEP because im full")
             started = False
             waiting = False
             auto = False
             manual = False
             stop()
             
    # Display frame rate and draw to screen
    cv2.putText(frame, "FPS: {0:.2f}".format(frame_rate_calc),    (30,  50), font, 1, (255,255,0), 2, cv2.LINE_AA)
    #cv2.putText(frame, "Average FPS: {0:.2f}".format(averageFPS), (30, 150), font, 1, (255,255,0), 2, cv2.LINE_AA)

    cv2.imshow('Object detector', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

    rawCapture.truncate(0)

camera.close()
cv2.destroyAllWindows()

