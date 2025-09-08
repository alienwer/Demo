'''
Author: LK
Date: 2025-01-XX XX:XX:XX
LastEditTime: 2025-01-XX XX:XX:XX
LastEditors: LK
FilePath: /Demo/app/control/scheduler_manager.py
'''

import threading
import time
import json
from typing import Dict, Any, List, Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

# 导入线程管理器和资源管理器
from ..core.thread_manager import get_thread_manager
from ..core.resource_manager import get_resource_manager, ResourceType, AccessMode

try:
    from flexiv import Scheduler, SchedulerStates, TaskInfo, TaskStatus
except ImportError:
    # 仿真模式下的模拟类
    class Scheduler:
        def __init__(self, robot_ip: str):
            self.robot_ip = robot_ip
            self.connected = False
            self.tasks = {}
            self.current_task_id = None
        
        def connect(self) -> bool:
            self.connected = True
            return True
        
        def disconnect(self):
            self.connected = False
        
        def is_connected(self) -> bool:
            return self.connected
        
        def get_scheduler_states(self) -> 'SchedulerStates':
            return SchedulerStates()
        
        def add_task(self, task_info: 'TaskInfo') -> str:
            task_id = f"task_{len(self.tasks) + 1}"
            self.tasks[task_id] = task_info
            return task_id
        
        def remove_task(self, task_id: str) -> bool:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
            return False
        
        def start_task(self, task_id: str) -> bool:
            if task_id in self.tasks:
                self.current_task_id = task_id
                return True
            return False
        
        def stop_task(self, task_id: str) -> bool:
            if task_id == self.current_task_id:
                self.current_task_id = None
                return True
            return False
        
        def pause_task(self, task_id: str) -> bool:
            return task_id in self.tasks
        
        def resume_task(self, task_id: str) -> bool:
            return task_id in self.tasks
        
        def get_task_list(self) -> List[str]:
            return list(self.tasks.keys())
        
        def get_task_info(self, task_id: str) -> Optional['TaskInfo']:
            return self.tasks.get(task_id)
        
        def get_task_status(self, task_id: str) -> 'TaskStatus':
            return TaskStatus()
        
        def clear_all_tasks(self) -> bool:
            self.tasks.clear()
            self.current_task_id = None
            return True
        
        def set_task_priority(self, task_id: str, priority: int) -> bool:
            return task_id in self.tasks
        
        def schedule_task(self, task_id: str, start_time: float) -> bool:
            return task_id in self.tasks
    
    class SchedulerStates:
        def __init__(self):
            self.scheduler_enabled = True
            self.current_task_id = ""
            self.current_task_status = "idle"
            self.task_queue_size = 0
            self.total_tasks = 0
            self.completed_tasks = 0
            self.failed_tasks = 0
            self.scheduler_mode = "auto"
            self.last_error_code = 0
            self.last_error_message = ""
    
    class TaskInfo:
        def __init__(self, name: str = "", description: str = "", 
                     task_type: str = "primitive", parameters: Dict = None):
            self.name = name
            self.description = description
            self.task_type = task_type
            self.parameters = parameters or {}
            self.priority = 0
            self.max_retries = 0
            self.timeout = 0.0
            self.dependencies = []
            self.created_time = time.time()
    
    class TaskStatus:
        def __init__(self):
            self.task_id = ""
            self.status = "idle"  # idle, running, paused, completed, failed
            self.progress = 0.0
            self.start_time = 0.0
            self.end_time = 0.0
            self.execution_time = 0.0
            self.retry_count = 0
            self.error_code = 0
            self.error_message = ""
            self.result = {}

class TaskType(Enum):
    """任务类型"""
    PRIMITIVE = "primitive"
    PLAN = "plan"
    SCRIPT = "script"
    CUSTOM = "custom"
    MAINTENANCE = "maintenance"
    CALIBRATION = "calibration"

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10

class SchedulerMode(Enum):
    """调度器模式"""
    MANUAL = "manual"  # 手动模式
    AUTO = "auto"      # 自动模式
    BATCH = "batch"    # 批处理模式
    REALTIME = "realtime"  # 实时模式

@dataclass
class TaskDefinition:
    """任务定义"""
    name: str
    description: str
    task_type: TaskType
    parameters: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 0
    timeout: float = 0.0  # 超时时间（秒），0表示无超时
    dependencies: List[str] = None  # 依赖的任务ID列表
    schedule_time: Optional[float] = None  # 计划执行时间
    repeat_interval: Optional[float] = None  # 重复间隔（秒）
    repeat_count: int = 1  # 重复次数，-1表示无限重复
    enabled: bool = True
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
    
    def to_task_info(self) -> 'TaskInfo':
        """转换为TaskInfo对象"""
        task_info = TaskInfo(
            name=self.name,
            description=self.description,
            task_type=self.task_type.value,
            parameters=self.parameters
        )
        task_info.priority = self.priority.value
        task_info.max_retries = self.max_retries
        task_info.timeout = self.timeout
        task_info.dependencies = self.dependencies.copy()
        return task_info

@dataclass
class TaskExecution:
    """任务执行记录"""
    task_id: str
    task_name: str
    status: str
    start_time: float
    end_time: Optional[float] = None
    execution_time: float = 0.0
    progress: float = 0.0
    retry_count: int = 0
    error_code: int = 0
    error_message: str = ""
    result: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.result is None:
            self.result = {}

class SchedulerManager(QObject):
    """任务调度管理器
    
    负责管理机器人任务调度，包括：
    - 任务定义和管理
    - 任务队列调度
    - 任务执行监控
    - 任务依赖处理
    - 定时任务
    - 重复任务
    - 任务优先级
    - 任务状态跟踪
    """
    
    # 信号定义
    scheduler_states_updated = pyqtSignal(object)  # SchedulerStates
    task_added = pyqtSignal(str, object)  # task_id, TaskDefinition
    task_removed = pyqtSignal(str)  # task_id
    task_started = pyqtSignal(str, object)  # task_id, TaskExecution
    task_completed = pyqtSignal(str, object)  # task_id, TaskExecution
    task_failed = pyqtSignal(str, object)  # task_id, TaskExecution
    task_paused = pyqtSignal(str)  # task_id
    task_resumed = pyqtSignal(str)  # task_id
    task_progress_updated = pyqtSignal(str, float)  # task_id, progress
    scheduler_mode_changed = pyqtSignal(str)  # mode
    scheduler_status_changed = pyqtSignal(str)  # status_message
    
    def __init__(self, robot=None, hardware=True, robot_ip: str = "192.168.2.100", parent=None):
        super().__init__(parent)
        
        self.robot = robot
        self.hardware = hardware
        self.robot_ip = robot_ip
        self.scheduler = None
        self.connected = False
        
        # 调度器状态
        self.current_states = None
        self.scheduler_mode = SchedulerMode.AUTO
        self.scheduler_enabled = True
        
        # 任务管理
        self.task_definitions = {}  # task_id -> TaskDefinition
        self.task_executions = {}   # task_id -> TaskExecution
        self.task_queue = []        # 待执行任务队列
        self.running_tasks = {}     # 正在执行的任务
        self.completed_tasks = {}   # 已完成的任务
        self.failed_tasks = {}      # 失败的任务
        
        # 定时任务
        self.scheduled_tasks = {}   # task_id -> schedule_time
        self.recurring_tasks = {}   # task_id -> (interval, next_time, count)
        
        # 监控线程
        self.monitor_thread = None
        self.monitor_lock = threading.Lock()
        self.stop_monitoring = threading.Event()
        
        # 调度线程
        self.scheduler_thread = None
        self.scheduler_lock = threading.Lock()
        self.stop_scheduling = threading.Event()
        
        # 初始化线程管理器和资源管理器
        self.thread_manager = get_thread_manager()
        self.resource_manager = get_resource_manager()
        
        # 注册调度器资源
        self.resource_manager.register_resource(
            resource_id=f"scheduler_{self.robot_ip}",
            resource_type=ResourceType.CUSTOM,
            metadata={
                "robot_ip": self.robot_ip,
                "type": "scheduler"
            }
        )
        
        # 定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        
        # 任务回调
        self.task_callbacks = {}  # task_type -> callback_function
        
        # 初始化
        self.init_scheduler()
    
    def init_scheduler(self):
        """初始化调度器"""
        try:
            self.scheduler = Scheduler(self.robot_ip)
            self.scheduler_status_changed.emit("任务调度器已初始化")
        except Exception as e:
            self.scheduler_status_changed.emit(f"任务调度器初始化失败: {str(e)}")
    
    def connect_scheduler(self) -> bool:
        """连接调度器"""
        try:
            if not self.scheduler:
                self.init_scheduler()
            
            if self.scheduler and self.scheduler.connect():
                self.connected = True
                self.scheduler_status_changed.emit("任务调度器已连接")
                
                # 获取初始状态
                self.update_scheduler_states()
                
                return True
            else:
                self.scheduler_status_changed.emit("任务调度器连接失败")
                return False
                
        except Exception as e:
            self.scheduler_status_changed.emit(f"任务调度器连接错误: {str(e)}")
            return False
    
    def disconnect_scheduler(self):
        """断开调度器连接"""
        try:
            self.stop_monitoring_scheduler()
            self.stop_task_scheduling()
            
            if self.scheduler and self.connected:
                self.scheduler.disconnect()
                self.connected = False
                self.scheduler_status_changed.emit("任务调度器已断开")
                
        except Exception as e:
            self.scheduler_status_changed.emit(f"任务调度器断开错误: {str(e)}")
    
    def is_connected(self) -> bool:
        """检查调度器连接状态"""
        return self.connected and self.scheduler and self.scheduler.is_connected()
    
    def start_monitoring_scheduler(self, interval: float = 0.5):
        """开始调度器监控"""
        if not self.is_connected():
            self.scheduler_status_changed.emit("调度器未连接，无法开始监控")
            return
        
        self.stop_monitoring.clear()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(
            target=self._scheduler_monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
        # 启动状态定时器
        self.status_timer.start(int(interval * 1000))
        
        self.scheduler_status_changed.emit("调度器监控已启动")
    
    def stop_monitoring_scheduler(self):
        """停止调度器监控"""
        self.stop_monitoring.set()
        
        # 停止定时器
        self.status_timer.stop()
        
        # 等待监控线程结束
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        
        self.scheduler_status_changed.emit("调度器监控已停止")
    
    def start_task_scheduling(self, interval: float = 0.1):
        """开始任务调度"""
        if not self.scheduler_enabled:
            return
        
        self.stop_scheduling.clear()
        
        # 启动调度线程
        self.scheduler_thread = threading.Thread(
            target=self._task_scheduler_loop,
            args=(interval,),
            daemon=True
        )
        self.scheduler_thread.start()
        
        self.scheduler_status_changed.emit("任务调度已启动")
    
    def stop_task_scheduling(self):
        """停止任务调度"""
        self.stop_scheduling.set()
        
        # 等待调度线程结束
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=1.0)
        
        self.scheduler_status_changed.emit("任务调度已停止")
    
    def _scheduler_monitor_loop(self, interval: float):
        """调度器监控循环"""
        while not self.stop_monitoring.is_set():
            try:
                with self.monitor_lock:
                    if self.is_connected():
                        self.update_scheduler_states()
                        self.update_task_statuses()
                
                time.sleep(interval)
                
            except Exception as e:
                self.scheduler_status_changed.emit(f"调度器监控错误: {str(e)}")
                time.sleep(interval)
    
    def _task_scheduler_loop(self, interval: float):
        """任务调度循环"""
        while not self.stop_scheduling.is_set():
            try:
                with self.scheduler_lock:
                    if self.scheduler_enabled:
                        self.process_scheduled_tasks()
                        self.process_recurring_tasks()
                        self.process_task_queue()
                
                time.sleep(interval)
                
            except Exception as e:
                self.scheduler_status_changed.emit(f"任务调度错误: {str(e)}")
                time.sleep(interval)
    
    def update_scheduler_states(self):
        """更新调度器状态"""
        try:
            if not self.is_connected():
                return
            
            states = self.scheduler.get_scheduler_states()
            self.current_states = states
            self.scheduler_states_updated.emit(states)
            
        except Exception as e:
            self.scheduler_status_changed.emit(f"获取调度器状态失败: {str(e)}")
    
    def update_task_statuses(self):
        """更新任务状态"""
        try:
            if not self.is_connected():
                return
            
            # 更新正在执行的任务状态
            for task_id in list(self.running_tasks.keys()):
                status = self.scheduler.get_task_status(task_id)
                if status:
                    execution = self.task_executions.get(task_id)
                    if execution:
                        execution.status = status.status
                        execution.progress = status.progress
                        execution.execution_time = status.execution_time
                        execution.retry_count = status.retry_count
                        execution.error_code = status.error_code
                        execution.error_message = status.error_message
                        execution.result = status.result
                        
                        # 发送进度更新信号
                        self.task_progress_updated.emit(task_id, status.progress)
                        
                        # 检查任务是否完成
                        if status.status == "completed":
                            execution.end_time = time.time()
                            self.running_tasks.pop(task_id, None)
                            self.completed_tasks[task_id] = execution
                            self.task_completed.emit(task_id, execution)
                        
                        elif status.status == "failed":
                            execution.end_time = time.time()
                            self.running_tasks.pop(task_id, None)
                            self.failed_tasks[task_id] = execution
                            self.task_failed.emit(task_id, execution)
            
        except Exception as e:
            self.scheduler_status_changed.emit(f"更新任务状态失败: {str(e)}")
    
    def add_task(self, task_def: TaskDefinition) -> str:
        """添加任务"""
        try:
            if not self.is_connected():
                self.scheduler_status_changed.emit("调度器未连接，无法添加任务")
                return ""
            
            # 转换为TaskInfo
            task_info = task_def.to_task_info()
            
            # 添加到调度器
            task_id = self.scheduler.add_task(task_info)
            if task_id:
                # 保存任务定义
                self.task_definitions[task_id] = task_def
                
                # 处理定时任务
                if task_def.schedule_time:
                    self.scheduled_tasks[task_id] = task_def.schedule_time
                
                # 处理重复任务
                if task_def.repeat_interval and task_def.repeat_count != 0:
                    next_time = task_def.schedule_time or time.time()
                    self.recurring_tasks[task_id] = (
                        task_def.repeat_interval, 
                        next_time, 
                        task_def.repeat_count
                    )
                
                # 如果没有计划时间且启用，添加到队列
                if not task_def.schedule_time and task_def.enabled:
                    self.add_to_queue(task_id)
                
                self.task_added.emit(task_id, task_def)
                self.scheduler_status_changed.emit(f"任务已添加: {task_def.name}")
                
                return task_id
            else:
                self.scheduler_status_changed.emit(f"添加任务失败: {task_def.name}")
                return ""
                
        except Exception as e:
            self.scheduler_status_changed.emit(f"添加任务错误: {str(e)}")
            return ""
    
    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        try:
            if not self.is_connected():
                return False
            
            # 从调度器移除
            success = self.scheduler.remove_task(task_id)
            if success:
                # 清理本地数据
                self.task_definitions.pop(task_id, None)
                self.task_executions.pop(task_id, None)
                self.scheduled_tasks.pop(task_id, None)
                self.recurring_tasks.pop(task_id, None)
                self.running_tasks.pop(task_id, None)
                self.completed_tasks.pop(task_id, None)
                self.failed_tasks.pop(task_id, None)
                
                # 从队列移除
                if task_id in self.task_queue:
                    self.task_queue.remove(task_id)
                
                self.task_removed.emit(task_id)
                self.scheduler_status_changed.emit(f"任务已移除: {task_id}")
            
            return success
            
        except Exception as e:
            self.scheduler_status_changed.emit(f"移除任务错误: {str(e)}")
            return False
    
    def start_task(self, task_id: str) -> bool:
        """启动任务"""
        try:
            if not self.is_connected():
                return False
            
            if task_id not in self.task_definitions:
                self.scheduler_status_changed.emit(f"任务不存在: {task_id}")
                return False
            
            # 检查依赖
            if not self.check_task_dependencies(task_id):
                self.scheduler_status_changed.emit(f"任务依赖未满足: {task_id}")
                return False
            
            # 启动任务
            success = self.scheduler.start_task(task_id)
            if success:
                # 创建执行记录
                task_def = self.task_definitions[task_id]
                execution = TaskExecution(
                    task_id=task_id,
                    task_name=task_def.name,
                    status="running",
                    start_time=time.time()
                )
                
                self.task_executions[task_id] = execution
                self.running_tasks[task_id] = execution
                
                # 从队列移除
                if task_id in self.task_queue:
                    self.task_queue.remove(task_id)
                
                self.task_started.emit(task_id, execution)
                self.scheduler_status_changed.emit(f"任务已启动: {task_def.name}")
            
            return success
            
        except Exception as e:
            self.scheduler_status_changed.emit(f"启动任务错误: {str(e)}")
            return False
    
    def stop_task(self, task_id: str) -> bool:
        """停止任务"""
        try:
            if not self.is_connected():
                return False
            
            success = self.scheduler.stop_task(task_id)
            if success:
                # 更新执行记录
                execution = self.task_executions.get(task_id)
                if execution:
                    execution.status = "stopped"
                    execution.end_time = time.time()
                
                self.running_tasks.pop(task_id, None)
                self.scheduler_status_changed.emit(f"任务已停止: {task_id}")
            
            return success
            
        except Exception as e:
            self.scheduler_status_changed.emit(f"停止任务错误: {str(e)}")
            return False
    
    def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        try:
            if not self.is_connected():
                return False
            
            success = self.scheduler.pause_task(task_id)
            if success:
                execution = self.task_executions.get(task_id)
                if execution:
                    execution.status = "paused"
                
                self.task_paused.emit(task_id)
                self.scheduler_status_changed.emit(f"任务已暂停: {task_id}")
            
            return success
            
        except Exception as e:
            self.scheduler_status_changed.emit(f"暂停任务错误: {str(e)}")
            return False
    
    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        try:
            if not self.is_connected():
                return False
            
            success = self.scheduler.resume_task(task_id)
            if success:
                execution = self.task_executions.get(task_id)
                if execution:
                    execution.status = "running"
                
                self.task_resumed.emit(task_id)
                self.scheduler_status_changed.emit(f"任务已恢复: {task_id}")
            
            return success
            
        except Exception as e:
            self.scheduler_status_changed.emit(f"恢复任务错误: {str(e)}")
            return False
    
    def add_to_queue(self, task_id: str):
        """添加任务到队列"""
        if task_id not in self.task_queue:
            # 按优先级插入
            task_def = self.task_definitions.get(task_id)
            if task_def:
                priority = task_def.priority.value
                
                # 找到合适的插入位置
                insert_pos = len(self.task_queue)
                for i, queued_task_id in enumerate(self.task_queue):
                    queued_task_def = self.task_definitions.get(queued_task_id)
                    if queued_task_def and queued_task_def.priority.value < priority:
                        insert_pos = i
                        break
                
                self.task_queue.insert(insert_pos, task_id)
    
    def process_scheduled_tasks(self):
        """处理定时任务"""
        current_time = time.time()
        
        for task_id, schedule_time in list(self.scheduled_tasks.items()):
            if current_time >= schedule_time:
                # 时间到了，添加到队列
                self.add_to_queue(task_id)
                self.scheduled_tasks.pop(task_id, None)
    
    def process_recurring_tasks(self):
        """处理重复任务"""
        current_time = time.time()
        
        for task_id, (interval, next_time, count) in list(self.recurring_tasks.items()):
            if current_time >= next_time:
                # 时间到了，添加到队列
                self.add_to_queue(task_id)
                
                # 更新下次执行时间
                if count > 0:
                    count -= 1
                    if count > 0:
                        self.recurring_tasks[task_id] = (interval, next_time + interval, count)
                    else:
                        self.recurring_tasks.pop(task_id, None)
                elif count == -1:  # 无限重复
                    self.recurring_tasks[task_id] = (interval, next_time + interval, -1)
    
    def process_task_queue(self):
        """处理任务队列"""
        if not self.task_queue:
            return
        
        # 在自动模式下执行队列中的任务
        if self.scheduler_mode == SchedulerMode.AUTO:
            # 检查是否有空闲的执行槽位
            max_concurrent = 3  # 最大并发任务数
            if len(self.running_tasks) < max_concurrent:
                task_id = self.task_queue[0]
                if self.check_task_dependencies(task_id):
                    self.start_task(task_id)
    
    def check_task_dependencies(self, task_id: str) -> bool:
        """检查任务依赖"""
        task_def = self.task_definitions.get(task_id)
        if not task_def or not task_def.dependencies:
            return True
        
        # 检查所有依赖任务是否已完成
        for dep_task_id in task_def.dependencies:
            if dep_task_id not in self.completed_tasks:
                return False
        
        return True
    
    def set_scheduler_mode(self, mode: SchedulerMode):
        """设置调度器模式"""
        self.scheduler_mode = mode
        self.scheduler_mode_changed.emit(mode.value)
        self.scheduler_status_changed.emit(f"调度器模式已设置为: {mode.value}")
    
    def enable_scheduler(self, enabled: bool):
        """启用/禁用调度器"""
        self.scheduler_enabled = enabled
        
        if enabled:
            self.start_task_scheduling()
        else:
            self.stop_task_scheduling()
        
        status = "启用" if enabled else "禁用"
        self.scheduler_status_changed.emit(f"调度器已{status}")
    
    def clear_all_tasks(self) -> bool:
        """清除所有任务"""
        try:
            if self.is_connected():
                success = self.scheduler.clear_all_tasks()
            else:
                success = True
            
            if success:
                # 清理本地数据
                self.task_definitions.clear()
                self.task_executions.clear()
                self.task_queue.clear()
                self.running_tasks.clear()
                self.completed_tasks.clear()
                self.failed_tasks.clear()
                self.scheduled_tasks.clear()
                self.recurring_tasks.clear()
                
                self.scheduler_status_changed.emit("所有任务已清除")
            
            return success
            
        except Exception as e:
            self.scheduler_status_changed.emit(f"清除任务错误: {str(e)}")
            return False
    
    def get_task_list(self) -> List[str]:
        """获取任务列表"""
        return list(self.task_definitions.keys())
    
    def get_task_definition(self, task_id: str) -> Optional[TaskDefinition]:
        """获取任务定义"""
        return self.task_definitions.get(task_id)
    
    def get_task_execution(self, task_id: str) -> Optional[TaskExecution]:
        """获取任务执行记录"""
        return self.task_executions.get(task_id)
    
    def get_scheduler_summary(self) -> Dict[str, Any]:
        """获取调度器摘要"""
        return {
            "connected": self.is_connected(),
            "enabled": self.scheduler_enabled,
            "mode": self.scheduler_mode.value,
            "total_tasks": len(self.task_definitions),
            "queued_tasks": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "scheduled_tasks": len(self.scheduled_tasks),
            "recurring_tasks": len(self.recurring_tasks),
            "last_update": time.time()
        }
    
    def register_task_callback(self, task_type: TaskType, callback: Callable):
        """注册任务回调函数"""
        self.task_callbacks[task_type] = callback
    
    def export_tasks(self, file_path: str) -> bool:
        """导出任务定义"""
        try:
            tasks_data = {
                task_id: asdict(task_def) 
                for task_id, task_def in self.task_definitions.items()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
            
            self.scheduler_status_changed.emit(f"任务已导出到: {file_path}")
            return True
            
        except Exception as e:
            self.scheduler_status_changed.emit(f"导出任务失败: {str(e)}")
            return False
    
    def import_tasks(self, file_path: str) -> bool:
        """导入任务定义"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            imported_count = 0
            for task_id, task_data in tasks_data.items():
                # 转换为TaskDefinition
                task_data['task_type'] = TaskType(task_data['task_type'])
                task_data['priority'] = TaskPriority(task_data['priority'])
                task_def = TaskDefinition(**task_data)
                
                # 添加任务
                if self.add_task(task_def):
                    imported_count += 1
            
            self.scheduler_status_changed.emit(f"已导入 {imported_count} 个任务")
            return True
            
        except Exception as e:
            self.scheduler_status_changed.emit(f"导入任务失败: {str(e)}")
            return False
    
    def update_status(self):
        """更新状态（定时器回调）"""
        if self.is_connected():
            self.update_scheduler_states()