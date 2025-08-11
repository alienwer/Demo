'''
Author: LK
Date: 2025-02-16 00:55:09
LastEditTime: 2025-07-18 16:11:31
LastEditors: LK
FilePath: /Demo/app/control/serial_comm.py
'''
import serial
import time
from serial.tools import list_ports
from typing import Optional

class SerialCommunication:
    def __init__(self):
        self.serial_port: Optional[serial.Serial] = None
        self._is_connected = False

    def get_available_ports(self) -> list:
        """获取系统中所有可用的串口设备列表"""
        return [port.device for port in list_ports.comports()]

    def connect(self, port: str, baudrate: int = 115200) -> bool:
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=1
            )
            self._is_connected = True
            return True
        except Exception as e:
            print(f"连接失败: {str(e)}")
            return False

    def disconnect(self) -> None:
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self._is_connected = False

    def is_connected(self) -> bool:
        return self._is_connected

    def send_command(self, command: str) -> bool:
        if not self.is_connected or not self.serial_port:
            return False
        try:
            self.serial_port.write(command.encode())
            return True
        except Exception as e:
            print(f"发送命令失败: {str(e)}")
            return False

    def read_response(self) -> Optional[str]:
        if not self.is_connected or not self.serial_port:
            return None
        try:
            if self.serial_port.in_waiting:
                return self.serial_port.readline().decode().strip()
            return None
        except Exception as e:
            print(f"读取响应失败: {str(e)}")
            return None