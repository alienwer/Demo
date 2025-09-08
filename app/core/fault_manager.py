"""
故障管理器 - 实现完整的故障分类体系
提供故障定义、注册、处理和恢复机制
"""

import threading
import time
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

# 导入信号管理器
from .signal_manager import SignalManager, SignalType

class FaultLevel(Enum):
    """故障级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"

class FaultCategory(Enum):
    """故障类别"""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    USER_ERROR = "user_error"
    EXTERNAL = "external"

@dataclass
class FaultDefinition:
    """故障定义"""
    code: int
    name: str
    category: FaultCategory
    level: FaultLevel
    description: str
    possible_causes: List[str] = field(default_factory=list)
    recovery_actions: List[str] = field(default_factory=list)
    auto_recovery: bool = False
    requires_user_action: bool = False

@dataclass
class FaultInstance:
    """故障实例"""
    id: str
    fault_code: int
    fault_definition: FaultDefinition
    occurred_at: float
    context_data: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: List[str] = field(default_factory=list)
    resolved_at: Optional[float] = None
    resolution_method: Optional[str] = None

class FaultRegistry:
    """故障注册表"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(FaultRegistry, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 使用双重检查锁定确保单例
        if hasattr(self, '_initialized'):
            return
            
        with FaultRegistry._lock:
            if hasattr(self, '_initialized'):
                return
                
            self._faults: Dict[int, FaultDefinition] = {}
            self._logger = logging.getLogger(__name__)
            self._initialize_standard_faults()
            self._initialized = True
    
    def _initialize_standard_faults(self):
        """初始化标准故障定义"""
        standard_faults = [
            FaultDefinition(
                code=1001,
                name="ROBOT_CONNECTION_LOST",
                category=FaultCategory.NETWORK,
                level=FaultLevel.ERROR,
                description="机器人连接丢失",
                possible_causes=["网络中断", "机器人断电", "RDK服务停止"],
                recovery_actions=["检查网络连接", "重启机器人", "重新连接"],
                auto_recovery=True
            ),
            FaultDefinition(
                code=1002,
                name="JOINT_LIMIT_EXCEEDED",
                category=FaultCategory.HARDWARE,
                level=FaultLevel.WARNING,
                description="关节超出限位",
                possible_causes=["运动规划错误", "关节限位设置错误"],
                recovery_actions=["停止运动", "回到安全位置", "检查限位设置"],
                auto_recovery=False,
                requires_user_action=True
            ),
            FaultDefinition(
                code=1003,
                name="EMERGENCY_STOP_ACTIVATED",
                category=FaultCategory.HARDWARE,
                level=FaultLevel.CRITICAL,
                description="紧急停止被激活",
                possible_causes=["用户按下急停", "安全系统触发", "外部急停信号"],
                recovery_actions=["确认安全", "复位急停", "重新启动系统"],
                auto_recovery=False,
                requires_user_action=True
            ),
            FaultDefinition(
                code=1004,
                name="COLLISION_DETECTED",
                category=FaultCategory.HARDWARE,
                level=FaultLevel.CRITICAL,
                description="检测到碰撞",
                possible_causes=["意外接触", "传感器故障", "运动规划错误"],
                recovery_actions=["停止运动", "回退", "检查环境"],
                auto_recovery=False,
                requires_user_action=True
            ),
            FaultDefinition(
                code=1005,
                name="MOTOR_OVERHEAT",
                category=FaultCategory.HARDWARE,
                level=FaultLevel.WARNING,
                description="电机过热",
                possible_causes=["长时间高负载运行", "环境温度过高", "散热不良"],
                recovery_actions=["降低负载", "暂停运行", "改善散热"],
                auto_recovery=True
            ),
            FaultDefinition(
                code=1006,
                name="SENSOR_FAILURE",
                category=FaultCategory.HARDWARE,
                level=FaultLevel.ERROR,
                description="传感器故障",
                possible_causes=["传感器损坏", "连接问题", "电源异常"],
                recovery_actions=["检查连接", "更换传感器", "重启系统"],
                auto_recovery=False,
                requires_user_action=True
            ),
            FaultDefinition(
                code=1007,
                name="CONFIGURATION_ERROR",
                category=FaultCategory.CONFIGURATION,
                level=FaultLevel.ERROR,
                description="配置错误",
                possible_causes=["参数设置错误", "配置文件损坏", "版本不兼容"],
                recovery_actions=["检查配置", "恢复默认配置", "更新配置"],
                auto_recovery=False,
                requires_user_action=True
            ),
            FaultDefinition(
                code=1008,
                name="SYSTEM_RESOURCE_EXHAUSTED",
                category=FaultCategory.SOFTWARE,
                level=FaultLevel.CRITICAL,
                description="系统资源耗尽",
                possible_causes=["内存不足", "CPU占用过高", "磁盘空间不足"],
                recovery_actions=["释放资源", "重启服务", "扩展资源"],
                auto_recovery=False,
                requires_user_action=True
            )
        ]
        
        for fault in standard_faults:
            self._faults[fault.code] = fault
    
    def register_fault(self, fault: FaultDefinition):
        """注册故障定义"""
        with self._lock:
            self._faults[fault.code] = fault
            self._logger.info(f"Registered fault: {fault.name} (code: {fault.code})")
    
    def get_fault(self, code: int) -> Optional[FaultDefinition]:
        """获取故障定义"""
        with self._lock:
            return self._faults.get(code)
    
    def get_faults_by_category(self, category: FaultCategory) -> List[FaultDefinition]:
        """按类别获取故障"""
        with self._lock:
            return [fault for fault in self._faults.values() if fault.category == category]
    
    def get_faults_by_level(self, level: FaultLevel) -> List[FaultDefinition]:
        """按级别获取故障"""
        with self._lock:
            return [fault for fault in self._faults.values() if fault.level == level]
    
    def list_all_faults(self) -> List[FaultDefinition]:
        """列出所有故障定义"""
        with self._lock:
            return list(self._faults.values())

class RecoveryActionType(Enum):
    """恢复动作类型"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    INTERACTIVE = "interactive"

class RecoveryStatus(Enum):
    """恢复状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class RecoveryAction:
    """恢复动作"""
    id: str
    name: str
    action_type: RecoveryActionType
    description: str
    handler: Callable[[], bool]
    timeout: float = 30.0
    prerequisites: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)

class FaultHandler:
    """故障处理器"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(FaultHandler, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 使用双重检查锁定确保单例
        if hasattr(self, '_initialized'):
            return
            
        with FaultHandler._lock:
            if hasattr(self, '_initialized'):
                return
                
            self.fault_registry = FaultRegistry()
            self.recovery_actions: Dict[str, RecoveryAction] = {}
            self.active_faults: Dict[str, FaultInstance] = {}
            self.fault_history: List[FaultInstance] = []
            self.recovery_callbacks: List[Callable[[FaultInstance, RecoveryStatus], None]] = []
            self._logger = logging.getLogger(__name__)
            self._signal_manager = SignalManager()
            
            # 注册标准恢复动作
            self._register_standard_recovery_actions()
            self._initialized = True
    
    def _register_standard_recovery_actions(self):
        """注册标准恢复动作"""
        # 自动重连动作
        self.register_recovery_action(RecoveryAction(
            id="auto_reconnect",
            name="自动重连",
            action_type=RecoveryActionType.AUTOMATIC,
            description="尝试重新连接机器人",
            handler=self._auto_reconnect_handler,
            timeout=10.0
        ))
        
        # 重启服务动作
        self.register_recovery_action(RecoveryAction(
            id="restart_service",
            name="重启服务",
            action_type=RecoveryActionType.MANUAL,
            description="重启相关服务",
            handler=self._restart_service_handler,
            timeout=30.0
        ))
        
        # 用户确认动作
        self.register_recovery_action(RecoveryAction(
            id="user_confirmation",
            name="用户确认",
            action_type=RecoveryActionType.INTERACTIVE,
            description="等待用户确认安全后继续",
            handler=self._user_confirmation_handler,
            timeout=300.0  # 5分钟超时
        ))
    
    def register_recovery_action(self, action: RecoveryAction):
        """注册恢复动作"""
        with self._lock:
            self.recovery_actions[action.id] = action
            self._logger.info(f"Registered recovery action: {action.name} (id: {action.id})")
    
    def handle_fault(self, fault_code: int, context_data: Optional[Dict[str, Any]] = None) -> str:
        """处理故障"""
        fault_definition = self.fault_registry.get_fault(fault_code)
        if not fault_definition:
            self._logger.error(f"Unknown fault code: {fault_code}")
            # 发送系统错误信号
            self._signal_manager.emit(SignalType.SYSTEM_ERROR, {
                "error_code": fault_code,
                "message": f"Unknown fault code: {fault_code}"
            })
            return ""
        
        # 创建故障实例
        fault_instance = FaultInstance(
            id=f"fault_{int(time.time() * 1000)}",
            fault_code=fault_code,
            fault_definition=fault_definition,
            occurred_at=time.time(),
            context_data=context_data or {}
        )
        
        with self._lock:
            self.active_faults[fault_instance.id] = fault_instance
        
        self._logger.error(f"Fault occurred: {fault_definition.name} - {fault_definition.description}")
        
        # 发送故障信号
        self._signal_manager.emit(SignalType.SYSTEM_ERROR, {
            "fault_id": fault_instance.id,
            "fault_code": fault_code,
            "fault_name": fault_definition.name,
            "level": fault_definition.level.value,
            "description": fault_definition.description
        })
        
        # 根据故障级别决定处理策略
        if fault_definition.level == FaultLevel.FATAL:
            self._handle_fatal_fault(fault_instance)
        elif fault_definition.auto_recovery:
            self._attempt_auto_recovery(fault_instance)
        elif fault_definition.requires_user_action:
            self._request_user_action(fault_instance)
        
        return fault_instance.id
    
    def _handle_fatal_fault(self, fault_instance: FaultInstance):
        """处理致命故障"""
        self._logger.critical(f"Fatal fault detected: {fault_instance.fault_definition.name}")
        
        # 立即停止所有操作
        self._emergency_shutdown()
        
        # 通知所有回调
        self._notify_recovery_callbacks(fault_instance, RecoveryStatus.FAILED)
    
    def _attempt_auto_recovery(self, fault_instance: FaultInstance):
        """尝试自动恢复"""
        recovery_actions = fault_instance.fault_definition.recovery_actions
        
        for action_id in recovery_actions:
            if action_id in self.recovery_actions:
                action = self.recovery_actions[action_id]
                if action.action_type == RecoveryActionType.AUTOMATIC:
                    success = self._execute_recovery_action(fault_instance, action)
                    if success:
                        self._resolve_fault(fault_instance, action_id)
                        return
        
        # 自动恢复失败，请求用户干预
        self._request_user_action(fault_instance)
    
    def _request_user_action(self, fault_instance: FaultInstance):
        """请求用户操作"""
        self._logger.warning(f"User action required for fault: {fault_instance.fault_definition.name}")
        
        # 发送用户通知信号
        self._signal_manager.emit(SignalType.UI_NOTIFICATION, {
            "type": "fault",
            "fault_id": fault_instance.id,
            "fault_name": fault_instance.fault_definition.name,
            "description": fault_instance.fault_definition.description,
            "level": fault_instance.fault_definition.level.value,
            "requires_user_action": True
        })
        
        # 等待用户响应（在实际实现中需要UI交互）
        # 这里简化处理，直接记录需要用户操作
        pass
    
    def _execute_recovery_action(self, fault_instance: FaultInstance, action: RecoveryAction) -> bool:
        """执行恢复动作"""
        self._logger.info(f"Executing recovery action: {action.name}")
        
        try:
            # 记录恢复尝试
            fault_instance.recovery_attempts.append(action.id)
            
            # 通知开始恢复
            self._notify_recovery_callbacks(fault_instance, RecoveryStatus.IN_PROGRESS)
            
            # 执行恢复动作
            success = action.handler()
            
            if success:
                self._logger.info(f"Recovery action succeeded: {action.name}")
                self._notify_recovery_callbacks(fault_instance, RecoveryStatus.SUCCESS)
            else:
                self._logger.warning(f"Recovery action failed: {action.name}")
                self._notify_recovery_callbacks(fault_instance, RecoveryStatus.FAILED)
            
            return success
        
        except Exception as e:
            self._logger.error(f"Recovery action error: {action.name} - {str(e)}")
            self._notify_recovery_callbacks(fault_instance, RecoveryStatus.FAILED)
            return False
    
    def _resolve_fault(self, fault_instance: FaultInstance, resolution_method: str):
        """解决故障"""
        fault_instance.resolved_at = time.time()
        fault_instance.resolution_method = resolution_method
        
        with self._lock:
            if fault_instance.id in self.active_faults:
                del self.active_faults[fault_instance.id]
            self.fault_history.append(fault_instance)
        
        self._logger.info(f"Fault resolved: {fault_instance.fault_definition.name} using {resolution_method}")
        
        # 发送故障解决信号
        self._signal_manager.emit(SignalType.SYSTEM_STATUS_UPDATED, {
            "type": "fault_resolved",
            "fault_id": fault_instance.id,
            "fault_name": fault_instance.fault_definition.name,
            "resolution_method": resolution_method
        })
    
    def _auto_reconnect_handler(self) -> bool:
        """自动重连处理器"""
        # 实现自动重连逻辑
        try:
            # 这里应该调用实际的重连逻辑
            # return robot_controller.reconnect()
            time.sleep(2)  # 模拟重连过程
            return True
        except Exception as e:
            self._logger.error(f"Auto reconnect failed: {str(e)}")
            return False
    
    def _restart_service_handler(self) -> bool:
        """重启服务处理器"""
        # 实现服务重启逻辑
        try:
            # 这里应该调用实际的服务重启逻辑
            time.sleep(5)  # 模拟重启过程
            return True
        except Exception as e:
            self._logger.error(f"Service restart failed: {str(e)}")
            return False
    
    def _user_confirmation_handler(self) -> bool:
        """用户确认处理器"""
        # 实现用户确认逻辑
        # 这通常涉及UI交互，这里简化处理
        return True
    
    def _emergency_shutdown(self):
        """紧急关闭"""
        self._logger.critical("Initiating emergency shutdown")
        # 实现紧急关闭逻辑
        # 发送紧急停止信号
        self._signal_manager.emit(SignalType.EMERGENCY_STOP_ACTIVATED, {
            "type": "emergency_shutdown",
            "timestamp": time.time()
        })
    
    def _notify_recovery_callbacks(self, fault_instance: FaultInstance, status: RecoveryStatus):
        """通知恢复回调"""
        for callback in self.recovery_callbacks:
            try:
                callback(fault_instance, status)
            except Exception as e:
                self._logger.error(f"Recovery callback error: {e}")
    
    def add_recovery_callback(self, callback: Callable[[FaultInstance, RecoveryStatus], None]):
        """添加恢复回调"""
        with self._lock:
            self.recovery_callbacks.append(callback)
    
    def get_active_faults(self) -> List[FaultInstance]:
        """获取活动故障列表"""
        with self._lock:
            return list(self.active_faults.values())
    
    def get_fault_history(self, limit: int = 100) -> List[FaultInstance]:
        """获取故障历史"""
        with self._lock:
            return self.fault_history[-limit:] if len(self.fault_history) > limit else self.fault_history

# 全局故障管理器实例
fault_registry = FaultRegistry()
fault_handler = FaultHandler()

def get_fault_registry() -> FaultRegistry:
    """获取全局故障注册表实例"""
    return fault_registry

def get_fault_handler() -> FaultHandler:
    """获取全局故障处理器实例"""
    return fault_handler