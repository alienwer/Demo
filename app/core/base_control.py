from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union, Callable, Tuple
import threading
import logging
import time
import subprocess
import socket

from ...config.constants import RobotState, GripperState, MotionPrimitive
from ...config.settings import ROBOT_CONFIG


class BaseRobotControl(ABC):
    """机器人控制抽象基类"""
    
    def __init__(self, robot_id: str = "Rizon4-062468"):
        self.robot_id = robot_id
        self._state = RobotState.DISCONNECTED
        self._lock = threading.RLock()
        self._running = False
        self._logger = logging.getLogger(__name__)
        
    @abstractmethod
    def connect(self) -> bool:
        """连接机器人"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """断开连接"""
        pass
    
    @abstractmethod
    def enable(self) -> bool:
        """使能机器人"""
        pass
    
    @abstractmethod
    def disable(self) -> bool:
        """禁用机器人"""
        pass
    
    @abstractmethod
    def get_state(self) -> RobotState:
        """获取机器人状态"""
        pass
    
    @abstractmethod
    def get_joint_positions(self) -> List[float]:
        """获取关节位置"""
        pass
    
    @abstractmethod
    def get_joint_velocities(self) -> List[float]:
        """获取关节速度"""
        pass
    
    @abstractmethod
    def get_joint_torques(self) -> List[float]:
        """获取关节力矩"""
        pass
    
    @abstractmethod
    def get_tcp_pose(self) -> List[float]:
        """获取TCP位姿"""
        pass
    
    @abstractmethod
    def move_joint(self, target_positions: List[float], 
                  speed: float = 1.0, 
                  primitive: MotionPrimitive = MotionPrimitive.JOINT_MOVE) -> bool:
        """关节运动"""
        pass
    
    @abstractmethod
    def move_linear(self, target_pose: List[float], 
                   speed: float = 1.0, 
                   primitive: MotionPrimitive = MotionPrimitive.LINEAR_MOVE) -> bool:
        """直线运动"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """停止运动"""
        pass
    
    @abstractmethod
    def get_diagnostics(self) -> Dict[str, Any]:
        """获取诊断信息"""
        pass
    
    def check_network_connection(self, robot_ip: str = "192.168.2.100", 
                               timeout: int = 3) -> Tuple[bool, Optional[float]]:
        """检查与机器人的网络连接状态
        输入: robot_ip - 机器人IP地址, timeout - 超时时间(秒)
        输出: (连接状态, 延迟时间ms) - 连接成功返回(True, 延迟), 失败返回(False, None)
        """
        try:
            # 尝试ping机器人IP
            result = subprocess.run(
                ["ping", "-c", "1", "-W", str(timeout * 1000), robot_ip],
                capture_output=True,
                text=True,
                timeout=timeout + 1
            )
            
            if result.returncode == 0:
                # 提取延迟信息
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if "time=" in line:
                        time_part = line.split("time=")[1].split()[0]
                        latency = float(time_part)
                        return True, latency
                return True, None
            else:
                return False, None
                
        except subprocess.TimeoutExpired:
            return False, None
        except Exception as e:
            self._logger.warning(f"网络检查失败: {e}")
            return False, None
    
    def check_tcp_connection(self, robot_ip: str = "192.168.2.100", 
                           port: int = 8080, timeout: int = 3) -> bool:
        """检查TCP连接到机器人
        输入: robot_ip - 机器人IP地址, port - 端口号, timeout - 超时时间(秒)
        输出: 连接成功返回True, 失败返回False
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((robot_ip, port))
            sock.close()
            
            return result == 0
                
        except Exception as e:
            self._logger.warning(f"TCP连接检查失败: {e}")
            return False