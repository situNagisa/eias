import threading
import logging
import serial


class Arm:
    ser: serial = None
    current_wave_event: threading.Event = None
    current_wave_thread: threading.Thread = None
    changing_wave_action: bool = False
    is_active: bool = True

    def __init__(self, serial_device):
        self.ser = serial_device
        if not self.ser.isOpen():
            self.ser.open()

    def send_servo_move(self, servo_count, time_ms, servo_angles):
        length = (servo_count * 3) + 5
        time_low = time_ms & 0xFF
        time_high = (time_ms >> 8) & 0xFF

        frame = bytearray([0x55, 0x55, length, 3])
        frame += bytearray([servo_count])
        frame += bytearray([time_low, time_high])

        for servo_id, angle in servo_angles:
            angle = int(angle * 2000 / 180 + 500)
            frame += bytearray([servo_id, angle & 0xFF, (angle >> 8) & 0xFF])

        self.ser.write(frame)
        logging.info(f"Servo move command sent for {servo_angles} over {time_ms} ms.")

    def try_send_servo_move(self, servo_count, time_ms, servo_angles):
        try:
            self.send_servo_move(servo_count, time_ms, servo_angles)
        except serial.SerialException:
            self.is_active = False
            logging.exception("arm write fail!")
            return False
        return True

    def lower_hand(self):
        # 抬手到最高点
        self.kill_current_thread()
        self.ser.reset_input_buffer()
        self.try_send_servo_move(1, 500, [(1, 50)])  # 假设90度是最高


    def raise_hand(self):
        # 垂手到最低点
        self.kill_current_thread()
        self.try_send_servo_move(1, 500, [(1, 0)]) # 假设0度是最低

    def kill_current_thread(self):
        if self.current_wave_thread and self.current_wave_thread.is_alive():
            self.changing_wave_action = True
            self.current_wave_event.set()
            self.current_wave_thread.join()
            self.changing_wave_action = False

    def wave(self, speed):
        self.kill_current_thread()

        def wave_inner(event):
            try:
                while self.ser.isOpen() and not self.changing_wave_action:
                    if not self.try_send_servo_move(1, speed, [(1, 80)]):
                        break
                    # 等待事件被设置或超时
                    event.wait(speed / 1000.0)
                    if not self.ser.isOpen() and not self.changing_wave_action:  # 检查串口是否已关闭
                        break
                    if not self.try_send_servo_move(1, speed, [(1, 0)]):
                        break
                    # 再次等待事件被设置或超时
                    event.wait(speed / 1000.0)
            except KeyboardInterrupt:
                logging.info("Wave interrupted by keyboard.")

        self.current_wave_event = threading.Event()  # 创建一个事件对象
        self.current_wave_thread = threading.Thread(target=wave_inner, args=(self.current_wave_event,))
        self.current_wave_thread.start()

    def fast_wave(self):
        # 快速挥手
        self.wave(250)  # 使用较短的时间间隔表示快速

    def slow_wave(self):
        # 慢速挥手
        self.wave(500)  # 使用较长的时间间隔表示慢速

    def close(self):
        if self.ser.isOpen():
            self.ser.close()
            logging.info("Serial port closed.")
