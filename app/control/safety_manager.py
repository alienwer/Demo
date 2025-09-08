'''
Author: LK
Date: 2025-01-XX XX:XX:XX
LastEditTime: 2025-01-XX XX:XX:XX
LastEditors: LK
FilePath: /Demo/app/control/safety_manager.py
'''

import threading
import time
from typing import Dict, Any, List, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from dataclasses import dataclass
from enum import Enum

# 导入线程管理器和资源管理器
from ..core.thread_manager import get_thread_manager
from ..core.resource_manager import get_resource_manager, ResourceType, AccessMode

try:
    from flexiv import Safety, SafetyStates, SafetyConfig
except ImportError:
    # 仿真模式下的模拟类
    class Safety:
        def __init__(self, robot_ip: str):
            self.robot_ip = robot_ip
            self.connected = False
        
        def connect(self) -> bool:
            self.connected = True
            return True
        
        def disconnect(self):
            self.connected = False
        
        def is_connected(self) -> bool:
            return self.connected
        
        def get_safety_states(self) -> 'SafetyStates':
            return SafetyStates()
        
        def get_safety_config(self) -> 'SafetyConfig':
            return SafetyConfig()
        
        def set_safety_config(self, config: 'SafetyConfig') -> bool:
            return True
        
        def enable_emergency_stop(self) -> bool:
            return True
        
        def disable_emergency_stop(self) -> bool:
            return True
        
        def reset_safety_system(self) -> bool:
            return True
        
        def set_collision_detection(self, enabled: bool, sensitivity: float = 0.5) -> bool:
            return True
        
        def set_joint_limits(self, joint_idx: int, min_pos: float, max_pos: float) -> bool:
            return True
        
        def set_cartesian_limits(self, limits: Dict[str, float]) -> bool:
            return True
        
        def set_velocity_limits(self, joint_vel: List[float], cartesian_vel: float) -> bool:
            return True
        
        def set_force_limits(self, force_limit: float, torque_limit: float) -> bool:
            return True
    
    class SafetyStates:
        def __init__(self):
            self.emergency_stopped = False
            self.protective_stopped = False
            self.collision_detected = False
            self.joint_limits_violated = [False] * 7
            self.cartesian_limits_violated = False
            self.velocity_limits_violated = False
            self.force_limits_violated = False
            self.safety_system_enabled = True
            self.safety_config_valid = True
            self.last_fault_code = 0
            self.fault_description = ""
    
    class SafetyConfig:
        def __init__(self):
            self.collision_detection_enabled = True
            self.collision_sensitivity = 0.5
            self.joint_position_limits = [[-180, 180]] * 7
            self.cartesian_position_limits = {
                "x_min": -1.0, "x_max": 1.0,
                "y_min": -1.0, "y_max": 1.0,
                "z_min": 0.0, "z_max": 2.0
            }
            self.joint_velocity_limits = [180.0] * 7  # deg/s
            self.cartesian_velocity_limit = 1.0  # m/s
            self.force_limit = 100.0  # N
            self.torque_limit = 50.0  # Nm
            self.emergency_stop_enabled = True

class SafetyLevel(Enum):
    """安全等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SafetyEvent(Enum):
    """安全事件类型"""
    EMERGENCY_STOP = "emergency_stop"
    PROTECTIVE_STOP = "protective_stop"
    COLLISION_DETECTED = "collision_detected"
    JOINT_LIMIT_VIOLATED = "joint_limit_violated"
    CARTESIAN_LIMIT_VIOLATED = "cartesian_limit_violated"
    VELOCITY_LIMIT_VIOLATED = "velocity_limit_violated"
    FORCE_LIMIT_VIOLATED = "force_limit_violated"
    SAFETY_SYSTEM_FAULT = "safety_system_fault"
    SAFETY_CONFIG_INVALID = "safety_config_invalid"

@dataclass
class SafetyAlert:
    """安全警报数据结构"""
    event_type: SafetyEvent
    level: SafetyLevel
    timestamp: float
    message: str
    details: Dict[str, Any]
    acknowledged: bool = False

class SafetyManager(QObject):
    """安全管理器
    
    负责管理机器人安全系统，包括：
    - 安全状态监控
    - 安全配置管理
    - 碰撞检测
    - 限位保护
    - 紧急停止
    - 安全事件处理
    """
    
    # 信号定义
    safety_states_updated = pyqtSignal(object)  # SafetyStates
    safety_config_updated = pyqtSignal(object)  # SafetyConfig
    safety_alert = pyqtSignal(object)  # SafetyAlert
    emergency_stop_triggered = pyqtSignal(str)  # reason
    protective_stop_triggered = pyqtSignal(str)  # reason
    collision_detected = pyqtSignal(dict)  # collision_info
    safety_system_fault = pyqtSignal(int, str)  # fault_code, description
    safety_status_changed = pyqtSignal(str)  # status_message
    
    def __init__(self, robot=None, hardware=True, robot_ip: str = "192.168.2.100", parent=None):
        super().__init__(parent)
        
        self.robot = robot
        self.hardware = hardware
        self.robot_ip = robot_ip
        self.safety = None
        self.connected = False
        self.monitoring_enabled = False
        
        # 状态数据
        self.current_states = None
        self.current_config = None
        self.safety_alerts = []  # 安全警报历史
        self.max_alerts = 1000  # 最大警报数量
        
        # 监控线程
        self.monitor_thread = None
        self.monitor_lock = threading.Lock()
        self.stop_monitoring = threading.Event()
        # 初始化线程管理器和资源管理器
        self.thread_manager = get_thread_manager()
        self.resource_manager = get_resource_manager()
        
        # 注册安全系统资源
        self.resource_manager.register_resource(
            resource_id=f"safety_{self.robot_ip}",
            resource_type=ResourceType.SENSOR,
            metadata={
                "robot_ip": self.robot_ip
            }
        )
        
        # 定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        
        # 安全配置缓存
        self.config_cache = {}
        
        # 初始化
        self.init_safety_system()
    
    def init_safety_system(self):
        """初始化安全系统"""
        try:
            self.safety = Safety(self.robot_ip)
            self.safety_status_changed.emit("安全系统已初始化")
        except Exception as e:
            self.safety_status_changed.emit(f"安全系统初始化失败: {str(e)}")
    
    def connect_safety_system(self) -> bool:
        """连接安全系统"""
        try:
            if not self.safety:
                self.init_safety_system()
            
            if self.safety and self.safety.connect():
                self.connected = True
                self.safety_status_changed.emit("安全系统已连接")
                
                # 获取初始状态和配置
                self.update_safety_states()
                self.update_safety_config()
                
                return True
            else:
                self.safety_status_changed.emit("安全系统连接失败")
                return False
                
        except Exception as e:
            self.safety_status_changed.emit(f"安全系统连接错误: {str(e)}")
            return False
    
    def disconnect_safety_system(self):
        """断开安全系统连接"""
        try:
            self.stop_monitoring_safety()
            
            if self.safety and self.connected:
                self.safety.disconnect()
                self.connected = False
                self.safety_status_changed.emit("安全系统已断开")
                
        except Exception as e:
            self.safety_status_changed.emit(f"安全系统断开错误: {str(e)}")
    
    def is_connected(self) -> bool:
        """检查安全系统连接状态"""
        return self.connected and self.safety and self.safety.is_connected()
    
    def start_monitoring_safety(self, interval: float = 0.1):
        """开始安全监控"""
        if self.monitoring_enabled:
            return
        
        if not self.is_connected():
            self.safety_status_changed.emit("安全系统未连接，无法开始监控")
            return
        
        self.monitoring_enabled = True
        self.stop_monitoring.clear()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(
            target=self._safety_monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
        # 启动状态定时器
        self.status_timer.start(int(interval * 1000))
        
        self.safety_status_changed.emit("安全监控已启动")
    
    def stop_monitoring_safety(self):
        """停止安全监控"""
        if not self.monitoring_enabled:
            return
        
        self.monitoring_enabled = False
        self.stop_monitoring.set()
        
        # 停止定时器
        self.status_timer.stop()
        
        # 等待监控线程结束
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        
        self.safety_status_changed.emit("安全监控已停止")
    
    def _safety_monitor_loop(self, interval: float):
        """安全监控循环"""
        while not self.stop_monitoring.is_set():
            try:
                with self.monitor_lock:
                    if self.is_connected():
                        # 更新安全状态
                        self.update_safety_states()
                        
                        # 检查安全事件
                        self.check_safety_events()
                
                time.sleep(interval)
                
            except Exception as e:
                self.safety_status_changed.emit(f"安全监控错误: {str(e)}")
                time.sleep(interval)
    
    def update_safety_states(self):
        """更新安全状态"""
        try:
            if not self.is_connected():
                return
            
            states = self.safety.get_safety_states()
            self.current_states = states
            self.safety_states_updated.emit(states)
            
        except Exception as e:
            self.safety_status_changed.emit(f"获取安全状态失败: {str(e)}")
    
    def update_safety_config(self):
        """更新安全配置"""
        try:
            if not self.is_connected():
                return
            
            config = self.safety.get_safety_config()
            self.current_config = config
            self.safety_config_updated.emit(config)
            
        except Exception as e:
            self.safety_status_changed.emit(f"获取安全配置失败: {str(e)}")
    
    def check_safety_events(self):
        """检查安全事件"""
        if not self.current_states:
            return
        
        states = self.current_states
        
        # 检查紧急停止
        if states.emergency_stopped:
            self.handle_safety_event(
                SafetyEvent.EMERGENCY_STOP,
                SafetyLevel.CRITICAL,
                "紧急停止已触发",
                {"emergency_stopped": True}
            )
            self.emergency_stop_triggered.emit("紧急停止按钮被按下")
        
        # 检查保护性停止
        if states.protective_stopped:
            self.handle_safety_event(
                SafetyEvent.PROTECTIVE_STOP,
                SafetyLevel.HIGH,
                "保护性停止已触发",
                {"protective_stopped": True}
            )
            self.protective_stop_triggered.emit("安全限制触发保护性停止")
        
        # 检查碰撞检测
        if states.collision_detected:
            collision_info = {"collision_detected": True}
            self.handle_safety_event(
                SafetyEvent.COLLISION_DETECTED,
                SafetyLevel.HIGH,
                "检测到碰撞",
                collision_info
            )
            self.collision_detected.emit(collision_info)
        
        # 检查关节限位
        for i, violated in enumerate(states.joint_limits_violated):
            if violated:
                self.handle_safety_event(
                    SafetyEvent.JOINT_LIMIT_VIOLATED,
                    SafetyLevel.MEDIUM,
                    f"关节 {i+1} 超出限位",
                    {"joint_index": i, "violated": True}
                )
        
        # 检查笛卡尔限位
        if states.cartesian_limits_violated:
            self.handle_safety_event(
                SafetyEvent.CARTESIAN_LIMIT_VIOLATED,
                SafetyLevel.MEDIUM,
                "笛卡尔空间超出限位",
                {"cartesian_limits_violated": True}
            )
        
        # 检查速度限制
        if states.velocity_limits_violated:
            self.handle_safety_event(
                SafetyEvent.VELOCITY_LIMIT_VIOLATED,
                SafetyLevel.MEDIUM,
                "速度超出限制",
                {"velocity_limits_violated": True}
            )
        
        # 检查力限制
        if states.force_limits_violated:
            self.handle_safety_event(
                SafetyEvent.FORCE_LIMIT_VIOLATED,
                SafetyLevel.MEDIUM,
                "力/力矩超出限制",
                {"force_limits_violated": True}
            )
        
        # 检查安全系统故障
        if not states.safety_system_enabled or not states.safety_config_valid:
            fault_code = states.last_fault_code
            fault_desc = states.fault_description
            
            self.handle_safety_event(
                SafetyEvent.SAFETY_SYSTEM_FAULT,
                SafetyLevel.CRITICAL,
                f"安全系统故障: {fault_desc}",
                {"fault_code": fault_code, "fault_description": fault_desc}
            )
            self.safety_system_fault.emit(fault_code, fault_desc)
    
    def handle_safety_event(self, event_type: SafetyEvent, level: SafetyLevel, 
                          message: str, details: Dict[str, Any]):
        """处理安全事件"""
        alert = SafetyAlert(
            event_type=event_type,
            level=level,
            timestamp=time.time(),
            message=message,
            details=details
        )
        
        # 添加到警报历史
        self.safety_alerts.append(alert)
        
        # 限制警报数量
        if len(self.safety_alerts) > self.max_alerts:
            self.safety_alerts = self.safety_alerts[-self.max_alerts:]
        
        # 发送警报信号
        self.safety_alert.emit(alert)
    
    def get_safety_states(self) -> Optional[object]:
        """获取当前安全状态"""
        return self.current_states
    
    def get_safety_config(self) -> Optional[object]:
        """获取当前安全配置"""
        return self.current_config
    
    def set_safety_config(self, config: object) -> bool:
        """设置安全配置"""
        try:
            if not self.is_connected():
                self.safety_status_changed.emit("安全系统未连接，无法设置配置")
                return False
            
            success = self.safety.set_safety_config(config)
            if success:
                self.current_config = config
                self.safety_config_updated.emit(config)
                self.safety_status_changed.emit("安全配置已更新")
            else:
                self.safety_status_changed.emit("安全配置设置失败")
            
            return success
            
        except Exception as e:
            self.safety_status_changed.emit(f"设置安全配置错误: {str(e)}")
            return False
    
    def enable_emergency_stop(self) -> bool:
        """启用紧急停止"""
        try:
            if not self.is_connected():
                return False
            
            success = self.safety.enable_emergency_stop()
            if success:
                self.safety_status_changed.emit("紧急停止已启用")
            else:
                self.safety_status_changed.emit("紧急停止启用失败")
            
            return success
            
        except Exception as e:
            self.safety_status_changed.emit(f"启用紧急停止错误: {str(e)}")
            return False
    
    def disable_emergency_stop(self) -> bool:
        """禁用紧急停止"""
        try:
            if not self.is_connected():
                return False
            
            success = self.safety.disable_emergency_stop()
            if success:
                self.safety_status_changed.emit("紧急停止已禁用")
            else:
                self.safety_status_changed.emit("紧急停止禁用失败")
            
            return success
            
        except Exception as e:
            self.safety_status_changed.emit(f"禁用紧急停止错误: {str(e)}")
            return False
    
    def reset_safety_system(self) -> bool:
        """重置安全系统"""
        try:
            if not self.is_connected():
                return False
            
            success = self.safety.reset_safety_system()
            if success:
                self.safety_status_changed.emit("安全系统已重置")
                # 重新获取状态
                self.update_safety_states()
                self.update_safety_config()
            else:
                self.safety_status_changed.emit("安全系统重置失败")
            
            return success
            
        except Exception as e:
            self.safety_status_changed.emit(f"重置安全系统错误: {str(e)}")
            return False
    
    def set_collision_detection(self, enabled: bool, sensitivity: float = 0.5) -> bool:
        """设置碰撞检测"""
        try:
            if not self.is_connected():
                return False
            
            success = self.safety.set_collision_detection(enabled, sensitivity)
            if success:
                status = "启用" if enabled else "禁用"
                self.safety_status_changed.emit(f"碰撞检测已{status}，灵敏度: {sensitivity}")
            else:
                self.safety_status_changed.emit("碰撞检测设置失败")
            
            return success
            
        except Exception as e:
            self.safety_status_changed.emit(f"设置碰撞检测错误: {str(e)}")
            return False
    
    def set_joint_limits(self, joint_idx: int, min_pos: float, max_pos: float) -> bool:
        """设置关节限位"""
        try:
            if not self.is_connected():
                return False
            
            if not (0 <= joint_idx < 7):
                self.safety_status_changed.emit("关节索引超出范围 (0-6)")
                return False
            
            success = self.safety.set_joint_limits(joint_idx, min_pos, max_pos)
            if success:
                self.safety_status_changed.emit(
                    f"关节 {joint_idx+1} 限位已设置: [{min_pos:.1f}, {max_pos:.1f}] deg"
                )
            else:
                self.safety_status_changed.emit(f"关节 {joint_idx+1} 限位设置失败")
            
            return success
            
        except Exception as e:
            self.safety_status_changed.emit(f"设置关节限位错误: {str(e)}")
            return False
    
    def set_cartesian_limits(self, limits: Dict[str, float]) -> bool:
        """设置笛卡尔空间限位"""
        try:
            if not self.is_connected():
                return False
            
            success = self.safety.set_cartesian_limits(limits)
            if success:
                self.safety_status_changed.emit("笛卡尔空间限位已设置")
            else:
                self.safety_status_changed.emit("笛卡尔空间限位设置失败")
            
            return success
            
        except Exception as e:
            self.safety_status_changed.emit(f"设置笛卡尔限位错误: {str(e)}")
            return False
    
    def set_velocity_limits(self, joint_vel: List[float], cartesian_vel: float) -> bool:
        """设置速度限制"""
        try:
            if not self.is_connected():
                return False
            
            success = self.safety.set_velocity_limits(joint_vel, cartesian_vel)
            if success:
                self.safety_status_changed.emit(
                    f"速度限制已设置: 关节 {joint_vel} deg/s, 笛卡尔 {cartesian_vel} m/s"
                )
            else:
                self.safety_status_changed.emit("速度限制设置失败")
            
            return success
            
        except Exception as e:
            self.safety_status_changed.emit(f"设置速度限制错误: {str(e)}")
            return False
    
    def set_force_limits(self, force_limit: float, torque_limit: float) -> bool:
        """设置力/力矩限制"""
        try:
            if not self.is_connected():
                return False
            
            success = self.safety.set_force_limits(force_limit, torque_limit)
            if success:
                self.safety_status_changed.emit(
                    f"力限制已设置: 力 {force_limit} N, 力矩 {torque_limit} Nm"
                )
            else:
                self.safety_status_changed.emit("力限制设置失败")
            
            return success
            
        except Exception as e:
            self.safety_status_changed.emit(f"设置力限制错误: {str(e)}")
            return False
    
    def get_safety_alerts(self, level: Optional[SafetyLevel] = None, 
                         limit: int = 100) -> List[SafetyAlert]:
        """获取安全警报"""
        alerts = self.safety_alerts
        
        if level:
            alerts = [alert for alert in alerts if alert.level == level]
        
        # 按时间倒序排列，返回最新的警报
        alerts = sorted(alerts, key=lambda x: x.timestamp, reverse=True)
        
        return alerts[:limit]
    
    def acknowledge_alert(self, alert_index: int) -> bool:
        """确认警报"""
        if 0 <= alert_index < len(self.safety_alerts):
            self.safety_alerts[alert_index].acknowledged = True
            return True
        return False
    
    def clear_acknowledged_alerts(self):
        """清除已确认的警报"""
        self.safety_alerts = [alert for alert in self.safety_alerts if not alert.acknowledged]
    
    def update_status(self):
        """更新状态（定时器回调）"""
        if self.is_connected() and not self.monitoring_enabled:
            self.update_safety_states()
    
    def get_safety_summary(self) -> Dict[str, Any]:
        """获取安全系统摘要"""
        summary = {
            "connected": self.is_connected(),
            "monitoring": self.monitoring_enabled,
            "total_alerts": len(self.safety_alerts),
            "unacknowledged_alerts": len([a for a in self.safety_alerts if not a.acknowledged]),
            "critical_alerts": len([a for a in self.safety_alerts if a.level == SafetyLevel.CRITICAL]),
            "last_update": time.time()
        }
        
        if self.current_states:
            summary.update({
                "emergency_stopped": self.current_states.emergency_stopped,
                "protective_stopped": self.current_states.protective_stopped,
                "collision_detected": self.current_states.collision_detected,
                "safety_system_enabled": self.current_states.safety_system_enabled
            })
        
        return summary