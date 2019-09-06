# import tensorflow as tf
#
# converter = tf.lite.TFLiteConverter.from_saved_model("D:/Computer-Vision/models/cardModels/ssd_mobilenet_v2_coco_2018/ssdModel_v2/saved_model")
# tflite_model = converter.convert()
# open("converted_model.tflite", "wb").write(tflite_model)

import tensorflow as tf

graph_def_file = "D:/Computer-Vision/models/cardModels/ssd_mobilenet_v2_coco_2018/ssdModel_v2/frozen_inference_graph.pb"
input_arrays = ["image_tensor"]
output_arrays = ["detection_scores","detection_boxes","detection_classes","num_detections"]

converter = tf.lite.TFLiteConverter.from_frozen_graph(
        graph_def_file, input_arrays, output_arrays,input_shapes={"image_tensor":[1,304,304,3]})
tflite_model = converter.convert()
open("converted_model.tflite", "wb").write(tflite_model)
