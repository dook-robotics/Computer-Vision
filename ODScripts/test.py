import os
import cv2
import sys
import glob
import numpy as np
import tensorflow as tf
from utils import label_map_util
from utils import visualization_utils as vis_util

MODEL_NAME = "ssd_mobilenet_v2_0037_v3"

BASE = "D:/Models/poop/inference_graphs"
PATH_TO_LABELS = "D:/Models/poop/labelmap.pbtxt"
FROZEN_INFERENCE_GRAPH = os.path.join(BASE,MODEL_NAME,'frozen_inference_graph.pb').replace("\\","/")
PATH_TO_IMAGES = "D:/Database/reduced/test/*.jpg"
PATH_TO_TESTS = "D:/Database/tests/*"
IMAGES = glob.glob(PATH_TO_IMAGES)
NUM_CLASSES = 1

filelist = glob.glob(PATH_TO_TESTS)
for f in filelist:
    os.remove(f)

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(FROZEN_INFERENCE_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

for image in IMAGES:
    image = image.replace("\\","/")
    name = image.split("/")
    name = name[len(name) - 1]

    image = cv2.imread(image)
    image_expanded = np.expand_dims(image, axis=0)

    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: image_expanded})

    vis_util.visualize_boxes_and_labels_on_image_array(
        image,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8,
        min_score_thresh=0.5)

    cv2.imwrite('D:/Database/tests/test' + name, image)
    print("Processed:", name)
