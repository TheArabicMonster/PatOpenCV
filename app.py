import cv2
import numpy as np
import onnxruntime as ort 

opts = ort.SessionOptions()
opts.intra_op_num_threads = 4 #nombre max de tthreads

session = ort.InferenceSession("ultra_light_320.onnx", opts)