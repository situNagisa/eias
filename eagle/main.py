import threading
from application import Application
import logging
import sys
import camera
import configparser
import json


def main():
    config = configparser.ConfigParser()
    config.read('eias_eagle.ini')

    output_file = None

    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    logging.basicConfig(
        # 日志输出位置
        filename=output_file,
        # 日志文件打开方式
        filemode="w",
        # 日志消息格式
        format='[%(asctime)s] [%(levelname)s] [%(module)s::%(name)s]:  %(message)s',
        # 时间格式
        datefmt='%Y-%m-%d %H:%M:%S %p',
        level=logging.DEBUG,
    )

    logging.info("hello nagisa")

    url = config.get("websocket", "url", fallback='ws://127.0.0.100:9000/websocket/100')
    # ws://192.168.0.100:9000/websocket/100
    # ws://127.0.0.1:8443/v1
    # ws_client = Application(url='ws://127.0.0.1:8443/v1')
    ws_client = Application(url=url)
    if not config.has_section('websocket'):
        config.add_section('websocket')
    config.set('websocket', 'url', url)

    def dont_stop():
        thread = ws_client.async_run()
        while True:
            thread.join()
            thread = ws_client.async_run()

    dont_stop_thread = threading.Thread(target=dont_stop)
    dont_stop_thread.daemon = True  # 设置为守护线程，这样主程序结束时线程也会结束
    dont_stop_thread.start()

    om_file = config.get("model", "om_file", fallback='./model/yolov5s_rgb.om')
    camera_model = camera.Camera(om_file, 640, 640)
    if not config.has_section('model'):
        config.add_section('model')
    config.set('model', 'om_file', om_file)

    with open('eias_eagle.ini', 'w') as configfile:
        config.write(configfile)

    while True:
        if not ws_client.is_open:
            continue

        msg = camera_model.get_labels()
        # msg = ""
        if len(msg) > 0:
            ws_client.send_message("image", json.dumps(msg, ensure_ascii=False))

    dont_stop_thread.join()


if __name__ == "__main__":
    main()
