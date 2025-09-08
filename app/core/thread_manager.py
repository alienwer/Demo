"""
线程管理器 - 优化多线程架构设计
实现线程协调、死锁预防和资源管理
"""

import threading
import queue
import time
import logging
from typing import Dict, Set, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
from contextlib import contextmanager

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """任务定义"""
    id: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: TaskPriority
    timeout: Optional[float] = None
    callback: Optional[Callable] = None

class DeadlockDetector:
    """死锁检测器"""
    
    def __init__(self):
        self._lock_graph: Dict[str, Set[str]] = defaultdict(set)
        self._thread_locks: Dict[str, Set[str]] = defaultdict(set)
        self._lock_owners: Dict[str, str] = {}
        self._detection_lock = threading.RLock()
        self._logger = logging.getLogger(__name__)
    
    def register_lock_request(self, thread_id: str, lock_id: str) -> bool:
        """注册锁请求，检测潜在死锁"""
        with self._detection_lock:
            # 检查是否会形成循环依赖
            if self._would_create_cycle(thread_id, lock_id):
                self._logger.warning(f"Deadlock detected: thread {thread_id} requesting lock {lock_id}")
                return False  # 拒绝锁请求以避免死锁
            
            # 记录锁请求
            self._lock_graph[thread_id].add(lock_id)
            return True
    
    def register_lock_acquired(self, thread_id: str, lock_id: str):
        """注册锁获取"""
        with self._detection_lock:
            self._thread_locks[thread_id].add(lock_id)
            self._lock_owners[lock_id] = thread_id
            # 清理锁请求记录
            self._lock_graph[thread_id].discard(lock_id)
    
    def register_lock_released(self, thread_id: str, lock_id: str):
        """注册锁释放"""
        with self._detection_lock:
            self._thread_locks[thread_id].discard(lock_id)
            if lock_id in self._lock_owners:
                del self._lock_owners[lock_id]
            self._lock_graph[thread_id].discard(lock_id)
    
    def _would_create_cycle(self, thread_id: str, lock_id: str) -> bool:
        """检查是否会创建循环依赖"""
        # 如果锁已被其他线程持有
        if lock_id in self._lock_owners:
            owner_thread = self._lock_owners[lock_id]
            if owner_thread != thread_id:
                # 检查是否存在从owner_thread到thread_id的路径
                return self._has_path(owner_thread, thread_id)
        return False
    
    def _has_path(self, from_thread: str, to_thread: str) -> bool:
        """检查是否存在从from_thread到to_thread的路径"""
        visited = set()
        stack = [from_thread]
        
        while stack:
            current = stack.pop()
            if current == to_thread:
                return True
            
            if current in visited:
                continue
            visited.add(current)
            
            # 添加当前线程等待的锁的所有者
            for lock_id in self._lock_graph[current]:
                if lock_id in self._lock_owners:
                    owner = self._lock_owners[lock_id]
                    if owner not in visited:
                        stack.append(owner)
        
        return False

class TimeoutLockManager:
    """带超时机制的锁管理器"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TimeoutLockManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 使用双重检查锁定确保单例
        if hasattr(self, '_initialized'):
            return
            
        with TimeoutLockManager._lock:
            if hasattr(self, '_initialized'):
                return
                
            self._locks: Dict[str, threading.RLock] = {}
            self._deadlock_detector = DeadlockDetector()
            self._manager_lock = threading.RLock()
            self._logger = logging.getLogger(__name__)
            self._initialized = True
    
    def acquire_lock(self, lock_id: str, timeout: float = 5.0) -> bool:
        """获取锁（带死锁检测和超时）"""
        thread_id = threading.current_thread().name
        
        # 死锁检测
        if not self._deadlock_detector.register_lock_request(thread_id, lock_id):
            raise RuntimeError(f"Lock request would create deadlock: {lock_id}")
        
        try:
            # 获取或创建锁
            with self._manager_lock:
                if lock_id not in self._locks:
                    self._locks[lock_id] = threading.RLock()
                lock = self._locks[lock_id]
            
            # 尝试获取锁
            if lock.acquire(timeout=timeout):
                self._deadlock_detector.register_lock_acquired(thread_id, lock_id)
                return True
            else:
                # 超时，清理请求记录
                self._deadlock_detector.register_lock_released(thread_id, lock_id)
                return False
        
        except Exception:
            # 异常时清理请求记录
            self._deadlock_detector.register_lock_released(thread_id, lock_id)
            raise
    
    def release_lock(self, lock_id: str):
        """释放锁"""
        thread_id = threading.current_thread().name
        
        with self._manager_lock:
            if lock_id in self._locks:
                self._locks[lock_id].release()
                self._deadlock_detector.register_lock_released(thread_id, lock_id)

class ThreadCoordinator:
    """线程协调器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._task_queue = queue.PriorityQueue()
        self._workers: List[threading.Thread] = []
        self._shutdown_event = threading.Event()
        self._results: Dict[str, Any] = {}
        self._result_lock = threading.RLock()
        self._logger = logging.getLogger(__name__)
        
        # 启动工作线程
        self._start_workers()
    
    def _start_workers(self):
        """启动工作线程"""
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"Worker-{i}",
                daemon=True
            )
            worker.start()
            self._workers.append(worker)
    
    def _worker_loop(self):
        """工作线程循环"""
        while not self._shutdown_event.is_set():
            try:
                # 获取任务（带超时）
                priority, task = self._task_queue.get(timeout=1.0)
                
                try:
                    # 执行任务
                    start_time = time.time()
                    result = task.func(*task.args, **task.kwargs)
                    execution_time = time.time() - start_time
                    
                    # 存储结果
                    with self._result_lock:
                        self._results[task.id] = {
                            'result': result,
                            'execution_time': execution_time,
                            'success': True
                        }
                    
                    # 调用回调
                    if task.callback:
                        try:
                            task.callback(result)
                        except Exception as e:
                            self._logger.error(f"Task callback error: {e}")
                
                except Exception as e:
                    # 存储错误结果
                    with self._result_lock:
                        self._results[task.id] = {
                            'error': str(e),
                            'success': False
                        }
                    self._logger.error(f"Task execution error: {e}")
                
                finally:
                    self._task_queue.task_done()
            
            except queue.Empty:
                continue
    
    def submit_task(self, task: Task) -> str:
        """提交任务"""
        # 使用负优先级值实现高优先级优先
        priority_value = -task.priority.value
        self._task_queue.put((priority_value, task))
        self._logger.debug(f"Task {task.id} submitted with priority {task.priority}")
        return task.id
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """获取任务结果"""
        start_time = time.time()
        
        while True:
            with self._result_lock:
                if task_id in self._results:
                    result_data = self._results[task_id]
                    if result_data['success']:
                        return result_data['result']
                    else:
                        raise Exception(result_data['error'])
            
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
            
            time.sleep(0.01)
    
    def shutdown(self, timeout: float = 5.0):
        """关闭协调器"""
        self._shutdown_event.set()
        
        # 等待所有工作线程结束
        for worker in self._workers:
            worker.join(timeout=timeout)
        
        self._logger.info("Thread coordinator shutdown completed")

class ThreadManager:
    """线程管理器 - 统一管理线程相关资源"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ThreadManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 使用双重检查锁定确保单例
        if hasattr(self, '_initialized'):
            return
            
        with ThreadManager._lock:
            if hasattr(self, '_initialized'):
                return
                
            self._coordinator = ThreadCoordinator(max_workers=4)
            self._lock_manager = TimeoutLockManager()
            self._managed_threads: Dict[str, threading.Thread] = {}
            self._thread_lock = threading.RLock()
            self._logger = logging.getLogger(__name__)
            
            self._initialized = True
    
    def create_thread(self, name: str, target: Callable, args: tuple = (), 
                     kwargs: dict = None, daemon: bool = True) -> threading.Thread:
        """创建并管理线程"""
        if kwargs is None:
            kwargs = {}
            
        thread = threading.Thread(
            target=target,
            args=args,
            kwargs=kwargs,
            name=name,
            daemon=daemon
        )
        
        with self._thread_lock:
            self._managed_threads[name] = thread
            
        self._logger.debug(f"Thread {name} created")
        return thread
    
    def start_thread(self, name: str, target: Callable, args: tuple = (), 
                    kwargs: dict = None, daemon: bool = True) -> threading.Thread:
        """创建并启动线程"""
        thread = self.create_thread(name, target, args, kwargs, daemon)
        thread.start()
        self._logger.debug(f"Thread {name} started")
        return thread
    
    def get_thread(self, name: str) -> Optional[threading.Thread]:
        """获取管理的线程"""
        with self._thread_lock:
            return self._managed_threads.get(name)
    
    def stop_thread(self, name: str, timeout: float = 1.0):
        """停止线程（需要线程自己检查停止条件）"""
        with self._thread_lock:
            if name in self._managed_threads:
                del self._managed_threads[name]
        self._logger.debug(f"Thread {name} marked for stop")
    
    def submit_task(self, task: Task) -> str:
        """提交任务到线程池"""
        return self._coordinator.submit_task(task)
    
    def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """获取任务结果"""
        return self._coordinator.get_result(task_id, timeout)
    
    def acquire_lock(self, lock_id: str, timeout: float = 5.0) -> bool:
        """获取锁"""
        return self._lock_manager.acquire_lock(lock_id, timeout)
    
    def release_lock(self, lock_id: str):
        """释放锁"""
        self._lock_manager.release_lock(lock_id)
    
    @contextmanager
    def managed_lock(self, lock_id: str, timeout: float = 5.0):
        """上下文管理器形式的锁"""
        acquired = self.acquire_lock(lock_id, timeout)
        if not acquired:
            raise TimeoutError(f"Failed to acquire lock {lock_id} within {timeout} seconds")
        try:
            yield
        finally:
            self.release_lock(lock_id)
    
    def shutdown(self, timeout: float = 5.0):
        """关闭线程管理器"""
        self._coordinator.shutdown(timeout)
        self._logger.info("Thread manager shutdown completed")

# 全局线程管理器实例
thread_manager = ThreadManager()

def get_thread_manager() -> ThreadManager:
    """获取全局线程管理器实例"""
    return thread_manager