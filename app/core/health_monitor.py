"""
健康监控器 - 添加健康检查和监控机制
实现系统组件的健康检查和状态监控
"""

import threading
import time
import logging
import psutil
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# 导入信号管理器和资源管理器
from .signal_manager import SignalManager, SignalType
from .resource_manager import get_resource_manager

@dataclass
class HealthCheckResult:
    """健康检查结果"""
    component: str
    status: str  # "healthy", "warning", "error"
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class HealthChecker(ABC):
    """健康检查器基类"""
    
    @abstractmethod
    def check_health(self) -> HealthCheckResult:
        """执行健康检查"""
        pass

class SystemResourceChecker(HealthChecker):
    """系统资源检查器"""
    
    def __init__(self, check_interval: float = 10.0):
        self.check_interval = check_interval
        self._logger = logging.getLogger(__name__)
    
    def check_health(self) -> HealthCheckResult:
        """检查系统资源使用情况"""
        try:
            # 获取系统资源使用情况
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "memory_available": memory.available,
                "disk_free": disk.free
            }
            
            # 判断健康状态
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = "error"
                message = "系统资源使用率过高"
            elif cpu_percent > 70 or memory.percent > 70 or disk.percent > 80:
                status = "warning"
                message = "系统资源使用率较高"
            else:
                status = "healthy"
                message = "系统资源使用正常"
            
            return HealthCheckResult(
                component="system_resources",
                status=status,
                message=message,
                metrics=metrics
            )
        
        except Exception as e:
            return HealthCheckResult(
                component="system_resources",
                status="error",
                message=f"资源检查失败: {str(e)}"
            )

class ResourceManagerChecker(HealthChecker):
    """资源管理器检查器"""
    
    def __init__(self):
        self._resource_manager = get_resource_manager()
        self._logger = logging.getLogger(__name__)
    
    def check_health(self) -> HealthCheckResult:
        """检查资源管理器状态"""
        try:
            # 获取资源使用统计
            resources = self._resource_manager.list_resources()
            total_resources = len(resources)
            
            # 统计被占用的资源
            occupied_resources = 0
            for resource in resources:
                if resource.current_access_count > 0:
                    occupied_resources += 1
            
            metrics = {
                "total_resources": total_resources,
                "occupied_resources": occupied_resources,
                "utilization_rate": occupied_resources / total_resources if total_resources > 0 else 0
            }
            
            # 判断健康状态
            if occupied_resources == total_resources and total_resources > 0:
                status = "error"
                message = "所有资源都被占用"
            elif occupied_resources / total_resources > 0.8 and total_resources > 0:
                status = "warning"
                message = "资源使用率较高"
            else:
                status = "healthy"
                message = "资源管理正常"
            
            return HealthCheckResult(
                component="resource_manager",
                status=status,
                message=message,
                metrics=metrics
            )
        
        except Exception as e:
            return HealthCheckResult(
                component="resource_manager",
                status="error",
                message=f"资源管理器检查失败: {str(e)}"
            )

class ThreadManagerChecker(HealthChecker):
    """线程管理器检查器"""
    
    def __init__(self):
        from .thread_manager import get_thread_manager
        self._thread_manager = get_thread_manager()
        self._logger = logging.getLogger(__name__)
    
    def check_health(self) -> HealthCheckResult:
        """检查线程管理器状态"""
        try:
            # 获取线程信息
            from .thread_manager import ThreadManager
            thread_manager = ThreadManager()
            
            # 这里简化处理，实际应该检查线程池状态
            metrics = {
                "active_threads": threading.active_count(),
                "managed_threads": len(thread_manager._managed_threads) if hasattr(thread_manager, '_managed_threads') else 0
            }
            
            # 判断健康状态
            if threading.active_count() > 100:
                status = "error"
                message = "线程数量过多"
            elif threading.active_count() > 50:
                status = "warning"
                message = "线程数量较多"
            else:
                status = "healthy"
                message = "线程管理正常"
            
            return HealthCheckResult(
                component="thread_manager",
                status=status,
                message=message,
                metrics=metrics
            )
        
        except Exception as e:
            return HealthCheckResult(
                component="thread_manager",
                status="error",
                message=f"线程管理器检查失败: {str(e)}"
            )

class HealthMonitor:
    """健康监控器"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(HealthMonitor, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, check_interval: float = 10.0):
        # 使用双重检查锁定确保单例
        if hasattr(self, '_initialized'):
            return
            
        with HealthMonitor._lock:
            if hasattr(self, '_initialized'):
                return
                
            self.check_interval = check_interval
            self.checkers: List[HealthChecker] = []
            self.health_status: Dict[str, HealthCheckResult] = {}
            self.callbacks: List[Callable[[Dict[str, HealthCheckResult]], None]] = []
            self._running = False
            self._monitor_thread: Optional[threading.Thread] = None
            self._logger = logging.getLogger(__name__)
            self._signal_manager = SignalManager()
            
            # 添加默认的健康检查器
            self.add_checker(SystemResourceChecker(check_interval))
            self.add_checker(ResourceManagerChecker())
            self.add_checker(ThreadManagerChecker())
            
            self._initialized = True
    
    def add_checker(self, checker: HealthChecker):
        """添加健康检查器"""
        with self._lock:
            self.checkers.append(checker)
            self._logger.info(f"Added health checker for component: {checker.__class__.__name__}")
    
    def remove_checker(self, checker: HealthChecker):
        """移除健康检查器"""
        with self._lock:
            if checker in self.checkers:
                self.checkers.remove(checker)
                self._logger.info(f"Removed health checker for component: {checker.__class__.__name__}")
    
    def add_callback(self, callback: Callable[[Dict[str, HealthCheckResult]], None]):
        """添加状态变化回调"""
        with self._lock:
            self.callbacks.append(callback)
    
    def start_monitoring(self):
        """开始监控"""
        if self._running:
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="HealthMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        self._logger.info("Health monitor started")
    
    def stop_monitoring(self):
        """停止监控"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        self._logger.info("Health monitor stopped")
    
    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                # 执行所有健康检查
                new_status = {}
                
                with self._lock:
                    checkers = self.checkers.copy()
                
                for checker in checkers:
                    try:
                        result = checker.check_health()
                        new_status[result.component] = result
                    except Exception as e:
                        # 检查器本身出错
                        component_name = getattr(checker, '__class__', type(checker)).__name__
                        new_status[component_name] = HealthCheckResult(
                            component=component_name,
                            status="error",
                            message=f"检查器执行失败: {str(e)}"
                        )
                
                # 更新状态并通知回调
                with self._lock:
                    old_status = self.health_status.copy()
                    self.health_status = new_status
                    
                    # 检查是否有状态变化
                    if self._has_status_changed(old_status, new_status):
                        for callback in self.callbacks:
                            try:
                                callback(new_status)
                            except Exception as e:
                                self._logger.error(f"Health monitor callback error: {e}")
                        
                        # 发送系统状态更新信号
                        self._signal_manager.emit(SignalType.SYSTEM_STATUS_UPDATED, {
                            "type": "health_status_changed",
                            "status": new_status
                        })
                
                time.sleep(self.check_interval)
            
            except Exception as e:
                self._logger.error(f"Health monitor loop error: {e}")
                time.sleep(1.0)
    
    def _has_status_changed(self, old_status: Dict[str, HealthCheckResult], 
                           new_status: Dict[str, HealthCheckResult]) -> bool:
        """检查状态是否发生变化"""
        if set(old_status.keys()) != set(new_status.keys()):
            return True
        
        for component in new_status:
            if (component not in old_status or 
                old_status[component].status != new_status[component].status):
                return True
        
        return False
    
    def get_overall_status(self) -> str:
        """获取整体健康状态"""
        with self._lock:
            if not self.health_status:
                return "unknown"
            
            statuses = [result.status for result in self.health_status.values()]
            
            if "error" in statuses:
                return "error"
            elif "warning" in statuses:
                return "warning"
            else:
                return "healthy"
    
    def get_component_status(self, component: str) -> Optional[HealthCheckResult]:
        """获取组件健康状态"""
        with self._lock:
            return self.health_status.get(component)
    
    def get_all_status(self) -> Dict[str, HealthCheckResult]:
        """获取所有组件健康状态"""
        with self._lock:
            return self.health_status.copy()
    
    def is_healthy(self) -> bool:
        """检查系统是否健康"""
        return self.get_overall_status() == "healthy"

# 全局健康监控器实例
health_monitor = HealthMonitor()

def get_health_monitor() -> HealthMonitor:
    """获取全局健康监控器实例"""
    return health_monitor