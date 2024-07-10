import numpy as np
import cv2
import json

from .acllite_resource import AclLiteResource
from .acllite_model import AclLiteModel
from .acllite_imageproc import AclLiteImageProc
from .acllite_image import AclLiteImage
from .label import labels
from .acllite_logger import log_error, log_info


class sampleYOLOV7(object):
    '''load the model, and do preprocess, infer, postprocess'''
    def __init__(self, model_path, model_width, model_height):
        self.model_path = model_path
        self.model_width = model_width
        self.model_height = model_height

    def init_resource(self):
        # initial acl resource, create image processor, create model
        self._resource = AclLiteResource()
        self._resource.init()
    
        self._dvpp = AclLiteImageProc(self._resource) 
        self._model = AclLiteModel(self.model_path)

    def preprocess(self, frame):
        # resize frame, keep original image
        self.src_image = frame
        self.resized_image = cv2.resize(frame, (self.model_width, self.model_height))

    def infer(self):
        # infer frame
        image_info = np.array([640, 640,
                            640, 640],
                            dtype=np.float32)
        self.result = self._model.execute([self.resized_image, image_info])
    
    def postprocess(self):
        box_num = self.result[1][0, 0]
        box_info = self.result[0].flatten()

        height, width, _ = self.src_image.shape 
        scale_x = width / self.model_width
        scale_y = height / self.model_height

        colors = [0, 0, 255]
        data_list = []  # 创建一个空列表来存储数据
        # draw the boxes in original image
        for n in range(int(box_num)):
            ids = int(box_info[5 * int(box_num) + n])
            score = box_info[4 * int(box_num) + n]
            label = labels[ids] + ":" + str("%.2f" % score)
            top_left_x = box_info[0 * int(box_num) + n] * scale_x
            top_left_y = box_info[1 * int(box_num) + n] * scale_y
            bottom_right_x = box_info[2 * int(box_num) + n] * scale_x
            bottom_right_y = box_info[3 * int(box_num) + n] * scale_y
            cv2.rectangle(self.src_image, (int(top_left_x), int(top_left_y)),
                        (int(bottom_right_x), int(bottom_right_y)), colors)
            p3 = (max(int(top_left_x), 15), max(int(top_left_y), 15))
            position = [int(top_left_x), int(top_left_y), int(bottom_right_x), int(bottom_right_y)]
            cv2.putText(self.src_image, label, p3, cv2.FONT_ITALIC, 0.6, colors, 1)
            data_list.append({
                'tag': labels[ids],
                'percent': str("%.2f" % score),
                'lx': int(top_left_x),
                'ly': int(top_left_y),
                'rx': int(bottom_right_x),
                'ry': int(bottom_right_y),
            })
        return data_list

    def release_resource(self):
        # release resource includes acl resource, data set and unload model
        del self._resource
        del self._dvpp
        del self._model
        del self.resized_image

def find_camera_index():
    max_index_to_check = 10  # Maximum index to check for camera
    for index in range(max_index_to_check):
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            cap.release()
            return index
    # If no camera is found
    raise ValueError("No camera found.")



if __name__ == '__main__':
    model_path = '../model/yolov5s_rgb.om'
    model_width = 640
    model_height = 640
    model = sampleYOLOV7(model_path, model_width, model_height)
    model.init_resource()

    camera_index = find_camera_index()
    cap = cv2.VideoCapture(camera_index)
    cv2.namedWindow('out', cv2.WINDOW_NORMAL)
    while True:
        ret, frame = cap.read()
        if not ret:  
            print("Can't receive frame (stream end?). Exiting ...")  
            break  
        model.preprocess(frame)
        model.infer()
        model.postprocess()
        # cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  
            break  
    cap.release()  
    cv2.destroyAllWindows()
    
    model.release_resource()
