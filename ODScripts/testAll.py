import os
import cv2
import sys
import glob
import numpy as np
import tensorflow as tf
from utils import label_map_util
from utils import visualization_utils as vis_util

# Detection Threshold
THRESH = 0.5

# Directories and Models
BASE   = "D:/Models/poop/inference_graphs"
LABELS = "D:/Models/poop/labelmap.pbtxt"
MODEL_NAMES  =  [
                "faster_rcnn_inception_v2_pets_v1",
                "ssd_mobilenet_v2_0052_v1",
                "ssd_mobilenet_v2_0037_v2",
                "ssd_mobilenet_v2_0037_v3",
                "ssd_mobilenet_v2_v4"
                ]

# Choose a model
MODEL_NAME = MODEL_NAMES[0]
FROZEN_INFERENCE_GRAPH = os.path.join(BASE,MODEL_NAME,'frozen_inference_graph.pb').replace("\\","/")

# Image Directories
PATH_TO_TRAIN_IMAGES = "D:/Database/reduced/train/*.jpg"
PATH_TO_TEST_IMAGES  = "D:/Database/reduced/test/*.jpg"
OUTPUT               = "D:/Database/tests/*"
NUM_CLASSES          = 1

# Grab all images
IMAGES = glob.glob(PATH_TO_TRAIN_IMAGES) + glob.glob(PATH_TO_TEST_IMAGES)

# Clean output folder
OUTPUT_FILES = glob.glob(OUTPUT)
for file in OUTPUT_FILES:
    os.remove(file)

# Load labels and categories
label_map = label_map_util.load_labelmap(LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load tensorflow model
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(FROZEN_INFERENCE_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
    sess = tf.Session(graph=detection_graph)

# Define inputs and outputs
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Run the model on every image
for image in IMAGES:

    # Get image name
    image = image.replace("\\","/")
    name = image.split("/")
    name = name[len(name) - 1]

    # Load current image
    image = cv2.imread(image)
    image_expanded = np.expand_dims(image, axis=0)

    # Run object detection
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: image_expanded})

    # Draw boxes
    vis_util.visualize_boxes_and_labels_on_image_array(
        image,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=2,
        min_score_thresh=THRESH)

    # Write to output
    cv2.imwrite('D:/Database/tests/test' + name, image)
    print("Processed:", name)
