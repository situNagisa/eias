import json
import websocket
import threading
from eye import Eye  # 假设EyeEmulator类在eye_emulator.py文件中
from arm import Arm
import device
import logging


# 定义WebSocket客户端类
class Application:
    ws: websocket.WebSocketApp = None
    left_eye: Eye = None
    right_eye: Eye = None
    arm: Arm = None
    is_open: bool = False

    def __init__(self, url):
        self.url = url

    def create_device(self, device_id, finder, creator):
        self_device = getattr(self, device_id)
        if self_device is None or not self_device.is_active:
            found_device = finder()
            if found_device is not None:
                setattr(self, device_id, creator(found_device))

    def create_left_eye(self):
        self.create_device('left_eye', lambda: device.find_char_device('n', b'b'), Eye)

    def create_right_eye(self):
        self.create_device('right_eye', lambda: device.find_char_device('n', b'6'), Eye)

    def create_arm(self):
        self.create_device('arm', device.find_servo, Arm)

    def action(self, device_id, method):
        self_device = getattr(self, device_id)
        if self_device is None:
            getattr(self, 'create_' + device_id)()

        self_device = getattr(self, device_id)
        if self_device is None:
            return

        is_active = self_device.is_active
        if not is_active:
            return

        function = getattr(self_device, method)
        function()
        if not self_device.is_active:
            setattr(self, device_id, None)

    def on_open(self, ws):
        def run(*args):
            logging.info("WebSocket connection opened.")
            # 可以在这里发送一些初始化消息到服务端
            ws.send("Hello Server!")

        threading.Thread(target=run).start()

        self.is_open = True

    def on_message(self, ws, message):
        logging.info(f"received message from server:{message}")
        topic = ""
        msg = ""

        try:
            data = json.loads(message)
            topic = data.get('topic')
            msg = data.get('msg')
        except json.JSONDecodeError as e:
            logging.exception(f"Failed to decode JSON:{e}")

        if topic == 'eye':
            if msg == 'normal':
                self.action('left_eye', 'normal')
                self.action('right_eye', 'normal')
                self.send_message(topic, message)
            elif msg == 'blink':
                self.action('left_eye', 'blink')
                self.action('right_eye', 'blink')
                self.send_message(topic, message)
            elif msg == 'star':
                self.action('left_eye', 'star_struck')
                self.action('right_eye', 'star_struck')
                self.send_message(topic, message)
            elif msg == 'momomo':
                self.action('left_eye', 'momomo')
                self.action('right_eye', 'momomo')
                self.send_message(topic, message)
            elif msg == 'smile':
                self.action('left_eye', 'smile')
                self.action('right_eye', 'smile')
                self.send_message(topic, message)
        elif topic == 'hand':
            if msg == 'raise':
                self.action('arm', 'raise_hand')
                self.send_message(topic, message)
            elif msg == 'lower':
                self.action('arm', 'lower_hand')
                self.send_message(topic, message)
            elif msg == 'fast_wave':
                self.action('arm', 'fast_wave')
                self.send_message(topic, message)
            elif msg == 'slow_wave':
                self.action('arm', 'slow_wave')
                self.send_message(topic, message)

    def on_error(self, ws, error):
        logging.exception(f"{error}")

    def on_close(self, ws, a, b):
        logging.info("WebSocket connection closed.")
        self.is_open = False

    def async_run(self):
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        thread = threading.Thread(target=self.ws.run_forever)
        thread.daemon = True  # 设置为守护线程，这样主程序结束时线程也会结束
        thread.start()
        logging.info(f"starting websocket, try connect {self.url}")
        return thread

    def send_message(self, topic, message):
        data = {
            'topic': topic,
            'msg': message
        }
        try:
            self.ws.send(json.dumps(data))
        except Exception as e:
            logging.exception(e)
        logging.info(f"sent topic: {topic}, message: {message}")
