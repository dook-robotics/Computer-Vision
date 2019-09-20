import tensorflow as tf
import os
# # from utils import label_map_util
# # from utils import visualization_utils as vis_util
#
# # PATH_TO_CKPT = os.path.join("C:/Users/bobar/Documents/GitHub/Models/poop/models/ssd_mobilenet_v2_0037_v2/ssd_mobilenet_v2_0037_v2/frozen_inference_graph.pb")
# PATH_TO_CKPT = os.path.join("C:/Users/bobar/Documents/GitHub/Models/poop/inference_graphs/faster_rcnn_inception_v2_pets_v1/frozen_inference_graph.pb")
# # PATH_TO_CKPT = os.path.join("C:/Users/bobar/Documents/GitHub/Models/poop/models/ssd_mobilenet_v2_0037_v2/ssd_mobilenet_v2_0037_v2/saved_model/saved_model.pb")
#
# # Path to label map file
# ################################ CHANGE ################################
# PATH_TO_LABELS = os.path.join("C:/Users/bobar/Documents/GitHub/Models/poop/models/ssd_mobilenet_v2_0037_v2/labelmap.pbtxt")
# ################################ CHANGE ################################
#
# # Number of classes the object detector can identify
# ################################ CHANGE ################################
# NUM_CLASSES = 1
# ################################ CHANGE ################################
#
# # Load labels.
# # label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
# # categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
# # category_index = label_map_util.create_category_index(categories)
#
# # Load the tf model
# detection_graph = tf.Graph()
# with detection_graph.as_default():
#     od_graph_def = tf.GraphDef()
#     with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
#         serialized_graph = fid.read()
#         od_graph_def.ParseFromString(serialized_graph)
#         print("here")
#         tf.import_graph_def(od_graph_def, name='')
#     sess = tf.Session(graph=detection_graph)
#
#
# # with tf.Session() as sess:
#     # Input tensor is the image
#     image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
#     # Output tensors are the detection boxes, scores, and classes
#     # Each box represents a part of the image where a particular object was detected
#     detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
#
#     # Each score represents level of confidence for each of the objects.
#     # The score is shown on the result image, together with the class label.
#     detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
#     detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
#
#     # Number of objects detected
#     num_detections = detection_graph.get_tensor_by_name('num_detections:0')
#     print([image_tensor])
#     print([detection_boxes,detection_scores,detection_classes,num_detections])
#     # with detection_graph.as_default():
#     print("test")
#     sess.run(tf.compat.v1.global_variables_initializer())
#     converter = tf.lite.TFLiteConverter.from_session(sess, [image_tensor], [detection_boxes,detection_scores,detection_classes,num_detections])
#     tflite_model = converter.convert()
#     # open("converted_model.tflite", "wb").write(tflite_model)

# PATH_TO_CKPT = os.path.join("C:/Users/bobar/Documents/GitHub/Models/poop/inference_graphs/ssd_mobilenet_v2_0037_v2/saved_model/")
PATH_TO_CKPT = os.path.join("C:/Users/bobar/Desktop/mn1/saved_model/")
converter = tf.lite.TFLiteConverter.from_saved_model(PATH_TO_CKPT, input_shapes={"image_tensor" : [1, 640, 640, 3]})
tflite_model = converter.convert()
