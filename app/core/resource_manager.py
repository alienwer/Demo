"""
资源管理器 - 实现线程安全的资源访问控制
提供资源池、资源锁和访问控制机制
"""

import threading
import time
import logging
from typing import Dict, Any, Optional, Callable, Set, List
from contextlib import contextmanager
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

# 导入线程管理器
from .thread_manager import get_thread_manager

class ResourceType(Enum):
    """资源类型枚举"""
    ROBOT = "robot"
    GRIPPER = "gripper"
    CAMERA = "camera"
    SENSOR = "sensor"
    DATABASE = "database"
    FILE = "file"
    NETWORK = "network"
    MEMORY = "memory"
    CUSTOM = "custom"

@dataclass
class ResourceInfo:
    """资源信息"""
    resource_id: str
    resource_type: ResourceType
    owner_thread: Optional[str] = None
    acquire_time: Optional[float] = None
    usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    max_concurrent_access: int = 1  # 最大并发访问数
    current_access_count: int = 0   # 当前访问计数

class AccessMode(Enum):
    """访问模式"""
    READ = "read"
    WRITE = "write"
    EXCLUSIVE = "exclusive"

class ResourceManager:
    """资源管理器 - 确保线程安全的资源访问控制"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ResourceManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 使用双重检查锁定确保单例
        if hasattr(self, '_initialized'):
            return
            
        with ResourceManager._lock:
            if hasattr(self, '_initialized'):
                return
                
            self._resources: Dict[str, ResourceInfo] = {}
            self._resource_locks: Dict[str, threading.RLock] = {}
            self._access_records: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            self._thread_manager = get_thread_manager()
            self._logger = logging.getLogger(__name__)
            
            # 初始化锁
            self._manager_lock = threading.RLock()
            self._access_lock = threading.RLock()
            
            self._initialized = True
    
    def register_resource(self, resource_id: str, resource_type: ResourceType, 
                         max_concurrent_access: int = 1, metadata: Dict[str, Any] = None) -> bool:
        """注册资源
        
        Args:
            resource_id: 资源ID
            resource_type: 资源类型
            max_concurrent_access: 最大并发访问数
            metadata: 资源元数据
            
        Returns:
            bool: 注册成功返回True，否则返回False
        """
        with self._manager_lock:
            if resource_id in self._resources:
                self._logger.warning(f"Resource {resource_id} already registered")
                return False
            
            if metadata is None:
                metadata = {}
            
            # 创建资源信息
            resource_info = ResourceInfo(
                resource_id=resource_id,
                resource_type=resource_type,
                max_concurrent_access=max_concurrent_access,
                metadata=metadata
            )
            
            # 创建资源锁
            self._resource_locks[resource_id] = threading.RLock()
            
            # 注册资源
            self._resources[resource_id] = resource_info
            
            self._logger.info(f"Resource {resource_id} registered as {resource_type.value}")
            return True
    
    def unregister_resource(self, resource_id: str) -> bool:
        """注销资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            bool: 注销成功返回True，否则返回False
        """
        with self._manager_lock:
            if resource_id not in self._resources:
                self._logger.warning(f"Resource {resource_id} not found")
                return False
            
            # 检查是否有线程正在使用该资源
            resource_info = self._resources[resource_id]
            if resource_info.current_access_count > 0:
                self._logger.warning(f"Resource {resource_id} is still in use")
                return False
            
            # 删除资源和锁
            del self._resources[resource_id]
            if resource_id in self._resource_locks:
                del self._resource_locks[resource_id]
            
            # 清理访问记录
            if resource_id in self._access_records:
                del self._access_records[resource_id]
            
            self._logger.info(f"Resource {resource_id} unregistered")
            return True
    
    def acquire_resource(self, resource_id: str, access_mode: AccessMode = AccessMode.EXCLUSIVE, 
                        timeout: float = 5.0) -> bool:
        """获取资源访问权限
        
        Args:
            resource_id: 资源ID
            access_mode: 访问模式
            timeout: 超时时间（秒）
            
        Returns:
            bool: 获取成功返回True，否则返回False
        """
        thread_id = threading.current_thread().name
        
        # 检查资源是否存在
        if resource_id not in self._resources:
            self._logger.error(f"Resource {resource_id} not registered")
            return False
        
        # 使用线程管理器获取锁
        lock_id = f"resource_{resource_id}"
        if not self._thread_manager.acquire_lock(lock_id, timeout):
            self._logger.warning(f"Failed to acquire lock for resource {resource_id}")
            return False
        
        try:
            with self._access_lock:
                resource_info = self._resources[resource_id]
                
                # 检查并发访问限制
                if access_mode == AccessMode.EXCLUSIVE:
                    # 独占访问需要没有其他访问者
                    if resource_info.current_access_count > 0:
                        return False
                elif access_mode == AccessMode.WRITE:
                    # 写访问需要没有其他写访问者
                    if resource_info.current_access_count > 0:
                        return False
                else:
                    # 读访问需要不超过最大并发数
                    if resource_info.current_access_count >= resource_info.max_concurrent_access:
                        return False
                
                # 更新资源信息
                resource_info.current_access_count += 1
                resource_info.owner_thread = thread_id
                resource_info.acquire_time = time.time()
                resource_info.usage_count += 1
                
                # 记录访问
                access_record = {
                    "thread_id": thread_id,
                    "access_mode": access_mode.value,
                    "acquire_time": time.time(),
                    "timeout": timeout
                }
                self._access_records[resource_id].append(access_record)
                
                self._logger.debug(f"Thread {thread_id} acquired resource {resource_id} in {access_mode.value} mode")
                return True
                
        except Exception as e:
            self._logger.error(f"Error acquiring resource {resource_id}: {e}")
            # 确保释放锁
            self._thread_manager.release_lock(lock_id)
            return False
    
    def release_resource(self, resource_id: str) -> bool:
        """释放资源访问权限
        
        Args:
            resource_id: 资源ID
            
        Returns:
            bool: 释放成功返回True，否则返回False
        """
        thread_id = threading.current_thread().name
        lock_id = f"resource_{resource_id}"
        
        try:
            with self._access_lock:
                if resource_id not in self._resources:
                    self._logger.error(f"Resource {resource_id} not registered")
                    return False
                
                resource_info = self._resources[resource_id]
                
                # 检查是否是当前线程持有资源
                if resource_info.owner_thread != thread_id:
                    self._logger.warning(f"Thread {thread_id} trying to release resource {resource_id} not owned by it")
                    return False
                
                # 更新资源信息
                resource_info.current_access_count -= 1
                if resource_info.current_access_count <= 0:
                    resource_info.current_access_count = 0
                    resource_info.owner_thread = None
                    resource_info.acquire_time = None
                
                # 更新访问记录
                if self._access_records[resource_id]:
                    last_record = self._access_records[resource_id][-1]
                    last_record["release_time"] = time.time()
                    last_record["duration"] = last_record["release_time"] - last_record["acquire_time"]
                
                self._logger.debug(f"Thread {thread_id} released resource {resource_id}")
                return True
                
        except Exception as e:
            self._logger.error(f"Error releasing resource {resource_id}: {e}")
            return False
        finally:
            # 释放锁
            self._thread_manager.release_lock(lock_id)
    
    @contextmanager
    def managed_resource(self, resource_id: str, access_mode: AccessMode = AccessMode.EXCLUSIVE, 
                        timeout: float = 5.0):
        """上下文管理器形式的资源访问
        
        Args:
            resource_id: 资源ID
            access_mode: 访问模式
            timeout: 超时时间（秒）
        """
        acquired = self.acquire_resource(resource_id, access_mode, timeout)
        if not acquired:
            raise RuntimeError(f"Failed to acquire resource {resource_id}")
        
        try:
            yield self._resources[resource_id]
        finally:
            self.release_resource(resource_id)
    
    def get_resource_info(self, resource_id: str) -> Optional[ResourceInfo]:
        """获取资源信息
        
        Args:
            resource_id: 资源ID
            
        Returns:
            ResourceInfo: 资源信息，如果资源不存在返回None
        """
        with self._manager_lock:
            return self._resources.get(resource_id)
    
    def list_resources(self) -> List[ResourceInfo]:
        """列出所有资源
        
        Returns:
            List[ResourceInfo]: 资源信息列表
        """
        with self._manager_lock:
            return list(self._resources.values())
    
    def get_access_records(self, resource_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取资源访问记录
        
        Args:
            resource_id: 资源ID
            limit: 记录数量限制
            
        Returns:
            List[Dict[str, Any]]: 访问记录列表
        """
        with self._manager_lock:
            records = self._access_records.get(resource_id, [])
            return records[-limit:] if len(records) > limit else records
    
    def is_resource_available(self, resource_id: str) -> bool:
        """检查资源是否可用
        
        Args:
            resource_id: 资源ID
            
        Returns:
            bool: 资源可用返回True，否则返回False
        """
        with self._manager_lock:
            if resource_id not in self._resources:
                return False
            
            resource_info = self._resources[resource_id]
            return resource_info.current_access_count == 0
    
    def get_resource_usage_stats(self, resource_id: str) -> Dict[str, Any]:
        """获取资源使用统计信息
        
        Args:
            resource_id: 资源ID
            
        Returns:
            Dict[str, Any]: 使用统计信息
        """
        with self._manager_lock:
            if resource_id not in self._resources:
                return {}
            
            resource_info = self._resources[resource_id]
            records = self._access_records.get(resource_id, [])
            
            total_access_time = 0.0
            access_count = 0
            for record in records:
                if "duration" in record:
                    total_access_time += record["duration"]
                    access_count += 1
            
            avg_access_time = total_access_time / access_count if access_count > 0 else 0.0
            
            return {
                "resource_id": resource_id,
                "current_access_count": resource_info.current_access_count,
                "usage_count": resource_info.usage_count,
                "average_access_time": avg_access_time,
                "total_access_time": total_access_time,
                "access_records_count": len(records)
            }

# 全局资源管理器实例
resource_manager = ResourceManager()

def get_resource_manager() -> ResourceManager:
    """获取全局资源管理器实例"""
    return resource_manager