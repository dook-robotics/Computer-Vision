# Check failed: s.ok() Found StridedSlice as non-selected output from Switch, but only Merge supported.
# Control flow ops like Switch and Merge are not generally supported. We are working on fixing this,
# please see the Github issue at https://github.com/tensorflow/tensorflow/issues/28485.

import tensorflow as tf

graph_def_file = "D:/Models/poop/inference_graphs/ssd_mobilenet_v2.5.7/frozen_inference_graph.pb"
input_arrays = ["image_tensor"]
output_arrays = ["detection_scores","detection_boxes","detection_classes","num_detections"]

converter = tf.lite.TFLiteConverter.from_frozen_graph(
        graph_def_file, input_arrays, output_arrays, input_shapes={"image_tensor":[1,300,300,3]})
converter.experimental_new_converter = True  # Add this line
tflite_model = converter.convert()
open("converted_model.tflite", "wb").write(tflite_model)
