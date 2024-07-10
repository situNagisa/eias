import time
import cv2
import serial
import serial.tools.list_ports
import logging
import os
import sys


def __open_port(port, baud_rate, timeout):
    def is_linux():
        return os.name == 'posix' and sys.platform.startswith('linux')

    # if is_linux():
    #     os.chmod(port, 0o666)
    return serial.Serial(port, baud_rate, timeout=timeout)


def find_char_device(verification_char, response_expected):
    # 列出所有串口设备
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        # logging.info(f"serial[{port}] checking {desc}...")

        try:
            # 打开串口
            ser = __open_port(port, 9600, timeout=1)
            ser.write(verification_char.encode())  # 发送验证字符
            response = ser.read(1)  # 读取一个字符
            # 如果找到匹配的设备，返回串口对象
            if response == response_expected:
                logging.info(f"char device[{port}] found!")
                return ser  # 只返回串口对象
        except serial.SerialException as e:
            logging.error(f"char device[{port}] open failed : {e}")

    logging.error(f"no char device found! verify={verification_char} response={response_expected}.")
    return None  # 如果没有找到设备，返回None


def find_servo():
    """
    枚举给定的串口列表，发送指令，并检查返回的数据是否符合协议格式。

    :return: 如果找到符合协议的设备，则返回这个串口对象；否则返回None。
    """
    port_list = serial.tools.list_ports.comports()
    cmd = bytearray([0x55, 0x55, 0x02, 0x0F])  # 定义指令，例如CMD_GET_BATTERY_VOLTAGE指令
    expected_frame_header = bytearray([0x55, 0x55])  # 期望的帧头
    expected_data_length = 4  # 期望的数据长度，例如返回电压值的指令应返回4个字节

    for port, desc, hwid in port_list:
        try:
            ser = __open_port(port, 9600, timeout=1)
            logging.debug(f"serial[{port}] checking {desc}...")
            ser.write(cmd)  # 发送指令
            time.sleep(0.3)
            # 等待并读取响应
            response = ser.read(ser.in_waiting or 1)
            formatted_bytes = ' '.join(format(b, '02X') for b in response)

            logging.debug(f'serial[{port}] response {formatted_bytes}')

            # 检查响应是否符合期望的格式
            if __check_response_format(response, expected_frame_header, expected_data_length):
                logging.info(f"servo[{port}] found!")
                return ser  # 直接返回串口对象，不关闭
        except serial.SerialException as e:
            logging.error(f"servo[{port}] open failed : {e}")

    logging.error("no servo device found.")
    return None


def __check_response_format(response, frame_header, data_length):
    """
    检查响应数据是否符合期望的协议格式。

    :param response: 从设备接收到的响应数据。
    :param frame_header: 期望的帧头。
    :param data_length: 期望的数据长度。
    :return: 如果响应符合格式，则返回True；否则返回False。
    """
    # 检查帧头和数据长度
    return response.startswith(frame_header) and len(response) == data_length + len(frame_header)


def find_camera_capture():
    max_index_to_check = 10  # Maximum index to check for camera
    for index in range(max_index_to_check):
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            logging.info(f"camera capture found! index: {index}")
            return cap
    # If no camera is found
    logging.error("no camera capture found")
    return None
