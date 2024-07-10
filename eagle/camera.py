from acllite import YOLOV5USBCamera as yolo
import logging
import cv2
import device
import time

class Camera(object):
    model: yolo.sampleYOLOV7 = None
    capture: cv2.VideoCapture = None

    def __init__(self, model_path, width, height):
        self.model = yolo.sampleYOLOV7(model_path, width, height)
        self.model.init_resource()

    def create_capture(self):
        while True:
            if self.capture is None:
                self.capture = device.find_camera_capture()
            if self.capture is None:
                continue
            success, _ = self.capture.read()
            if not success:
                self.capture = None
            break

    def get_labels(self):
        self.create_capture()
        ret, frame = self.capture.read()
        if not ret:
            logging.warning("can't receive frame (stream end?). exiting ...")
            return ""
        self.model.preprocess(frame)
        self.model.infer()
        return self.model.postprocess()

