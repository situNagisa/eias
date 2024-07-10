import threading
import logging
import serial


class Eye:
    ser: serial.Serial = None
    is_active: bool = True

    def __init__(self, serial_device):
        self.ser = serial_device
        if not self.ser.isOpen():
            self.ser.open()

    def __send_command_callback(self, command):
        try:
            self.ser.write(command)
            logging.info(f"command '{command}' sent to the eye device.")
        except serial.SerialException:
            self.is_active = False
            logging.exception("Serial port error")

    def send_command(self, command):
        thread = threading.Thread(target=self.__send_command_callback, args=(command,))
        thread.daemon = True  # 设置为守护线程，这样主程序结束时线程也会结束
        thread.start()

    def normal(self):
        """模拟正常状态"""
        self.send_command(b'a')

    def blink(self):
        """模拟眨眼状态"""
        self.send_command(b'b')

    def star_struck(self):
        """模拟星星眼状态"""
        self.send_command(b'c')

    def momomo(self):
        """模拟'momomo'状态"""
        self.send_command(b'd')

    def smile(self):
        """模拟'momomo'状态"""
        self.send_command(b'e')

    def close(self):
        self.ser.close()
        logging.info(f"serial port closed")
