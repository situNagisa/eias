cd model
wget https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/003_Atc_Models/yolov5s/yolov5s_nms.onnx --no-check-certificate
wget https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/003_Atc_Models/yolov5s/aipp_rgb.cfg --no-check-certificate
atc --model=yolov5s_nms.onnx --framework=5 --output=yolov5s_rgb --input_shape="images:1,3,640,640;img_info:1,4"  --soc_version=Ascend310B4  --insert_op_conf=aipp_rgb.cfg