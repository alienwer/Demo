"""
信号管理器 - 实现基于信号的松耦合通信机制
"""
import threading
import weakref
import logging
from enum import Enum
from typing import Dict, List, Callable, Any, Optional
import time

class SignalType(Enum):
    """信号类型枚举"""
    # 机器人连接相关信号
    ROBOT_CONNECTED = "robot_connected"
    ROBOT_DISCONNECTED = "robot_disconnected"
    ROBOT_STATE_CHANGED = "robot_state_changed"
    
    # 运动控制相关信号
    MOTION_STARTED = "motion_started"
    MOTION_COMPLETED = "motion_completed"
    MOTION_STOPPED = "motion_stopped"
    
    # Primitive执行相关信号
    PRIMITIVE_STARTED = "primitive_started"
    PRIMITIVE_COMPLETED = "primitive_completed"
    PRIMITIVE_FAILED = "primitive_failed"
    PRIMITIVE_PROGRESS = "primitive_progress"
    
    # 安全相关信号
    SAFETY_STATE_CHANGED = "safety_state_changed"
    EMERGENCY_STOP_ACTIVATED = "emergency_stop_activated"
    COLLISION_DETECTED = "collision_detected"
    
    # 系统状态相关信号
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    SYSTEM_STATUS_UPDATED = "system_status_updated"
    
    # 配置相关信号
    CONFIG_UPDATED = "config_updated"
    GLOBAL_VARS_UPDATED = "global_vars_updated"
    
    # UI相关信号
    UI_NOTIFICATION = "ui_notification"
    UI_REFRESH_REQUESTED = "ui_refresh_requested"
    
    # 文件IO相关信号
    FILE_TRANSFER_STARTED = "file_transfer_started"
    FILE_TRANSFER_COMPLETED = "file_transfer_completed"
    FILE_TRANSFER_FAILED = "file_transfer_failed"

class SignalManager:
    """信号管理器 - 实现观察者模式的事件系统"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SignalManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 使用双重检查锁定确保单例
        if hasattr(self, '_initialized'):
            return
            
        with self._lock:
            if hasattr(self, '_initialized'):
                return
                
            self._handlers: Dict[SignalType, List[weakref.WeakMethod]] = {}
            self._logger = logging.getLogger(__name__)
            
            # 初始化所有信号类型的处理器列表
            for signal_type in SignalType:
                self._handlers[signal_type] = []
                
            self._initialized = True
    
    def connect(self, signal_type: SignalType, handler: Callable[[Any], None]):
        """
        连接信号处理器
        
        Args:
            signal_type: 信号类型
            handler: 处理函数
        """
        with self._lock:
            # 使用弱引用避免循环引用
            weak_handler = weakref.WeakMethod(handler)
            self._handlers[signal_type].append(weak_handler)
            self._logger.debug(f"Connected handler to signal: {signal_type.value}")
    
    def disconnect(self, signal_type: SignalType, handler: Callable[[Any], None]):
        """
        断开信号处理器
        
        Args:
            signal_type: 信号类型
            handler: 处理函数
        """
        with self._lock:
            handlers = self._handlers[signal_type]
            # 移除匹配的处理器
            self._handlers[signal_type] = [
                h for h in handlers 
                if h() is not None and h() != handler
            ]
            self._logger.debug(f"Disconnected handler from signal: {signal_type.value}")
    
    def emit(self, signal_type: SignalType, data: Any = None):
        """
        发送信号
        
        Args:
            signal_type: 信号类型
            data: 信号数据
        """
        with self._lock:
            handlers = self._handlers[signal_type][:]
            
        # 在锁外执行处理器，避免死锁
        executed_count = 0
        for weak_handler in handlers:
            handler = weak_handler()
            if handler is not None:
                try:
                    handler(data)
                    executed_count += 1
                except Exception as e:
                    self._logger.error(f"Signal handler error for {signal_type.value}: {e}")
            else:
                # 清理失效的弱引用
                with self._lock:
                    if weak_handler in self._handlers[signal_type]:
                        self._handlers[signal_type].remove(weak_handler)
        
        self._logger.debug(f"Emitted signal {signal_type.value} to {executed_count} handlers")

class SignalMixin:
    """信号混入类，为其他类提供信号功能"""
    
    def __init__(self):
        self._signal_manager = SignalManager()
    
    def connect_signal(self, signal_type: SignalType, handler: Callable[[Any], None]):
        """连接信号处理器"""
        self._signal_manager.connect(signal_type, handler)
    
    def disconnect_signal(self, signal_type: SignalType, handler: Callable[[Any], None]):
        """断开信号处理器"""
        self._signal_manager.disconnect(signal_type, handler)
    
    def emit_signal(self, signal_type: SignalType, data: Any = None):
        """发送信号"""
        self._signal_manager.emit(signal_type, data)

# 全局信号管理器实例
signal_manager = SignalManager()

def get_signal_manager() -> SignalManager:
    """获取全局信号管理器实例"""
    return signal_manager