"""
硬件机器人控制实现 - 基于Flexiv RDK的机器人控制
"""

import numpy as np
import threading
import logging
import time
from typing import List, Optional, Dict, Any, Union, Callable

from PyQt5.QtCore import QObject
from ...utils.core.signal_manager import get_signal_manager, SignalType, SignalData

from .base_control import BaseRobotControl
from ...config.constants import RobotState, MotionPrimitive
from ...config.settings import ROBOT_CONFIG

# Flexiv RDK导入
FLEXIV_AVAILABLE = False
try:
    from flexivrdk import Robot, Model, Mode, Tool
    FLEXIV_AVAILABLE = True
except ImportError:
    pass


class HardwareRobotControl(BaseRobotControl, QObject):
    """硬件机器人控制实现类"""
    
    def __init__(self, robot_id: str = "Rizon4-062468"):
        """初始化硬件机器人控制器
        输入: robot_id - 机器人ID
        输出: 无返回值
        """
        BaseRobotControl.__init__(self, robot_id)
        QObject.__init__(self)
        
        self._signal_manager = get_signal_manager()
        self.robot: Optional[Robot] = None
        self.model: Optional[Model] = None
        self.tool: Optional[Tool] = None
        
        # 线程安全控制
        self._running = False
        self._robot_lock = threading.RLock()  # 可重入锁，保护机器人对象访问
        self._state_lock = threading.RLock()  # 状态变量保护锁
        self._monitor_lock = threading.RLock()  # 监控线程保护锁
        
        # 状态变量（线程安全访问）
        self.joint_angles = [0.0] * 7
        self.joint_velocities = [0.0] * 7
        self.joint_torques = [0.0] * 7
        self.tcp_pose = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
        self._current_mode = None
        self._last_error = None
        self._error_count = 0
        self._last_recovery_time = 0.0
        
        # 关节限位设置
        import math
        self.joint_limits = [
            (-math.pi, math.pi),           # Joint 1: ±180° -> ±π rad
            (-math.pi/2, math.pi/2),       # Joint 2: ±90° -> ±π/2 rad
            (-170*math.pi/180, 170*math.pi/180),  # Joint 3: ±170° -> ±170π/180 rad
            (-math.pi, math.pi),           # Joint 4: ±180° -> ±π rad
            (-120*math.pi/180, 120*math.pi/180),  # Joint 5: ±120° -> ±120π/180 rad
            (-2*math.pi, 2*math.pi),       # Joint 6: ±360° -> ±2π rad
            (-math.pi, math.pi)            # Joint 7: ±180° -> ±π rad
        ]
        
        # 错误恢复配置
        self._recovery_config = {
            'max_retries': 3,
            'retry_delay': 2.0,
            'error_threshold': 5,
            'recovery_timeout': 30.0
        }

    def connect(self) -> bool:
        """连接到硬件机器人
        输入: 无
        输出: 连接成功返回True，否则返回False
        """
        with self._robot_lock:
            if self.robot is not None:
                self._emit_signal(SignalType.WARNING, "机器人已连接")
                return True
            
            max_retries = self._recovery_config['max_retries']
            retry_delay = self._recovery_config['retry_delay']
            
            for attempt in range(max_retries):
                try:
                    # 尝试连接机器人
                    self.robot = Robot(self.robot_id, "192.168.2.100", "192.168.2.110")
                    
                    # 初始化模型和工具
                    self.model = Model(self.robot)
                    self.tool = Tool(self.robot)
                    
                    self._emit_signal(SignalType.INFO, f"成功连接到机器人 {self.robot_id}")
                    self._state = RobotState.CONNECTED
                    self._error_count = 0
                    self._last_error = None
                    return True
                    
                except Exception as e:
                    error_msg = f"连接尝试 {attempt + 1}/{max_retries} 失败: {str(e)}"
                    self._last_error = str(e)
                    self._error_count += 1
                    
                    if attempt < max_retries - 1:
                        self._emit_signal(SignalType.WARNING, f"{error_msg}, {retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                    else:
                        self._emit_signal(SignalType.ERROR, f"连接机器人失败: {str(e)}")
                        self.robot = None
                        self.model = None
                        self.tool = None
                        return False

    def disconnect(self) -> bool:
        """断开机器人连接
        输出: 断开成功返回True, 失败返回False
        """
        try:
            with self._robot_lock:
                if self.robot is not None:
                    self.stop()
                    self.robot = None
                    self.model = None
                    self.tool = None
                    self._state = RobotState.DISCONNECTED
                    self._emit_signal(SignalType.STATUS_UPDATE, "已断开机器人连接")
            return True
        except Exception as e:
            self._emit_signal(SignalType.ERROR, f"断开连接失败: {str(e)}")
            return False

    def enable(self) -> bool:
        """使能机器人
        输入: 无
        输出: 使能成功返回True，否则返回False
        """
        with self._robot_lock:
            if self.robot is None:
                self._emit_signal(SignalType.ERROR, "机器人未连接，无法使能")
                return False
            
            max_retries = self._recovery_config['max_retries']
            retry_delay = self._recovery_config['retry_delay']
            
            for attempt in range(max_retries):
                try:
                    # 检查急停状态
                    if not self.robot.estop_released():
                        self._emit_signal(SignalType.ERROR, "急停未释放，请先释放急停按钮")
                        return False
                    
                    # 检查并清除故障
                    if self.robot.fault():
                        self._emit_signal(SignalType.WARNING, "检测到机器人故障，正在清除...")
                        self.robot.ClearFault()
                        time.sleep(2.0)
                    
                    # 使能机器人
                    self.robot.enable()
                    
                    # 等待使能完成
                    enable_timeout = 30.0
                    start_time = time.time()
                    while time.time() - start_time < enable_timeout:
                        if self.robot.operational():
                            break
                        time.sleep(0.1)
                    
                    if not self.robot.operational():
                        raise TimeoutError("机器人使能超时")
                    
                    # 启动状态监控
                    self.start_monitoring()
                    
                    self._emit_signal(SignalType.INFO, "机器人已成功使能")
                    self._state = RobotState.ENABLED
                    self._error_count = 0
                    self._last_error = None
                    return True
                    
                except Exception as e:
                    error_msg = f"使能尝试 {attempt + 1}/{max_retries} 失败: {str(e)}"
                    self._last_error = str(e)
                    self._error_count += 1
                    
                    if attempt < max_retries - 1:
                        self._emit_signal(SignalType.WARNING, f"{error_msg}, {retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                    else:
                        self._emit_signal(SignalType.ERROR, f"机器人使能失败: {str(e)}")
                        return False

    def disable(self) -> bool:
        """禁用机器人
        输出: 禁用成功返回True, 失败返回False
        """
        try:
            self.stop()
            self._state = RobotState.CONNECTED
            self._emit_signal(SignalType.STATUS_UPDATE, "机器人已禁用")
            return True
        except Exception as e:
            self._emit_signal(SignalType.ERROR, f"禁用机器人失败: {str(e)}")
            return False

    def get_state(self) -> RobotState:
        """获取机器人状态
        输出: 当前机器人状态枚举值
        """
        return self._state

    def get_joint_positions(self) -> List[float]:
        """获取关节位置
        输出: 7个关节的角度列表(弧度制)
        """
        if self.robot and self.robot.connected():
            try:
                states = self.robot.states()
                return list(states.q)
            except Exception as e:
                self._logger.warning(f"获取关节位置失败: {e}")
        return self.joint_angles.copy()

    def get_joint_velocities(self) -> List[float]:
        """获取关节速度
        输出: 7个关节的速度列表(弧度/秒)
        """
        if self.robot and self.robot.connected():
            try:
                states = self.robot.states()
                return list(states.dq)
            except Exception as e:
                self._logger.warning(f"获取关节速度失败: {e}")
        return [0.0] * 7

    def get_joint_torques(self) -> List[float]:
        """获取关节力矩
        输出: 7个关节的力矩列表(Nm)
        """
        if self.robot and self.robot.connected():
            try:
                states = self.robot.states()
                return list(states.tau)
            except Exception as e:
                self._logger.warning(f"获取关节力矩失败: {e}")
        return [0.0] * 7

    def get_tcp_pose(self) -> List[float]:
        """获取TCP位姿
        输出: TCP位姿列表[x, y, z, qw, qx, qy, qz]
        """
        if self.robot and self.robot.connected():
            try:
                states = self.robot.states()
                return list(states.tcp_pose)
            except Exception as e:
                self._logger.warning(f"获取TCP位姿失败: {e}")
        return [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]

    def move_joint(self, target_positions: List[float], 
                  speed: float = 1.0, 
                  primitive: MotionPrimitive = MotionPrimitive.JOINT_MOVE) -> bool:
        """关节运动
        输入: target_positions - 目标关节角度, speed - 速度倍率, primitive - 运动原语
        输出: 运动命令发送成功返回True, 失败返回False
        """
        # 实现将在此处添加
        return False

    def move_linear(self, target_pose: List[float], 
                   speed: float = 1.0, 
                   primitive: MotionPrimitive = MotionPrimitive.LINEAR_MOVE) -> bool:
        """直线运动
        输入: target_pose - 目标位姿, speed - 速度倍率, primitive - 运动原语
        输出: 运动命令发送成功返回True, 失败返回False
        """
        # 实现将在此处添加
        return False

    def stop(self) -> bool:
        """停止运动
        输出: 停止成功返回True, 失败返回False
        """
        try:
            if self.robot and self.robot.connected():
                self.robot.Stop()
                return True
            return True
        except Exception as e:
            self._emit_signal(SignalType.ERROR, f"停止运动失败: {str(e)}")
            return False

    def get_diagnostics(self) -> Dict[str, Any]:
        """获取诊断信息
        输出: 包含诊断信息的字典
        """
        diagnostics = {
            'connected': self.robot.connected() if self.robot else False,
            'operational': self.robot.operational() if self.robot else False,
            'fault': self.robot.fault() if self.robot else False,
            'estop_released': self.robot.estop_released() if self.robot else False,
            'current_mode': str(self.robot.mode()) if self.robot else None,
            'state': self._state.value
        }
        return diagnostics

    def start_monitoring(self):
        """开始监控机器人状态"""
        if not self._running:
            self._running = True
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()

    def stop_monitoring(self):
        """停止监控机器人状态"""
        self._running = False

    def _monitor_loop(self):
        """机器人状态监控循环"""
        monitor_interval = 0.02  # 50Hz监控频率
        error_count = 0
        max_error_count = 10
        
        while self._running:
            try:
                with self._monitor_lock:
                    if self.robot and self.robot.connected():
                        # 获取机器人状态
                        states = self.robot.states()
                        
                        # 更新状态变量（线程安全）
                        with self._state_lock:
                            self.joint_angles = list(states.q)
                            self.joint_velocities = list(states.dq)
                            self.joint_torques = list(states.tau)
                            self.tcp_pose = list(states.tcp_pose)
                        
                        # 发射状态更新信号
                        self._emit_signal(SignalType.JOINT_UPDATE, self.joint_angles)
                        self._emit_signal(SignalType.CUSTOM, self.joint_velocities, "joint_velocity")
                        self._emit_signal(SignalType.CUSTOM, self.joint_torques, "joint_torque")
                        self._emit_signal(SignalType.TCP_UPDATE, self.tcp_pose)
                        self._emit_signal(SignalType.CUSTOM, states, "robot_states")
                        
                        # 更新模式
                        current_mode = self.robot.mode()
                        if current_mode != self._current_mode:
                            with self._state_lock:
                                self._current_mode = current_mode
                            self._emit_signal(SignalType.MODE_CHANGE, str(current_mode))
                        
                        # 检查机器人故障状态
                        if self.robot.fault():
                            self._emit_signal(SignalType.ERROR, "检测到机器人故障")
                            self._handle_robot_fault()
                        
                        # 重置错误计数
                        error_count = 0
                    
                time.sleep(monitor_interval)
                
            except Exception as e:
                error_count += 1
                self._logger.warning(f"状态监控错误 ({error_count}/{max_error_count}): {e}")
                
                # 如果连续错误超过阈值，停止监控
                if error_count >= max_error_count:
                    self._emit_signal(SignalType.ERROR, f"监控线程连续错误超过{max_error_count}次，停止监控")
                    self._running = False
                    break
                
                # 错误恢复延迟
                recovery_delay = min(1.0, 0.1 * error_count)
                time.sleep(recovery_delay)
    
    def _emit_signal(self, signal_type: SignalType, data: Any, custom_type: str = None) -> bool:
        """发射信号到信号管理器
        输入: signal_type - 信号类型, data - 信号数据, custom_type - 自定义信号类型
        输出: 发射成功返回True, 失败返回False
        """
        try:
            metadata = {"source": self._robot_id, "class": "HardwareRobotControl"}
            if custom_type:
                metadata["custom_type"] = custom_type
            
            signal_data = SignalData(
                signal_type=signal_type,
                source=self._robot_id,
                timestamp=time.time(),
                data=data,
                metadata=metadata
            )
            
            return self._signal_manager.emit_signal(signal_data)
            
        except Exception as e:
            self._logger.error(f"信号发射失败: {e}")
            return False

    def _handle_robot_fault(self):
        """处理机器人故障"""
        try:
            with self._robot_lock:
                if self.robot and self.robot.connected() and self.robot.fault():
                    self._emit_signal(SignalType.WARNING, "正在尝试清除机器人故障...")
                    self.robot.ClearFault()
                    time.sleep(2.0)
                    
                    if not self.robot.fault():
                        self._emit_signal(SignalType.INFO, "机器人故障已清除")
                    else:
                        self._emit_signal(SignalType.ERROR, "无法清除机器人故障")
                        
        except Exception as e:
            self._emit_signal(SignalType.ERROR, f"处理机器人故障失败: {str(e)}")