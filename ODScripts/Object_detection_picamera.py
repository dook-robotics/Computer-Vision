## Object Detection using TF Model PiCam ##

# Authors:
#   Mikian Musser
#   Austin Janushan

# Usage
#   python Object_detection_picamera.py

# Description
#   Script to run tf model on the Pi

# Imports
import os
import cv2
import argparse
import sys
import numpy as np
import tensorflow as tf
from picamera.array import PiRGBArray
from picamera import PiCamera
from utils import label_map_util
from utils import visualization_utils as vis_util

THRESHOLD = 0.6

# Set up camera constants
# We can use smaller resolution for faster frame rates
IM_WIDTH = 1280
IM_HEIGHT = 720
#IM_WIDTH = 640
#IM_HEIGHT = 480

# Default camera is picam
camera_type = 'picamera'

sys.path.append('..') # This might be depracated, check once on pi

# File containing the model to use
################################ CHANGE ################################
#MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09' #Default
#MODEL_NAME = 'ssd_mobilenet_v1_coco_2018' # test card on mobile
MODEL_NAME = 'ssd_mobilenet_v2_coco_2018' # test card on mobile
#MODEL_NAME = 'card'
################################ CHANGE ################################

# Get file paths
CWD_PATH = os.getcwd()
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
################################ CHANGE ################################
#PATH_TO_LABELS = os.path.join(CWD_PATH,'data','mscoco_label_map.pbtxt')
PATH_TO_LABELS = os.path.join(CWD_PATH,'data', 'cardssd_labelmap.pbtxt')
#PATH_TO_LABELS = os.path.join(CWD_PATH,'data','labelmap.pbtxt')
################################ CHANGE ################################

# Number of classes the object detector can identify
################################ CHANGE ################################
#NUM_CLASSES = 90
NUM_CLASSES = 1
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
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# Init Tracker and the tracker's bounding box
# tracker = cv2.TrackerMOSSE_create()
# initBB = None

# Initialize Picamera and grab reference to the raw capture
camera = PiCamera()
camera.resolution = (IM_WIDTH,IM_HEIGHT)
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=(IM_WIDTH,IM_HEIGHT))
rawCapture.truncate(0)

for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    t1 = cv2.getTickCount()

    frame = np.copy(frame1.array)
    frame.setflags(write=1)
    frame_expanded = np.expand_dims(frame, axis=0)

    # Run the frame through the TF model
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

    # For every box, find the center, draw a dot
    for index, box in enumerate(np.squeeze(boxes)):
        ymin = int((box[0]*IM_HEIGHT))
        xmin = int((box[1]*IM_WIDTH))
        ymax = int((box[2]*IM_HEIGHT))
        xmax = int((box[3]*IM_WIDTH))
        Result = np.array(frame[ymin:ymax,xmin:xmax])
        if(scores[0][index] >= THRESHOLD):
            cv2.circle(frame,(int((xmin + xmax)/2),int((ymin + ymax)/2)),5,(0,255,0),-1)

    # Draw the center lines
    cv2.line(frame, (int(IM_WIDTH/2-25),0), (int(IM_WIDTH/2-25),int(IM_HEIGHT)), (0,0,255),5) #left
    cv2.line(frame, (int(IM_WIDTH/2+25),0), (int(IM_WIDTH/2+25),int(IM_HEIGHT)), (0,0,255),5) #right

    # Get the 'primary' card's x value
    # primaryx = int((boxes[0][0][1]*IM_WIDTH + boxes[0][0][3]*IM_WIDTH)/2)

    # Send instructions
    # if(primaryx > int(width/2+25) and scores[0][0] >= THRESHOLD):
    #     print("Move Left")
    # elif(primaryx < int(width/2-25) and scores[0][0] >= THRESHOLD):
    #     print("Move Right")
    # elif(primaryx > int(width/2-25) and primaryx < int(width/2+25) and scores[0][0] >= THRESHOLD):
    #     print("Move forrward, suck")

    # Calc Frame Rate
    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc = 1/time1

    # Display frame rate and draw to screen
    cv2.putText(frame,"FPS: {0:.2f}".format(frame_rate_calc),(30,50),font,1,(255,255,0),2,cv2.LINE_AA)
    cv2.imshow('Object detector', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

    rawCapture.truncate(0)

camera.close()
cv2.destroyAllWindows()
