## Object Detection using TF Model (WebCam) ##
## Not Pi Compatible                        ##

# Authors:
#   Mikian Musser
#   Austin Janushan

# Usage
#   python Object_detection_webcam.py

# Description
#   Script to test TF models and tracking algs before ported to Pi

# Imports
import os
import cv2
import sys
import numpy as np
import tensorflow as tf
from utils import label_map_util
from utils import visualization_utils as vis_util

# Constants
THRESHOLD = 0.6

# Number of classes the object detector can identify
NUM_CLASSES = 1

# File containing the model to use
# MODEL_NAME = 'inference_graph' # Default
MODEL_NAME = 'ssd_mobilenet_v2_coco_inference_graph'

# Get file paths
CWD_PATH = os.getcwd()
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')
PATH_TO_LABELS = os.path.join(CWD_PATH,'training','labelmap.pbtxt')

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

# Init webcam
video = cv2.VideoCapture(0)

# Get height/width
width = video.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
height = video.get(cv2.CAP_PROP_FRAME_HEIGHT) # float

# Init Tracker and the tracker's bounding box
tracker = cv2.TrackerMOSSE_create()
initBB = None

while(True):

    # Get frame from camera
    ret, frame = video.read()
    frame_expanded = np.expand_dims(frame, axis=0)

    # Run the frame through the TF model
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: frame_expanded})

    # Draw significant bounding boxes
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
        if(scores[0][index] >= THRESHOLD):
            ymin = int((box[0]*height))
            xmin = int((box[1]*width))
            ymax = int((box[2]*height))
            xmax = int((box[3]*width))
            Result = np.array(frame[ymin:ymax,xmin:xmax])
            cv2.circle(frame,(int((xmin + xmax)/2),int((ymin + ymax)/2)),5,(0,255,0),-1)

    # Draw the center lines
    cv2.line(frame, (int(width/2-25),0), (int(width/2-25),int(height)), (0,0,255),5) #left
    cv2.line(frame, (int(width/2+25),0), (int(width/2+25),int(height)), (0,0,255),5) #right

    # Get the 'primary' card's x value
    primaryx = int((boxes[0][0][1]*width + boxes[0][0][3]*width)/2)

    # If score is high enough, track object
    if(scores[0][0] >= 0.9):
        initBB = (
            boxes[0][0][1]*width,
            boxes[0][0][0]*height,
            boxes[0][0][3]*width-boxes[0][0][1]*width,
            boxes[0][0][2]*height-boxes[0][0][0]*height)
        tracker.init(frame, initBB)
    else:
        tracker = cv2.TrackerMOSSE_create()

    # Draw trackers bounding object and update tracker
    if(initBB is not None):
        (success, box) = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
            (0, 255, 0), 2)

    # Send instructions
    if(primaryx > int(width/2+25) and scores[0][0] >= THRESHOLD):
        print("Move Left")
    elif(primaryx < int(width/2-25) and scores[0][0] >= THRESHOLD):
        print("Move Right")
    elif(primaryx > int(width/2-25) and primaryx < int(width/2+25) and scores[0][0] >= THRESHOLD):
        print("Move forrward, suck")

    cv2.imshow('Object detector', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

# Clean up
video.release()
cv2.destroyAllWindows()
