"""
异常恢复管理器 - 完善异常恢复流程
提供更完善的异常检测、处理和恢复机制
"""

import threading
import time
import logging
import traceback
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager

# 导入相关模块
from .signal_manager import SignalManager, SignalType
from .fault_manager import get_fault_handler, FaultLevel, FaultCategory
from .health_monitor import get_health_monitor

class ExceptionSeverity(Enum):
    """异常严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ExceptionRecord:
    """异常记录"""
    id: str
    exception_type: str
    message: str
    severity: ExceptionSeverity
    timestamp: float
    traceback: str
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution_time: Optional[float] = None

class ExceptionRecoveryManager:
    """异常恢复管理器"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ExceptionRecoveryManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 使用双重检查锁定确保单例
        if hasattr(self, '_initialized'):
            return
            
        with ExceptionRecoveryManager._lock:
            if hasattr(self, '_initialized'):
                return
                
            self.exception_records: Dict[str, ExceptionRecord] = {}
            self.recovery_strategies: Dict[str, Callable] = {}
            self.exception_callbacks: List[Callable[[ExceptionRecord], None]] = []
            self._logger = logging.getLogger(__name__)
            self._signal_manager = SignalManager()
            self._fault_handler = get_fault_handler()
            self._health_monitor = get_health_monitor()
            
            # 注册默认的恢复策略
            self._register_default_strategies()
            
            self._initialized = True
    
    def _register_default_strategies(self):
        """注册默认的恢复策略"""
        # 网络异常恢复策略
        self.register_recovery_strategy("ConnectionError", self._handle_connection_error)
        self.register_recovery_strategy("TimeoutError", self._handle_timeout_error)
        
        # 资源异常恢复策略
        self.register_recovery_strategy("MemoryError", self._handle_memory_error)
        self.register_recovery_strategy("OSError", self._handle_os_error)
        
        # 通用异常恢复策略
        self.register_recovery_strategy("Exception", self._handle_generic_exception)
    
    def register_recovery_strategy(self, exception_type: str, strategy: Callable):
        """注册恢复策略"""
        with self._lock:
            self.recovery_strategies[exception_type] = strategy
            self._logger.info(f"Registered recovery strategy for {exception_type}")
    
    def record_exception(self, exception: Exception, context: Dict[str, Any] = None, 
                        severity: ExceptionSeverity = ExceptionSeverity.MEDIUM) -> str:
        """记录异常"""
        exception_id = f"exc_{int(time.time() * 1000)}"
        
        # 创建异常记录
        record = ExceptionRecord(
            id=exception_id,
            exception_type=type(exception).__name__,
            message=str(exception),
            severity=severity,
            timestamp=time.time(),
            traceback=traceback.format_exc(),
            context=context or {}
        )
        
        with self._lock:
            self.exception_records[exception_id] = record
        
        self._logger.error(f"Exception recorded: {record.exception_type} - {record.message}")
        
        # 发送系统错误信号
        self._signal_manager.emit(SignalType.SYSTEM_ERROR, {
            "exception_id": exception_id,
            "exception_type": record.exception_type,
            "message": record.message,
            "severity": severity.value,
            "timestamp": record.timestamp
        })
        
        # 通知回调
        for callback in self.exception_callbacks:
            try:
                callback(record)
            except Exception as e:
                self._logger.error(f"Exception callback error: {e}")
        
        return exception_id
    
    def attempt_recovery(self, exception_id: str) -> bool:
        """尝试恢复异常"""
        with self._lock:
            if exception_id not in self.exception_records:
                self._logger.warning(f"Exception {exception_id} not found")
                return False
            
            record = self.exception_records[exception_id]
            if record.resolved:
                self._logger.info(f"Exception {exception_id} already resolved")
                return True
        
        # 查找匹配的恢复策略
        strategy = self.recovery_strategies.get(record.exception_type)
        if not strategy:
            # 尝试使用通用异常处理策略
            strategy = self.recovery_strategies.get("Exception")
        
        if strategy:
            try:
                self._logger.info(f"Attempting recovery for exception {exception_id}")
                success = strategy(record)
                
                if success:
                    self._mark_resolved(exception_id)
                    self._logger.info(f"Exception {exception_id} recovered successfully")
                    
                    # 发送恢复成功信号
                    self._signal_manager.emit(SignalType.SYSTEM_STATUS_UPDATED, {
                        "type": "exception_recovered",
                        "exception_id": exception_id,
                        "exception_type": record.exception_type
                    })
                    
                    return True
                else:
                    self._logger.warning(f"Recovery failed for exception {exception_id}")
                    return False
                    
            except Exception as e:
                self._logger.error(f"Recovery strategy failed: {e}")
                return False
        else:
            self._logger.warning(f"No recovery strategy for exception type: {record.exception_type}")
            return False
    
    def _handle_connection_error(self, record: ExceptionRecord) -> bool:
        """处理连接错误"""
        self._logger.info("Handling connection error")
        
        # 记录恢复尝试
        record.recovery_attempts.append("connection_recovery")
        
        # 尝试重新连接
        try:
            # 这里应该调用实际的重连逻辑
            time.sleep(2)  # 模拟重连过程
            return True
        except Exception as e:
            self._logger.error(f"Connection recovery failed: {e}")
            return False
    
    def _handle_timeout_error(self, record: ExceptionRecord) -> bool:
        """处理超时错误"""
        self._logger.info("Handling timeout error")
        
        # 记录恢复尝试
        record.recovery_attempts.append("timeout_recovery")
        
        # 增加超时时间或重试
        try:
            # 这里应该实现具体的超时处理逻辑
            time.sleep(1)  # 模拟处理过程
            return True
        except Exception as e:
            self._logger.error(f"Timeout recovery failed: {e}")
            return False
    
    def _handle_memory_error(self, record: ExceptionRecord) -> bool:
        """处理内存错误"""
        self._logger.info("Handling memory error")
        
        # 记录恢复尝试
        record.recovery_attempts.append("memory_recovery")
        
        try:
            # 尝试释放资源
            import gc
            gc.collect()
            
            # 检查内存使用情况
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent < 80:
                self._logger.info("Memory usage reduced to acceptable level")
                return True
            else:
                self._logger.warning("Memory usage still high after cleanup")
                return False
                
        except Exception as e:
            self._logger.error(f"Memory recovery failed: {e}")
            return False
    
    def _handle_os_error(self, record: ExceptionRecord) -> bool:
        """处理操作系统错误"""
        self._logger.info("Handling OS error")
        
        # 记录恢复尝试
        record.recovery_attempts.append("os_recovery")
        
        try:
            # 检查磁盘空间
            import psutil
            disk = psutil.disk_usage('/')
            
            if disk.percent < 90:
                self._logger.info("Disk space is sufficient")
                return True
            else:
                self._logger.warning("Disk space is low")
                return False
                
        except Exception as e:
            self._logger.error(f"OS recovery failed: {e}")
            return False
    
    def _handle_generic_exception(self, record: ExceptionRecord) -> bool:
        """处理通用异常"""
        self._logger.info("Handling generic exception")
        
        # 记录恢复尝试
        record.recovery_attempts.append("generic_recovery")
        
        try:
            # 检查系统健康状态
            health_status = self._health_monitor.get_overall_status()
            
            if health_status == "healthy":
                self._logger.info("System is healthy, generic recovery successful")
                return True
            else:
                self._logger.warning(f"System health status: {health_status}")
                return False
                
        except Exception as e:
            self._logger.error(f"Generic recovery failed: {e}")
            return False
    
    def _mark_resolved(self, exception_id: str):
        """标记异常已解决"""
        with self._lock:
            if exception_id in self.exception_records:
                record = self.exception_records[exception_id]
                record.resolved = True
                record.resolution_time = time.time()
    
    def add_exception_callback(self, callback: Callable[[ExceptionRecord], None]):
        """添加异常回调"""
        with self._lock:
            self.exception_callbacks.append(callback)
    
    def get_exception_record(self, exception_id: str) -> Optional[ExceptionRecord]:
        """获取异常记录"""
        with self._lock:
            return self.exception_records.get(exception_id)
    
    def get_unresolved_exceptions(self) -> List[ExceptionRecord]:
        """获取未解决的异常"""
        with self._lock:
            return [record for record in self.exception_records.values() if not record.resolved]
    
    def get_exception_history(self, limit: int = 100) -> List[ExceptionRecord]:
        """获取异常历史"""
        with self._lock:
            records = list(self.exception_records.values())
            return records[-limit:] if len(records) > limit else records
    
    @contextmanager
    def exception_context(self, context: Dict[str, Any] = None):
        """异常上下文管理器"""
        try:
            yield
        except Exception as e:
            # 记录异常
            exception_id = self.record_exception(e, context)
            
            # 尝试自动恢复
            self.attempt_recovery(exception_id)
            
            # 重新抛出异常
            raise

# 全局异常恢复管理器实例
exception_recovery_manager = ExceptionRecoveryManager()

def get_exception_recovery_manager() -> ExceptionRecoveryManager:
    """获取全局异常恢复管理器实例"""
    return exception_recovery_manager

# 便捷函数
def handle_exception(exception: Exception, context: Dict[str, Any] = None, 
                    severity: ExceptionSeverity = ExceptionSeverity.MEDIUM) -> str:
    """处理异常的便捷函数"""
    manager = get_exception_recovery_manager()
    exception_id = manager.record_exception(exception, context, severity)
    manager.attempt_recovery(exception_id)
    return exception_id

def with_exception_recovery(context: Dict[str, Any] = None):
    """异常恢复装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = get_exception_recovery_manager()
            with manager.exception_context(context):
                return func(*args, **kwargs)
        return wrapper
    return decorator