"""
信号管理器 - 实现模块间通信的松耦合机制

遵循模块化设计原则：
1. 单一职责：专门负责信号通信
2. 接口统一：提供标准化的信号接口
3. 松耦合：通过信号-槽机制解耦模块
4. 可扩展性：支持动态添加新信号类型
"""

from typing import Dict, Any, Callable, List, Optional
from enum import Enum, auto
import logging
from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal


class SignalType(Enum):
    """信号类型枚举"""
    STATUS_UPDATE = auto()        # 状态更新信号
    ERROR = auto()               # 错误信号
    JOINT_UPDATE = auto()        # 关节数据更新
    TCP_UPDATE = auto()          # TCP位姿更新
    MODE_CHANGE = auto()         # 模式变更
    MOTION_START = auto()        # 运动开始
    MOTION_COMPLETE = auto()    # 运动完成
    CUSTOM = auto()              # 自定义信号


@dataclass
class SignalData:
    """信号数据容器"""
    signal_type: SignalType
    source: str                   # 信号源标识
    timestamp: float             # 时间戳
    data: Any                    # 信号数据
    metadata: Optional[Dict[str, Any]] = None  # 元数据


class SignalManager(QObject):
    """信号管理器 - 统一管理所有模块间通信信号"""
    
    # 定义标准信号接口
    status_updated = pyqtSignal(str)           # 状态更新信号
    error_occurred = pyqtSignal(str)           # 错误信号
    joint_angles_updated = pyqtSignal(list)   # 关节角度更新
    joint_velocities_updated = pyqtSignal(list) # 关节速度更新
    joint_torques_updated = pyqtSignal(list)   # 关节力矩更新
    tcp_pose_updated = pyqtSignal(list)        # TCP位姿更新
    mode_changed = pyqtSignal(str)            # 模式变更
    motion_started = pyqtSignal(str)          # 运动开始
    motion_completed = pyqtSignal(str)        # 运动完成
    
    # 通用信号（用于扩展）
    custom_signal = pyqtSignal(object)         # 自定义信号
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化信号管理器"""
        if self._initialized:
            return
            
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._signal_handlers: Dict[SignalType, List[Callable]] = {}
        self._custom_signals: Dict[str, pyqtSignal] = {}
        
        # 初始化所有信号类型的处理器列表
        for signal_type in SignalType:
            self._signal_handlers[signal_type] = []
        
        self._initialized = True
        self._logger.info("信号管理器初始化完成")
    
    def connect_signal(self, signal_type: SignalType, handler: Callable) -> bool:
        """连接信号处理器
        输入: signal_type - 信号类型, handler - 处理函数
        输出: 连接成功返回True, 失败返回False
        """
        try:
            if signal_type not in self._signal_handlers:
                self._logger.warning(f"未知信号类型: {signal_type}")
                return False
            
            if handler not in self._signal_handlers[signal_type]:
                self._signal_handlers[signal_type].append(handler)
                self._logger.debug(f"已连接信号处理器: {signal_type.name} -> {handler.__name__}")
            
            return True
            
        except Exception as e:
            self._logger.error(f"连接信号处理器失败: {e}")
            return False
    
    def disconnect_signal(self, signal_type: SignalType, handler: Callable) -> bool:
        """断开信号处理器
        输入: signal_type - 信号类型, handler - 处理函数
        输出: 断开成功返回True, 失败返回False
        """
        try:
            if signal_type in self._signal_handlers and handler in self._signal_handlers[signal_type]:
                self._signal_handlers[signal_type].remove(handler)
                self._logger.debug(f"已断开信号处理器: {signal_type.name} -> {handler.__name__}")
                return True
            return False
            
        except Exception as e:
            self._logger.error(f"断开信号处理器失败: {e}")
            return False
    
    def emit_signal(self, signal_data: SignalData) -> bool:
        """发射信号
        输入: signal_data - 信号数据
        输出: 发射成功返回True, 失败返回False
        """
        try:
            # 调用所有注册的处理器
            handlers = self._signal_handlers.get(signal_data.signal_type, [])
            for handler in handlers:
                try:
                    handler(signal_data)
                except Exception as e:
                    self._logger.error(f"信号处理器执行错误: {e}")
            
            # 同时发射对应的Qt信号
            self._emit_qt_signal(signal_data)
            
            self._logger.debug(f"信号发射成功: {signal_data.signal_type.name} from {signal_data.source}")
            return True
            
        except Exception as e:
            self._logger.error(f"信号发射失败: {e}")
            return False
    
    def _emit_qt_signal(self, signal_data: SignalData):
        """发射对应的Qt信号"""
        try:
            if signal_data.signal_type == SignalType.STATUS_UPDATE:
                if isinstance(signal_data.data, str):
                    self.status_updated.emit(signal_data.data)
            elif signal_data.signal_type == SignalType.ERROR:
                if isinstance(signal_data.data, str):
                    self.error_occurred.emit(signal_data.data)
            elif signal_data.signal_type == SignalType.JOINT_UPDATE:
                if isinstance(signal_data.data, list):
                    self.joint_angles_updated.emit(signal_data.data)
            elif signal_data.signal_type == SignalType.TCP_UPDATE:
                if isinstance(signal_data.data, list):
                    self.tcp_pose_updated.emit(signal_data.data)
            elif signal_data.signal_type == SignalType.MODE_CHANGE:
                if isinstance(signal_data.data, str):
                    self.mode_changed.emit(signal_data.data)
            elif signal_data.signal_type == SignalType.MOTION_START:
                if isinstance(signal_data.data, str):
                    self.motion_started.emit(signal_data.data)
            elif signal_data.signal_type == SignalType.MOTION_COMPLETE:
                if isinstance(signal_data.data, str):
                    self.motion_completed.emit(signal_data.data)
            elif signal_data.signal_type == SignalType.CUSTOM:
                self.custom_signal.emit(signal_data.data)
                
        except Exception as e:
            self._logger.error(f"Qt信号发射失败: {e}")
    
    def create_custom_signal(self, signal_name: str) -> Optional[pyqtSignal]:
        """创建自定义信号
        输入: signal_name - 信号名称
        输出: 创建的信号对象, 失败返回None
        """
        try:
            if signal_name in self._custom_signals:
                self._logger.warning(f"自定义信号已存在: {signal_name}")
                return self._custom_signals[signal_name]
            
            # 动态创建信号
            custom_signal = pyqtSignal(object)
            self._custom_signals[signal_name] = custom_signal
            
            self._logger.info(f"创建自定义信号: {signal_name}")
            return custom_signal
            
        except Exception as e:
            self._logger.error(f"创建自定义信号失败: {e}")
            return None
    
    def get_custom_signal(self, signal_name: str) -> Optional[pyqtSignal]:
        """获取自定义信号
        输入: signal_name - 信号名称
        输出: 信号对象, 不存在返回None
        """
        return self._custom_signals.get(signal_name)
    
    def remove_custom_signal(self, signal_name: str) -> bool:
        """移除自定义信号
        输入: signal_name - 信号名称
        输出: 移除成功返回True, 失败返回False
        """
        try:
            if signal_name in self._custom_signals:
                del self._custom_signals[signal_name]
                self._logger.info(f"已移除自定义信号: {signal_name}")
                return True
            return False
            
        except Exception as e:
            self._logger.error(f"移除自定义信号失败: {e}")
            return False
    
    def get_connected_handlers(self, signal_type: SignalType) -> List[Callable]:
        """获取已连接的处理器
        输入: signal_type - 信号类型
        输出: 处理器列表
        """
        return self._signal_handlers.get(signal_type, []).copy()
    
    def clear_handlers(self, signal_type: Optional[SignalType] = None):
        """清除信号处理器
        输入: signal_type - 信号类型(为None时清除所有)
        输出: 无返回值
        """
        try:
            if signal_type is None:
                for st in self._signal_handlers:
                    self._signal_handlers[st].clear()
                self._logger.info("已清除所有信号处理器")
            elif signal_type in self._signal_handlers:
                self._signal_handlers[signal_type].clear()
                self._logger.info(f"已清除信号处理器: {signal_type.name}")
                
        except Exception as e:
            self._logger.error(f"清除信号处理器失败: {e}")


# 全局信号管理器实例
def get_signal_manager() -> SignalManager:
    """获取全局信号管理器实例
    输出: 信号管理器实例
    """
    return SignalManager()