'''
Author: LK
Date: 2025-01-XX XX:XX:XX
LastEditTime: 2025-01-XX XX:XX:XX
LastEditors: LK
FilePath: /Demo/app/control/fileio_manager.py
'''

import threading
import time
import json
import os
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

try:
    from flexiv import FileIO
except ImportError:
    # 仿真模式下的模拟类
    class FileIO:
        def __init__(self, robot_ip: str):
            self.robot_ip = robot_ip
            self.connected = False
            self.remote_files = {
                "/flexiv/plans/": [
                    {"name": "home_plan.json", "size": 1024, "modified": time.time() - 3600},
                    {"name": "pick_place.json", "size": 2048, "modified": time.time() - 7200}
                ],
                "/flexiv/scripts/": [
                    {"name": "init_script.py", "size": 512, "modified": time.time() - 1800},
                    {"name": "calibration.py", "size": 1536, "modified": time.time() - 3600}
                ],
                "/flexiv/configs/": [
                    {"name": "robot_config.xml", "size": 4096, "modified": time.time() - 86400},
                    {"name": "safety_config.json", "size": 768, "modified": time.time() - 43200}
                ],
                "/flexiv/logs/": [
                    {"name": "system.log", "size": 10240, "modified": time.time() - 300},
                    {"name": "error.log", "size": 2560, "modified": time.time() - 600}
                ]
            }
            self.transfer_progress = {}
        
        def connect(self) -> bool:
            self.connected = True
            return True
        
        def disconnect(self):
            self.connected = False
        
        def is_connected(self) -> bool:
            return self.connected
        
        def list_files(self, remote_path: str) -> List[Dict[str, Any]]:
            return self.remote_files.get(remote_path, [])
        
        def list_directories(self, remote_path: str = "/") -> List[str]:
            if remote_path == "/":
                return ["/flexiv/plans/", "/flexiv/scripts/", "/flexiv/configs/", "/flexiv/logs/"]
            return []
        
        def file_exists(self, remote_path: str) -> bool:
            for dir_path, files in self.remote_files.items():
                if remote_path.startswith(dir_path):
                    filename = remote_path[len(dir_path):]
                    return any(f["name"] == filename for f in files)
            return False
        
        def get_file_info(self, remote_path: str) -> Optional[Dict[str, Any]]:
            for dir_path, files in self.remote_files.items():
                if remote_path.startswith(dir_path):
                    filename = remote_path[len(dir_path):]
                    for file_info in files:
                        if file_info["name"] == filename:
                            return {
                                "name": file_info["name"],
                                "path": remote_path,
                                "size": file_info["size"],
                                "modified": file_info["modified"],
                                "type": "file",
                                "permissions": "rw-r--r--"
                            }
            return None
        
        def create_directory(self, remote_path: str) -> bool:
            if remote_path not in self.remote_files:
                self.remote_files[remote_path] = []
                return True
            return False
        
        def delete_file(self, remote_path: str) -> bool:
            for dir_path, files in self.remote_files.items():
                if remote_path.startswith(dir_path):
                    filename = remote_path[len(dir_path):]
                    self.remote_files[dir_path] = [f for f in files if f["name"] != filename]
                    return True
            return False
        
        def delete_directory(self, remote_path: str) -> bool:
            if remote_path in self.remote_files:
                del self.remote_files[remote_path]
                return True
            return False
        
        def upload_file(self, local_path: str, remote_path: str, 
                       progress_callback: Optional[Callable] = None) -> bool:
            if not os.path.exists(local_path):
                return False
            
            # 模拟上传进度
            file_size = os.path.getsize(local_path)
            transfer_id = f"upload_{int(time.time())}"
            
            def simulate_upload():
                for progress in range(0, 101, 10):
                    if progress_callback:
                        progress_callback(transfer_id, progress, file_size * progress // 100, file_size)
                    time.sleep(0.1)
            
            # 在后台线程中模拟上传
            threading.Thread(target=simulate_upload, daemon=True).start()
            
            # 添加到远程文件列表
            dir_path = os.path.dirname(remote_path) + "/"
            filename = os.path.basename(remote_path)
            
            if dir_path not in self.remote_files:
                self.remote_files[dir_path] = []
            
            # 移除同名文件
            self.remote_files[dir_path] = [f for f in self.remote_files[dir_path] if f["name"] != filename]
            
            # 添加新文件
            self.remote_files[dir_path].append({
                "name": filename,
                "size": file_size,
                "modified": time.time()
            })
            
            return True
        
        def download_file(self, remote_path: str, local_path: str,
                         progress_callback: Optional[Callable] = None) -> bool:
            file_info = self.get_file_info(remote_path)
            if not file_info:
                return False
            
            # 模拟下载进度
            file_size = file_info["size"]
            transfer_id = f"download_{int(time.time())}"
            
            def simulate_download():
                for progress in range(0, 101, 10):
                    if progress_callback:
                        progress_callback(transfer_id, progress, file_size * progress // 100, file_size)
                    time.sleep(0.1)
                
                # 创建模拟文件
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'w') as f:
                    f.write(f"# 模拟文件内容\n# 远程路径: {remote_path}\n# 文件大小: {file_size} bytes\n")
            
            # 在后台线程中模拟下载
            threading.Thread(target=simulate_download, daemon=True).start()
            
            return True
        
        def copy_file(self, source_path: str, dest_path: str) -> bool:
            file_info = self.get_file_info(source_path)
            if not file_info:
                return False
            
            # 复制到目标位置
            dest_dir = os.path.dirname(dest_path) + "/"
            dest_filename = os.path.basename(dest_path)
            
            if dest_dir not in self.remote_files:
                self.remote_files[dest_dir] = []
            
            self.remote_files[dest_dir].append({
                "name": dest_filename,
                "size": file_info["size"],
                "modified": time.time()
            })
            
            return True
        
        def move_file(self, source_path: str, dest_path: str) -> bool:
            if self.copy_file(source_path, dest_path):
                return self.delete_file(source_path)
            return False
        
        def get_disk_usage(self, path: str = "/") -> Dict[str, int]:
            return {
                "total": 1024 * 1024 * 1024,  # 1GB
                "used": 512 * 1024 * 1024,    # 512MB
                "free": 512 * 1024 * 1024     # 512MB
            }
        
        def sync_time(self) -> bool:
            return True
        
        def get_system_logs(self, log_type: str = "system", lines: int = 100) -> List[str]:
            return [
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] INFO: 系统启动完成",
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] INFO: 机器人连接成功",
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] WARNING: 关节2温度略高",
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] INFO: 执行计划完成"
            ][-lines:]

class FileType(Enum):
    """文件类型"""
    PLAN = "plan"                 # 计划文件
    SCRIPT = "script"             # 脚本文件
    CONFIG = "config"             # 配置文件
    LOG = "log"                   # 日志文件
    DATA = "data"                 # 数据文件
    BACKUP = "backup"             # 备份文件
    FIRMWARE = "firmware"         # 固件文件
    URDF = "urdf"                 # URDF文件
    MESH = "mesh"                 # 网格文件
    OTHER = "other"               # 其他文件

class TransferDirection(Enum):
    """传输方向"""
    UPLOAD = "upload"             # 上传
    DOWNLOAD = "download"         # 下载
    SYNC = "sync"                 # 同步

class TransferStatus(Enum):
    """传输状态"""
    PENDING = "pending"           # 等待中
    RUNNING = "running"           # 进行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消
    PAUSED = "paused"             # 已暂停

@dataclass
class FileInfo:
    """文件信息"""
    name: str
    path: str
    size: int
    modified: float
    file_type: FileType
    permissions: str
    checksum: Optional[str] = None
    
    def __post_init__(self):
        if self.modified == 0.0:
            self.modified = time.time()

@dataclass
class TransferTask:
    """传输任务"""
    id: str
    direction: TransferDirection
    local_path: str
    remote_path: str
    file_size: int
    status: TransferStatus
    progress: float
    transferred_bytes: int
    start_time: float
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.start_time == 0.0:
            self.start_time = time.time()
    
    @property
    def duration(self) -> float:
        """传输持续时间"""
        end = self.end_time or time.time()
        return end - self.start_time
    
    @property
    def transfer_rate(self) -> float:
        """传输速率（字节/秒）"""
        duration = self.duration
        if duration > 0:
            return self.transferred_bytes / duration
        return 0.0
    
    @property
    def estimated_time_remaining(self) -> float:
        """预计剩余时间（秒）"""
        if self.progress > 0 and self.transfer_rate > 0:
            remaining_bytes = self.file_size - self.transferred_bytes
            return remaining_bytes / self.transfer_rate
        return 0.0

@dataclass
class SyncRule:
    """同步规则"""
    name: str
    local_path: str
    remote_path: str
    direction: TransferDirection
    file_patterns: List[str]  # 文件模式匹配
    exclude_patterns: List[str]  # 排除模式
    auto_sync: bool
    sync_interval: float  # 自动同步间隔（秒）
    last_sync: float
    enabled: bool = True
    
    def __post_init__(self):
        if self.file_patterns is None:
            self.file_patterns = ["*"]
        if self.exclude_patterns is None:
            self.exclude_patterns = []
        if self.last_sync == 0.0:
            self.last_sync = time.time()

class FileIOManager(QObject):
    """文件传输管理器
    
    负责机器人文件传输和管理，包括：
    - 文件上传和下载
    - 远程文件浏览
    - 文件同步
    - 传输进度监控
    - 文件管理操作
    - 日志文件访问
    """
    
    # 信号定义
    fileio_status_changed = pyqtSignal(str)  # status_message
    file_list_updated = pyqtSignal(str, list)  # remote_path, file_list
    transfer_started = pyqtSignal(object)  # TransferTask
    transfer_progress = pyqtSignal(str, float, int, int)  # task_id, progress, transferred, total
    transfer_completed = pyqtSignal(str, bool, str)  # task_id, success, message
    file_operation_completed = pyqtSignal(str, bool, str)  # operation, success, message
    sync_started = pyqtSignal(str)  # rule_name
    sync_completed = pyqtSignal(str, bool, str)  # rule_name, success, message
    disk_usage_updated = pyqtSignal(dict)  # usage_info
    
    def __init__(self, robot=None, hardware=True, robot_ip: str = "192.168.2.100", parent=None):
        super().__init__(parent)
        
        self.robot = robot
        self.hardware = hardware
        self.robot_ip = robot_ip
        self.fileio = None
        self.connected = False
        
        # 传输管理
        self.transfer_tasks = {}  # task_id -> TransferTask
        self.active_transfers = set()  # 活跃传输的task_id
        self.max_concurrent_transfers = 3
        
        # 同步规则
        self.sync_rules = {}  # rule_name -> SyncRule
        
        # 文件缓存
        self.file_cache = {}  # remote_path -> List[FileInfo]
        self.cache_timeout = 300.0  # 缓存超时时间（秒）
        self.cache_timestamps = {}  # remote_path -> timestamp
        
        # 监控线程
        self.monitor_thread = None
        self.monitor_lock = threading.Lock()
        self.stop_monitoring = threading.Event()
        
        # 初始化线程管理器和资源管理器
        self.thread_manager = get_thread_manager()
        self.resource_manager = get_resource_manager()
        
        # 注册文件传输资源
        self.resource_manager.register_resource(
            resource_id=f"fileio_{self.robot_ip}",
            resource_type=ResourceType.FILE,
            metadata={
                "robot_ip": self.robot_ip,
                "type": "fileio"
            }
        )
        
        # 定时器
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.check_auto_sync)
        
        self.disk_timer = QTimer()
        self.disk_timer.timeout.connect(self.update_disk_usage)
        
        # 预定义同步规则
        self.init_default_sync_rules()
        
        # 初始化
        self.init_fileio()
    
    def init_fileio(self):
        """初始化文件传输管理器"""
        try:
            self.fileio = FileIO(self.robot_ip)
            self.fileio_status_changed.emit("文件传输管理器已初始化")
        except Exception as e:
            self.fileio_status_changed.emit(f"文件传输管理器初始化失败: {str(e)}")
    
    def init_default_sync_rules(self):
        """初始化默认同步规则"""
        # 计划文件同步
        plans_rule = SyncRule(
            name="plans_sync",
            local_path="./plans/",
            remote_path="/flexiv/plans/",
            direction=TransferDirection.SYNC,
            file_patterns=["*.json", "*.xml"],
            exclude_patterns=["*.tmp", "*.bak"],
            auto_sync=True,
            sync_interval=3600.0,  # 1小时
            last_sync=0.0
        )
        self.sync_rules["plans_sync"] = plans_rule
        
        # 配置文件同步
        configs_rule = SyncRule(
            name="configs_sync",
            local_path="./configs/",
            remote_path="/flexiv/configs/",
            direction=TransferDirection.DOWNLOAD,
            file_patterns=["*.xml", "*.json", "*.yaml"],
            exclude_patterns=[],
            auto_sync=True,
            sync_interval=7200.0,  # 2小时
            last_sync=0.0
        )
        self.sync_rules["configs_sync"] = configs_rule
        
        # 日志文件同步
        logs_rule = SyncRule(
            name="logs_sync",
            local_path="./logs/",
            remote_path="/flexiv/logs/",
            direction=TransferDirection.DOWNLOAD,
            file_patterns=["*.log", "*.txt"],
            exclude_patterns=["*.tmp"],
            auto_sync=True,
            sync_interval=1800.0,  # 30分钟
            last_sync=0.0
        )
        self.sync_rules["logs_sync"] = logs_rule
    
    def connect_fileio(self) -> bool:
        """连接文件传输管理器"""
        try:
            if not self.fileio:
                self.init_fileio()
            
            if self.fileio and self.fileio.connect():
                self.connected = True
                self.fileio_status_changed.emit("文件传输管理器已连接")
                
                # 更新磁盘使用情况
                self.update_disk_usage()
                
                return True
            else:
                self.fileio_status_changed.emit("文件传输管理器连接失败")
                return False
                
        except Exception as e:
            self.fileio_status_changed.emit(f"文件传输管理器连接错误: {str(e)}")
            return False
    
    def disconnect_fileio(self):
        """断开文件传输管理器连接"""
        try:
            self.stop_monitoring_fileio()
            
            # 取消所有活跃传输
            for task_id in list(self.active_transfers):
                self.cancel_transfer(task_id)
            
            if self.fileio and self.connected:
                self.fileio.disconnect()
                self.connected = False
                self.fileio_status_changed.emit("文件传输管理器已断开")
                
        except Exception as e:
            self.fileio_status_changed.emit(f"文件传输管理器断开错误: {str(e)}")
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.connected and self.fileio and self.fileio.is_connected()
    
    def start_monitoring_fileio(self, sync_interval: float = 3600.0, disk_interval: float = 60.0):
        """开始监控文件传输"""
        if not self.is_connected():
            self.fileio_status_changed.emit("文件传输管理器未连接，无法开始监控")
            return
        
        self.stop_monitoring.clear()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(
            target=self._fileio_monitor_loop,
            args=(1.0,),  # 传输监控间隔
            daemon=True
        )
        self.monitor_thread.start()
        
        # 启动定时器
        self.sync_timer.start(int(sync_interval * 1000))
        self.disk_timer.start(int(disk_interval * 1000))
        
        self.fileio_status_changed.emit("文件传输监控已启动")
    
    def stop_monitoring_fileio(self):
        """停止监控文件传输"""
        self.stop_monitoring.set()
        
        # 停止定时器
        self.sync_timer.stop()
        self.disk_timer.stop()
        
        # 等待监控线程结束
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        
        self.fileio_status_changed.emit("文件传输监控已停止")
    
    def _fileio_monitor_loop(self, interval: float):
        """文件传输监控循环"""
        while not self.stop_monitoring.is_set():
            try:
                with self.monitor_lock:
                    if self.is_connected():
                        # 监控传输进度
                        self.update_transfer_progress()
                        
                        # 清理过期缓存
                        self.cleanup_file_cache()
                
                time.sleep(interval)
                
            except Exception as e:
                self.fileio_status_changed.emit(f"文件传输监控错误: {str(e)}")
                time.sleep(interval)
    
    def list_remote_files(self, remote_path: str, use_cache: bool = True) -> List[FileInfo]:
        """列出远程文件"""
        try:
            if not self.is_connected():
                self.fileio_status_changed.emit("文件传输管理器未连接")
                return []
            
            # 检查缓存
            if use_cache and remote_path in self.file_cache:
                cache_time = self.cache_timestamps.get(remote_path, 0)
                if time.time() - cache_time < self.cache_timeout:
                    return self.file_cache[remote_path]
            
            # 获取文件列表
            files_data = self.fileio.list_files(remote_path)
            
            # 转换为FileInfo对象
            file_infos = []
            for file_data in files_data:
                file_type = self.detect_file_type(file_data["name"])
                file_info = FileInfo(
                    name=file_data["name"],
                    path=os.path.join(remote_path, file_data["name"]).replace("\\", "/"),
                    size=file_data["size"],
                    modified=file_data["modified"],
                    file_type=file_type,
                    permissions=file_data.get("permissions", "rw-r--r--")
                )
                file_infos.append(file_info)
            
            # 更新缓存
            self.file_cache[remote_path] = file_infos
            self.cache_timestamps[remote_path] = time.time()
            
            self.file_list_updated.emit(remote_path, file_infos)
            return file_infos
            
        except Exception as e:
            self.fileio_status_changed.emit(f"列出远程文件错误: {str(e)}")
            return []
    
    def list_remote_directories(self, remote_path: str = "/") -> List[str]:
        """列出远程目录"""
        try:
            if not self.is_connected():
                return []
            
            return self.fileio.list_directories(remote_path)
            
        except Exception as e:
            self.fileio_status_changed.emit(f"列出远程目录错误: {str(e)}")
            return []
    
    def detect_file_type(self, filename: str) -> FileType:
        """检测文件类型"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext in [".json", ".xml"] and "plan" in filename.lower():
            return FileType.PLAN
        elif ext in [".py", ".lua", ".js"]:
            return FileType.SCRIPT
        elif ext in [".xml", ".json", ".yaml", ".yml", ".cfg", ".conf"]:
            return FileType.CONFIG
        elif ext in [".log", ".txt"]:
            return FileType.LOG
        elif ext in [".urdf", ".xacro"]:
            return FileType.URDF
        elif ext in [".stl", ".obj", ".dae", ".mesh"]:
            return FileType.MESH
        elif ext in [".bin", ".hex", ".fw"]:
            return FileType.FIRMWARE
        elif ext in [".bak", ".backup", ".tar", ".zip"]:
            return FileType.BACKUP
        elif ext in [".csv", ".dat", ".db"]:
            return FileType.DATA
        else:
            return FileType.OTHER
    
    def upload_file(self, local_path: str, remote_path: str) -> Optional[str]:
        """上传文件"""
        try:
            if not self.is_connected():
                self.fileio_status_changed.emit("文件传输管理器未连接")
                return None
            
            if not os.path.exists(local_path):
                self.fileio_status_changed.emit(f"本地文件不存在: {local_path}")
                return None
            
            # 检查并发传输限制
            if len(self.active_transfers) >= self.max_concurrent_transfers:
                self.fileio_status_changed.emit("传输任务已达到最大并发数")
                return None
            
            # 创建传输任务
            task_id = f"upload_{int(time.time())}_{len(self.transfer_tasks)}"
            file_size = os.path.getsize(local_path)
            
            task = TransferTask(
                id=task_id,
                direction=TransferDirection.UPLOAD,
                local_path=local_path,
                remote_path=remote_path,
                file_size=file_size,
                status=TransferStatus.PENDING,
                progress=0.0,
                transferred_bytes=0,
                start_time=time.time()
            )
            
            self.transfer_tasks[task_id] = task
            self.active_transfers.add(task_id)
            
            # 启动传输
            def progress_callback(transfer_id, progress, transferred, total):
                self.update_transfer_task(transfer_id, progress, transferred)
            
            success = self.fileio.upload_file(local_path, remote_path, progress_callback)
            
            if success:
                task.status = TransferStatus.RUNNING
                self.transfer_started.emit(task)
                self.fileio_status_changed.emit(f"开始上传文件: {os.path.basename(local_path)}")
                
                # 清除相关缓存
                remote_dir = os.path.dirname(remote_path)
                self.file_cache.pop(remote_dir, None)
                
                return task_id
            else:
                task.status = TransferStatus.FAILED
                task.error_message = "上传启动失败"
                self.active_transfers.discard(task_id)
                self.fileio_status_changed.emit(f"上传文件失败: {os.path.basename(local_path)}")
                return None
                
        except Exception as e:
            self.fileio_status_changed.emit(f"上传文件错误: {str(e)}")
            return None
    
    def download_file(self, remote_path: str, local_path: str) -> Optional[str]:
        """下载文件"""
        try:
            if not self.is_connected():
                self.fileio_status_changed.emit("文件传输管理器未连接")
                return None
            
            if not self.fileio.file_exists(remote_path):
                self.fileio_status_changed.emit(f"远程文件不存在: {remote_path}")
                return None
            
            # 检查并发传输限制
            if len(self.active_transfers) >= self.max_concurrent_transfers:
                self.fileio_status_changed.emit("传输任务已达到最大并发数")
                return None
            
            # 获取文件信息
            file_info = self.fileio.get_file_info(remote_path)
            if not file_info:
                self.fileio_status_changed.emit(f"无法获取文件信息: {remote_path}")
                return None
            
            # 创建传输任务
            task_id = f"download_{int(time.time())}_{len(self.transfer_tasks)}"
            file_size = file_info["size"]
            
            task = TransferTask(
                id=task_id,
                direction=TransferDirection.DOWNLOAD,
                local_path=local_path,
                remote_path=remote_path,
                file_size=file_size,
                status=TransferStatus.PENDING,
                progress=0.0,
                transferred_bytes=0,
                start_time=time.time()
            )
            
            self.transfer_tasks[task_id] = task
            self.active_transfers.add(task_id)
            
            # 启动传输
            def progress_callback(transfer_id, progress, transferred, total):
                self.update_transfer_task(transfer_id, progress, transferred)
            
            success = self.fileio.download_file(remote_path, local_path, progress_callback)
            
            if success:
                task.status = TransferStatus.RUNNING
                self.transfer_started.emit(task)
                self.fileio_status_changed.emit(f"开始下载文件: {os.path.basename(remote_path)}")
                return task_id
            else:
                task.status = TransferStatus.FAILED
                task.error_message = "下载启动失败"
                self.active_transfers.discard(task_id)
                self.fileio_status_changed.emit(f"下载文件失败: {os.path.basename(remote_path)}")
                return None
                
        except Exception as e:
            self.fileio_status_changed.emit(f"下载文件错误: {str(e)}")
            return None
    
    def update_transfer_task(self, task_id: str, progress: float, transferred_bytes: int):
        """更新传输任务进度"""
        if task_id in self.transfer_tasks:
            task = self.transfer_tasks[task_id]
            task.progress = progress
            task.transferred_bytes = transferred_bytes
            
            self.transfer_progress.emit(task_id, progress, transferred_bytes, task.file_size)
            
            # 检查是否完成
            if progress >= 100.0:
                task.status = TransferStatus.COMPLETED
                task.end_time = time.time()
                self.active_transfers.discard(task_id)
                
                direction = "上传" if task.direction == TransferDirection.UPLOAD else "下载"
                filename = os.path.basename(task.local_path)
                self.transfer_completed.emit(task_id, True, f"{direction}完成: {filename}")
    
    def update_transfer_progress(self):
        """更新传输进度（监控线程调用）"""
        # 这里可以添加实际的传输进度查询逻辑
        # 目前由progress_callback处理
        pass
    
    def cancel_transfer(self, task_id: str) -> bool:
        """取消传输任务"""
        try:
            if task_id not in self.transfer_tasks:
                return False
            
            task = self.transfer_tasks[task_id]
            if task.status in [TransferStatus.COMPLETED, TransferStatus.FAILED, TransferStatus.CANCELLED]:
                return False
            
            task.status = TransferStatus.CANCELLED
            task.end_time = time.time()
            self.active_transfers.discard(task_id)
            
            direction = "上传" if task.direction == TransferDirection.UPLOAD else "下载"
            filename = os.path.basename(task.local_path)
            self.transfer_completed.emit(task_id, False, f"{direction}已取消: {filename}")
            
            return True
            
        except Exception as e:
            self.fileio_status_changed.emit(f"取消传输错误: {str(e)}")
            return False
    
    def pause_transfer(self, task_id: str) -> bool:
        """暂停传输任务"""
        try:
            if task_id not in self.transfer_tasks:
                return False
            
            task = self.transfer_tasks[task_id]
            if task.status != TransferStatus.RUNNING:
                return False
            
            task.status = TransferStatus.PAUSED
            self.fileio_status_changed.emit(f"传输已暂停: {os.path.basename(task.local_path)}")
            return True
            
        except Exception as e:
            self.fileio_status_changed.emit(f"暂停传输错误: {str(e)}")
            return False
    
    def resume_transfer(self, task_id: str) -> bool:
        """恢复传输任务"""
        try:
            if task_id not in self.transfer_tasks:
                return False
            
            task = self.transfer_tasks[task_id]
            if task.status != TransferStatus.PAUSED:
                return False
            
            task.status = TransferStatus.RUNNING
            self.fileio_status_changed.emit(f"传输已恢复: {os.path.basename(task.local_path)}")
            return True
            
        except Exception as e:
            self.fileio_status_changed.emit(f"恢复传输错误: {str(e)}")
            return False
    
    def delete_remote_file(self, remote_path: str) -> bool:
        """删除远程文件"""
        try:
            if not self.is_connected():
                self.fileio_status_changed.emit("文件传输管理器未连接")
                return False
            
            success = self.fileio.delete_file(remote_path)
            if success:
                # 清除相关缓存
                remote_dir = os.path.dirname(remote_path)
                self.file_cache.pop(remote_dir, None)
                
                filename = os.path.basename(remote_path)
                self.file_operation_completed.emit("delete", True, f"文件已删除: {filename}")
                return True
            else:
                self.file_operation_completed.emit("delete", False, f"删除文件失败: {remote_path}")
                return False
                
        except Exception as e:
            self.file_operation_completed.emit("delete", False, f"删除文件错误: {str(e)}")
            return False
    
    def create_remote_directory(self, remote_path: str) -> bool:
        """创建远程目录"""
        try:
            if not self.is_connected():
                self.fileio_status_changed.emit("文件传输管理器未连接")
                return False
            
            success = self.fileio.create_directory(remote_path)
            if success:
                self.file_operation_completed.emit("create_dir", True, f"目录已创建: {remote_path}")
                return True
            else:
                self.file_operation_completed.emit("create_dir", False, f"创建目录失败: {remote_path}")
                return False
                
        except Exception as e:
            self.file_operation_completed.emit("create_dir", False, f"创建目录错误: {str(e)}")
            return False
    
    def copy_remote_file(self, source_path: str, dest_path: str) -> bool:
        """复制远程文件"""
        try:
            if not self.is_connected():
                self.fileio_status_changed.emit("文件传输管理器未连接")
                return False
            
            success = self.fileio.copy_file(source_path, dest_path)
            if success:
                # 清除相关缓存
                dest_dir = os.path.dirname(dest_path)
                self.file_cache.pop(dest_dir, None)
                
                filename = os.path.basename(source_path)
                self.file_operation_completed.emit("copy", True, f"文件已复制: {filename}")
                return True
            else:
                self.file_operation_completed.emit("copy", False, f"复制文件失败: {source_path}")
                return False
                
        except Exception as e:
            self.file_operation_completed.emit("copy", False, f"复制文件错误: {str(e)}")
            return False
    
    def move_remote_file(self, source_path: str, dest_path: str) -> bool:
        """移动远程文件"""
        try:
            if not self.is_connected():
                self.fileio_status_changed.emit("文件传输管理器未连接")
                return False
            
            success = self.fileio.move_file(source_path, dest_path)
            if success:
                # 清除相关缓存
                source_dir = os.path.dirname(source_path)
                dest_dir = os.path.dirname(dest_path)
                self.file_cache.pop(source_dir, None)
                self.file_cache.pop(dest_dir, None)
                
                filename = os.path.basename(source_path)
                self.file_operation_completed.emit("move", True, f"文件已移动: {filename}")
                return True
            else:
                self.file_operation_completed.emit("move", False, f"移动文件失败: {source_path}")
                return False
                
        except Exception as e:
            self.file_operation_completed.emit("move", False, f"移动文件错误: {str(e)}")
            return False
    
    def add_sync_rule(self, rule: SyncRule):
        """添加同步规则"""
        self.sync_rules[rule.name] = rule
        self.fileio_status_changed.emit(f"同步规则已添加: {rule.name}")
    
    def remove_sync_rule(self, rule_name: str) -> bool:
        """移除同步规则"""
        if rule_name in self.sync_rules:
            del self.sync_rules[rule_name]
            self.fileio_status_changed.emit(f"同步规则已移除: {rule_name}")
            return True
        return False
    
    def execute_sync_rule(self, rule_name: str) -> bool:
        """执行同步规则"""
        try:
            if rule_name not in self.sync_rules:
                self.fileio_status_changed.emit(f"同步规则不存在: {rule_name}")
                return False
            
            rule = self.sync_rules[rule_name]
            if not rule.enabled:
                self.fileio_status_changed.emit(f"同步规则已禁用: {rule_name}")
                return False
            
            self.sync_started.emit(rule_name)
            
            # 执行同步逻辑
            success = self.perform_sync(rule)
            
            if success:
                rule.last_sync = time.time()
                self.sync_completed.emit(rule_name, True, "同步完成")
            else:
                self.sync_completed.emit(rule_name, False, "同步失败")
            
            return success
            
        except Exception as e:
            self.sync_completed.emit(rule_name, False, f"同步错误: {str(e)}")
            return False
    
    def perform_sync(self, rule: SyncRule) -> bool:
        """执行同步操作"""
        try:
            if rule.direction == TransferDirection.UPLOAD:
                return self.sync_upload(rule)
            elif rule.direction == TransferDirection.DOWNLOAD:
                return self.sync_download(rule)
            elif rule.direction == TransferDirection.SYNC:
                return self.sync_bidirectional(rule)
            else:
                return False
                
        except Exception as e:
            self.fileio_status_changed.emit(f"执行同步错误: {str(e)}")
            return False
    
    def sync_upload(self, rule: SyncRule) -> bool:
        """上传同步"""
        # 简化的上传同步实现
        if not os.path.exists(rule.local_path):
            return False
        
        for root, dirs, files in os.walk(rule.local_path):
            for file in files:
                if self.match_patterns(file, rule.file_patterns, rule.exclude_patterns):
                    local_file = os.path.join(root, file)
                    rel_path = os.path.relpath(local_file, rule.local_path)
                    remote_file = os.path.join(rule.remote_path, rel_path).replace("\\", "/")
                    
                    # 检查是否需要上传（简化检查）
                    if not self.fileio.file_exists(remote_file):
                        self.upload_file(local_file, remote_file)
        
        return True
    
    def sync_download(self, rule: SyncRule) -> bool:
        """下载同步"""
        # 简化的下载同步实现
        remote_files = self.list_remote_files(rule.remote_path, use_cache=False)
        
        for file_info in remote_files:
            if self.match_patterns(file_info.name, rule.file_patterns, rule.exclude_patterns):
                local_file = os.path.join(rule.local_path, file_info.name)
                
                # 检查是否需要下载（简化检查）
                if not os.path.exists(local_file):
                    os.makedirs(os.path.dirname(local_file), exist_ok=True)
                    self.download_file(file_info.path, local_file)
        
        return True
    
    def sync_bidirectional(self, rule: SyncRule) -> bool:
        """双向同步"""
        # 简化的双向同步实现
        upload_success = self.sync_upload(rule)
        download_success = self.sync_download(rule)
        return upload_success and download_success
    
    def match_patterns(self, filename: str, include_patterns: List[str], exclude_patterns: List[str]) -> bool:
        """匹配文件模式"""
        import fnmatch
        
        # 检查排除模式
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False
        
        # 检查包含模式
        for pattern in include_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        
        return False
    
    def check_auto_sync(self):
        """检查自动同步（定时器回调）"""
        current_time = time.time()
        
        for rule_name, rule in self.sync_rules.items():
            if rule.enabled and rule.auto_sync:
                if current_time - rule.last_sync >= rule.sync_interval:
                    self.execute_sync_rule(rule_name)
    
    def update_disk_usage(self):
        """更新磁盘使用情况"""
        try:
            if not self.is_connected():
                return
            
            usage_info = self.fileio.get_disk_usage()
            self.disk_usage_updated.emit(usage_info)
            
        except Exception as e:
            self.fileio_status_changed.emit(f"更新磁盘使用情况错误: {str(e)}")
    
    def cleanup_file_cache(self):
        """清理过期的文件缓存"""
        current_time = time.time()
        expired_paths = [
            path for path, timestamp in self.cache_timestamps.items()
            if current_time - timestamp > self.cache_timeout
        ]
        
        for path in expired_paths:
            self.file_cache.pop(path, None)
            self.cache_timestamps.pop(path, None)
    
    def get_system_logs(self, log_type: str = "system", lines: int = 100) -> List[str]:
        """获取系统日志"""
        try:
            if not self.is_connected():
                return []
            
            return self.fileio.get_system_logs(log_type, lines)
            
        except Exception as e:
            self.fileio_status_changed.emit(f"获取系统日志错误: {str(e)}")
            return []
    
    def calculate_file_checksum(self, file_path: str) -> Optional[str]:
        """计算文件校验和"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    def get_transfer_tasks(self, status: Optional[TransferStatus] = None) -> List[TransferTask]:
        """获取传输任务列表"""
        tasks = list(self.transfer_tasks.values())
        
        if status:
            tasks = [task for task in tasks if task.status == status]
        
        return tasks
    
    def get_sync_rules(self) -> List[SyncRule]:
        """获取同步规则列表"""
        return list(self.sync_rules.values())
    
    def get_fileio_summary(self) -> Dict[str, Any]:
        """获取文件传输摘要"""
        return {
            "connected": self.is_connected(),
            "active_transfers": len(self.active_transfers),
            "total_transfers": len(self.transfer_tasks),
            "sync_rules": len(self.sync_rules),
            "cache_entries": len(self.file_cache),
            "max_concurrent_transfers": self.max_concurrent_transfers,
            "last_update": time.time()
        }