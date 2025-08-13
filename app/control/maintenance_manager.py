'''
Author: LK
Date: 2025-01-XX XX:XX:XX
LastEditTime: 2025-01-XX XX:XX:XX
LastEditors: LK
FilePath: /Demo/app/control/maintenance_manager.py
'''

import threading
import time
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

try:
    from flexiv import Maintenance
except ImportError:
    # 仿真模式下的模拟类
    class Maintenance:
        def __init__(self, robot_ip: str):
            self.robot_ip = robot_ip
            self.connected = False
            self.maintenance_data = {
                "joint_temperatures": [25.0] * 7,
                "motor_currents": [0.5] * 7,
                "joint_positions": [0.0] * 7,
                "joint_velocities": [0.0] * 7,
                "joint_torques": [0.0] * 7,
                "system_temperature": 35.0,
                "power_consumption": 150.0,
                "uptime": 3600.0,
                "error_count": 0,
                "warning_count": 2,
                "last_maintenance": time.time() - 86400 * 30,
                "next_maintenance": time.time() + 86400 * 60
            }
            self.diagnostics_running = False
            self.calibration_running = False
        
        def connect(self) -> bool:
            self.connected = True
            return True
        
        def disconnect(self):
            self.connected = False
        
        def is_connected(self) -> bool:
            return self.connected
        
        def get_system_info(self) -> Dict[str, Any]:
            return {
                "robot_model": "Rizon 4s",
                "serial_number": "RZ4S-2024-001",
                "firmware_version": "2.8.1",
                "hardware_version": "1.2",
                "manufacture_date": "2024-01-15",
                "last_update": "2024-12-01"
            }
        
        def get_joint_info(self, joint_id: int) -> Dict[str, Any]:
            return {
                "joint_id": joint_id,
                "temperature": self.maintenance_data["joint_temperatures"][joint_id],
                "current": self.maintenance_data["motor_currents"][joint_id],
                "position": self.maintenance_data["joint_positions"][joint_id],
                "velocity": self.maintenance_data["joint_velocities"][joint_id],
                "torque": self.maintenance_data["joint_torques"][joint_id],
                "status": "normal",
                "error_count": 0,
                "warning_count": 0,
                "last_calibration": time.time() - 86400 * 7,
                "next_calibration": time.time() + 86400 * 90
            }
        
        def get_system_status(self) -> Dict[str, Any]:
            return {
                "overall_status": "normal",
                "temperature": self.maintenance_data["system_temperature"],
                "power_consumption": self.maintenance_data["power_consumption"],
                "uptime": self.maintenance_data["uptime"],
                "error_count": self.maintenance_data["error_count"],
                "warning_count": self.maintenance_data["warning_count"],
                "cpu_usage": 25.5,
                "memory_usage": 45.2,
                "disk_usage": 68.1,
                "network_status": "connected"
            }
        
        def get_maintenance_schedule(self) -> Dict[str, Any]:
            return {
                "last_maintenance": self.maintenance_data["last_maintenance"],
                "next_maintenance": self.maintenance_data["next_maintenance"],
                "maintenance_interval": 86400 * 90,  # 90天
                "overdue": False,
                "days_until_next": 60,
                "maintenance_type": "routine"
            }
        
        def start_diagnostics(self, test_type: str = "full") -> bool:
            self.diagnostics_running = True
            return True
        
        def stop_diagnostics(self) -> bool:
            self.diagnostics_running = False
            return True
        
        def get_diagnostics_status(self) -> Dict[str, Any]:
            return {
                "running": self.diagnostics_running,
                "progress": 75.0 if self.diagnostics_running else 100.0,
                "current_test": "joint_calibration" if self.diagnostics_running else "completed",
                "estimated_time_remaining": 300 if self.diagnostics_running else 0,
                "tests_completed": 8,
                "tests_total": 12,
                "errors_found": 0,
                "warnings_found": 1
            }
        
        def get_diagnostics_results(self) -> Dict[str, Any]:
            return {
                "test_date": time.time(),
                "test_duration": 1800,
                "overall_result": "pass",
                "tests": [
                    {"name": "joint_movement", "result": "pass", "details": "所有关节运动正常"},
                    {"name": "sensor_calibration", "result": "pass", "details": "传感器校准正常"},
                    {"name": "communication", "result": "pass", "details": "通信正常"},
                    {"name": "temperature", "result": "warning", "details": "关节2温度略高"}
                ],
                "recommendations": [
                    "建议检查关节2的散热情况",
                    "下次维护时更换润滑油"
                ]
            }
        
        def calibrate_joint(self, joint_id: int) -> bool:
            self.calibration_running = True
            return True
        
        def calibrate_all_joints(self) -> bool:
            self.calibration_running = True
            return True
        
        def get_calibration_status(self) -> Dict[str, Any]:
            return {
                "running": self.calibration_running,
                "current_joint": 2 if self.calibration_running else -1,
                "progress": 30.0 if self.calibration_running else 100.0,
                "estimated_time_remaining": 600 if self.calibration_running else 0
            }
        
        def reset_error_count(self) -> bool:
            self.maintenance_data["error_count"] = 0
            return True
        
        def reset_warning_count(self) -> bool:
            self.maintenance_data["warning_count"] = 0
            return True
        
        def export_maintenance_log(self, file_path: str) -> bool:
            return True
        
        def import_maintenance_config(self, file_path: str) -> bool:
            return True
        
        def update_firmware(self, firmware_path: str) -> bool:
            return True
        
        def backup_system(self, backup_path: str) -> bool:
            return True
        
        def restore_system(self, backup_path: str) -> bool:
            return True

class MaintenanceType(Enum):
    """维护类型"""
    ROUTINE = "routine"           # 例行维护
    PREVENTIVE = "preventive"     # 预防性维护
    CORRECTIVE = "corrective"     # 纠正性维护
    EMERGENCY = "emergency"       # 紧急维护
    CALIBRATION = "calibration"   # 校准维护
    UPGRADE = "upgrade"           # 升级维护

class DiagnosticsType(Enum):
    """诊断类型"""
    QUICK = "quick"               # 快速诊断
    FULL = "full"                 # 全面诊断
    JOINT = "joint"               # 关节诊断
    SENSOR = "sensor"             # 传感器诊断
    COMMUNICATION = "communication" # 通信诊断
    PERFORMANCE = "performance"   # 性能诊断

class MaintenanceStatus(Enum):
    """维护状态"""
    NORMAL = "normal"             # 正常
    WARNING = "warning"           # 警告
    ERROR = "error"               # 错误
    CRITICAL = "critical"         # 严重
    MAINTENANCE_DUE = "maintenance_due"  # 需要维护
    CALIBRATION_DUE = "calibration_due" # 需要校准

@dataclass
class MaintenanceRecord:
    """维护记录"""
    id: str
    timestamp: float
    maintenance_type: MaintenanceType
    description: str
    technician: str
    duration: float  # 维护时长（秒）
    parts_replaced: List[str]
    issues_found: List[str]
    issues_resolved: List[str]
    next_maintenance_date: float
    notes: str
    status: MaintenanceStatus
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

@dataclass
class DiagnosticsResult:
    """诊断结果"""
    id: str
    timestamp: float
    test_type: DiagnosticsType
    duration: float
    overall_result: str  # pass, warning, fail
    tests_completed: int
    tests_total: int
    errors_found: int
    warnings_found: int
    test_details: List[Dict[str, Any]]
    recommendations: List[str]
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if self.test_details is None:
            self.test_details = []
        if self.recommendations is None:
            self.recommendations = []

@dataclass
class SystemHealth:
    """系统健康状态"""
    overall_status: MaintenanceStatus
    temperature: float
    power_consumption: float
    uptime: float
    error_count: int
    warning_count: int
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_status: str
    last_update: float
    
    def __post_init__(self):
        if self.last_update == 0.0:
            self.last_update = time.time()

class MaintenanceManager(QObject):
    """维护管理器
    
    负责机器人维护和诊断，包括：
    - 系统状态监控
    - 维护计划管理
    - 诊断测试执行
    - 校准管理
    - 维护记录管理
    - 系统备份和恢复
    - 固件更新
    """
    
    # 信号定义
    maintenance_status_changed = pyqtSignal(str)  # status_message
    system_health_updated = pyqtSignal(object)  # SystemHealth
    maintenance_due = pyqtSignal(str, object)  # maintenance_type, details
    diagnostics_started = pyqtSignal(str)  # test_type
    diagnostics_progress = pyqtSignal(float, str)  # progress, current_test
    diagnostics_completed = pyqtSignal(object)  # DiagnosticsResult
    calibration_started = pyqtSignal(int)  # joint_id (-1 for all)
    calibration_progress = pyqtSignal(int, float)  # joint_id, progress
    calibration_completed = pyqtSignal(int, bool, str)  # joint_id, success, message
    maintenance_record_added = pyqtSignal(object)  # MaintenanceRecord
    firmware_update_progress = pyqtSignal(float, str)  # progress, status
    backup_progress = pyqtSignal(float, str)  # progress, status
    
    def __init__(self, robot=None, hardware=True, robot_ip: str = "192.168.2.100", parent=None):
        super().__init__(parent)
        
        self.robot = robot
        self.hardware = hardware
        self.robot_ip = robot_ip
        self.maintenance = None
        self.connected = False
        
        # 维护数据
        self.maintenance_records = []  # List[MaintenanceRecord]
        self.diagnostics_results = []  # List[DiagnosticsResult]
        self.system_health = None  # SystemHealth
        
        # 维护计划
        self.maintenance_schedule = {}
        self.maintenance_intervals = {
            MaintenanceType.ROUTINE: 86400 * 90,      # 90天
            MaintenanceType.PREVENTIVE: 86400 * 180,  # 180天
            MaintenanceType.CALIBRATION: 86400 * 30   # 30天
        }
        
        # 诊断状态
        self.diagnostics_running = False
        self.current_diagnostics_type = None
        self.diagnostics_progress = 0.0
        
        # 校准状态
        self.calibration_running = False
        self.current_calibration_joint = -1
        self.calibration_progress = 0.0
        
        # 监控线程
        self.monitor_thread = None
        self.monitor_lock = threading.Lock()
        self.stop_monitoring = threading.Event()
        
        # 定时器
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self.update_system_health)
        
        self.schedule_timer = QTimer()
        self.schedule_timer.timeout.connect(self.check_maintenance_schedule)
        
        # 初始化
        self.init_maintenance()
    
    def init_maintenance(self):
        """初始化维护管理器"""
        try:
            self.maintenance = Maintenance(self.robot_ip)
            self.maintenance_status_changed.emit("维护管理器已初始化")
        except Exception as e:
            self.maintenance_status_changed.emit(f"维护管理器初始化失败: {str(e)}")
    
    def connect_maintenance(self) -> bool:
        """连接维护管理器"""
        try:
            if not self.maintenance:
                self.init_maintenance()
            
            if self.maintenance and self.maintenance.connect():
                self.connected = True
                self.maintenance_status_changed.emit("维护管理器已连接")
                
                # 初始化系统健康状态
                self.update_system_health()
                
                # 检查维护计划
                self.check_maintenance_schedule()
                
                return True
            else:
                self.maintenance_status_changed.emit("维护管理器连接失败")
                return False
                
        except Exception as e:
            self.maintenance_status_changed.emit(f"维护管理器连接错误: {str(e)}")
            return False
    
    def disconnect_maintenance(self):
        """断开维护管理器连接"""
        try:
            self.stop_monitoring_maintenance()
            
            if self.maintenance and self.connected:
                self.maintenance.disconnect()
                self.connected = False
                self.maintenance_status_changed.emit("维护管理器已断开")
                
        except Exception as e:
            self.maintenance_status_changed.emit(f"维护管理器断开错误: {str(e)}")
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.connected and self.maintenance and self.maintenance.is_connected()
    
    def start_monitoring_maintenance(self, health_interval: float = 5.0, schedule_interval: float = 3600.0):
        """开始监控维护状态"""
        if not self.is_connected():
            self.maintenance_status_changed.emit("维护管理器未连接，无法开始监控")
            return
        
        self.stop_monitoring.clear()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(
            target=self._maintenance_monitor_loop,
            args=(health_interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
        # 启动定时器
        self.health_timer.start(int(health_interval * 1000))
        self.schedule_timer.start(int(schedule_interval * 1000))
        
        self.maintenance_status_changed.emit("维护监控已启动")
    
    def stop_monitoring_maintenance(self):
        """停止监控维护状态"""
        self.stop_monitoring.set()
        
        # 停止定时器
        self.health_timer.stop()
        self.schedule_timer.stop()
        
        # 等待监控线程结束
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        
        self.maintenance_status_changed.emit("维护监控已停止")
    
    def _maintenance_monitor_loop(self, interval: float):
        """维护监控循环"""
        while not self.stop_monitoring.is_set():
            try:
                with self.monitor_lock:
                    if self.is_connected():
                        # 更新诊断进度
                        if self.diagnostics_running:
                            self.update_diagnostics_progress()
                        
                        # 更新校准进度
                        if self.calibration_running:
                            self.update_calibration_progress()
                
                time.sleep(interval)
                
            except Exception as e:
                self.maintenance_status_changed.emit(f"维护监控错误: {str(e)}")
                time.sleep(interval)
    
    def update_system_health(self):
        """更新系统健康状态"""
        try:
            if not self.is_connected():
                return
            
            # 获取系统状态
            status_data = self.maintenance.get_system_status()
            
            # 创建系统健康对象
            self.system_health = SystemHealth(
                overall_status=MaintenanceStatus(status_data.get("overall_status", "normal")),
                temperature=status_data.get("temperature", 0.0),
                power_consumption=status_data.get("power_consumption", 0.0),
                uptime=status_data.get("uptime", 0.0),
                error_count=status_data.get("error_count", 0),
                warning_count=status_data.get("warning_count", 0),
                cpu_usage=status_data.get("cpu_usage", 0.0),
                memory_usage=status_data.get("memory_usage", 0.0),
                disk_usage=status_data.get("disk_usage", 0.0),
                network_status=status_data.get("network_status", "unknown"),
                last_update=time.time()
            )
            
            self.system_health_updated.emit(self.system_health)
            
        except Exception as e:
            self.maintenance_status_changed.emit(f"更新系统健康状态错误: {str(e)}")
    
    def check_maintenance_schedule(self):
        """检查维护计划"""
        try:
            if not self.is_connected():
                return
            
            # 获取维护计划
            schedule_data = self.maintenance.get_maintenance_schedule()
            
            current_time = time.time()
            next_maintenance = schedule_data.get("next_maintenance", current_time + 86400)
            
            # 检查是否需要维护
            if next_maintenance <= current_time:
                maintenance_type = schedule_data.get("maintenance_type", "routine")
                self.maintenance_due.emit(maintenance_type, schedule_data)
            
            # 检查是否即将需要维护（提前7天提醒）
            elif next_maintenance - current_time <= 86400 * 7:
                days_remaining = int((next_maintenance - current_time) / 86400)
                self.maintenance_status_changed.emit(f"维护提醒：还有 {days_remaining} 天需要进行维护")
            
        except Exception as e:
            self.maintenance_status_changed.emit(f"检查维护计划错误: {str(e)}")
    
    def start_diagnostics(self, test_type: DiagnosticsType = DiagnosticsType.FULL) -> bool:
        """开始诊断测试"""
        try:
            if not self.is_connected():
                self.maintenance_status_changed.emit("维护管理器未连接")
                return False
            
            if self.diagnostics_running:
                self.maintenance_status_changed.emit("诊断测试正在进行中")
                return False
            
            # 启动诊断
            success = self.maintenance.start_diagnostics(test_type.value)
            if success:
                self.diagnostics_running = True
                self.current_diagnostics_type = test_type
                self.diagnostics_progress = 0.0
                
                self.diagnostics_started.emit(test_type.value)
                self.maintenance_status_changed.emit(f"诊断测试已启动: {test_type.value}")
                return True
            else:
                self.maintenance_status_changed.emit("启动诊断测试失败")
                return False
                
        except Exception as e:
            self.maintenance_status_changed.emit(f"启动诊断测试错误: {str(e)}")
            return False
    
    def stop_diagnostics(self) -> bool:
        """停止诊断测试"""
        try:
            if not self.diagnostics_running:
                self.maintenance_status_changed.emit("没有正在进行的诊断测试")
                return False
            
            success = self.maintenance.stop_diagnostics()
            if success:
                self.diagnostics_running = False
                self.current_diagnostics_type = None
                self.diagnostics_progress = 0.0
                
                self.maintenance_status_changed.emit("诊断测试已停止")
                return True
            else:
                self.maintenance_status_changed.emit("停止诊断测试失败")
                return False
                
        except Exception as e:
            self.maintenance_status_changed.emit(f"停止诊断测试错误: {str(e)}")
            return False
    
    def update_diagnostics_progress(self):
        """更新诊断进度"""
        try:
            if not self.diagnostics_running:
                return
            
            status_data = self.maintenance.get_diagnostics_status()
            
            self.diagnostics_progress = status_data.get("progress", 0.0)
            current_test = status_data.get("current_test", "unknown")
            
            self.diagnostics_progress.emit(self.diagnostics_progress, current_test)
            
            # 检查是否完成
            if not status_data.get("running", True) or self.diagnostics_progress >= 100.0:
                self.complete_diagnostics()
            
        except Exception as e:
            self.maintenance_status_changed.emit(f"更新诊断进度错误: {str(e)}")
    
    def complete_diagnostics(self):
        """完成诊断测试"""
        try:
            # 获取诊断结果
            results_data = self.maintenance.get_diagnostics_results()
            
            # 创建诊断结果对象
            result = DiagnosticsResult(
                id=f"diag_{int(time.time())}",
                timestamp=results_data.get("test_date", time.time()),
                test_type=self.current_diagnostics_type or DiagnosticsType.FULL,
                duration=results_data.get("test_duration", 0.0),
                overall_result=results_data.get("overall_result", "unknown"),
                tests_completed=results_data.get("tests_completed", 0),
                tests_total=results_data.get("tests_total", 0),
                errors_found=results_data.get("errors_found", 0),
                warnings_found=results_data.get("warnings_found", 0),
                test_details=results_data.get("tests", []),
                recommendations=results_data.get("recommendations", [])
            )
            
            # 保存结果
            self.diagnostics_results.append(result)
            
            # 重置状态
            self.diagnostics_running = False
            self.current_diagnostics_type = None
            self.diagnostics_progress = 0.0
            
            self.diagnostics_completed.emit(result)
            self.maintenance_status_changed.emit(f"诊断测试完成: {result.overall_result}")
            
        except Exception as e:
            self.maintenance_status_changed.emit(f"完成诊断测试错误: {str(e)}")
    
    def start_calibration(self, joint_id: int = -1) -> bool:
        """开始校准（-1表示所有关节）"""
        try:
            if not self.is_connected():
                self.maintenance_status_changed.emit("维护管理器未连接")
                return False
            
            if self.calibration_running:
                self.maintenance_status_changed.emit("校准正在进行中")
                return False
            
            # 启动校准
            if joint_id == -1:
                success = self.maintenance.calibrate_all_joints()
            else:
                success = self.maintenance.calibrate_joint(joint_id)
            
            if success:
                self.calibration_running = True
                self.current_calibration_joint = joint_id
                self.calibration_progress = 0.0
                
                self.calibration_started.emit(joint_id)
                joint_desc = "所有关节" if joint_id == -1 else f"关节{joint_id}"
                self.maintenance_status_changed.emit(f"校准已启动: {joint_desc}")
                return True
            else:
                self.maintenance_status_changed.emit("启动校准失败")
                return False
                
        except Exception as e:
            self.maintenance_status_changed.emit(f"启动校准错误: {str(e)}")
            return False
    
    def update_calibration_progress(self):
        """更新校准进度"""
        try:
            if not self.calibration_running:
                return
            
            status_data = self.maintenance.get_calibration_status()
            
            self.calibration_progress = status_data.get("progress", 0.0)
            current_joint = status_data.get("current_joint", -1)
            
            self.calibration_progress.emit(current_joint, self.calibration_progress)
            
            # 检查是否完成
            if not status_data.get("running", True) or self.calibration_progress >= 100.0:
                self.complete_calibration()
            
        except Exception as e:
            self.maintenance_status_changed.emit(f"更新校准进度错误: {str(e)}")
    
    def complete_calibration(self):
        """完成校准"""
        try:
            joint_id = self.current_calibration_joint
            
            # 重置状态
            self.calibration_running = False
            self.current_calibration_joint = -1
            self.calibration_progress = 0.0
            
            self.calibration_completed.emit(joint_id, True, "校准完成")
            
            joint_desc = "所有关节" if joint_id == -1 else f"关节{joint_id}"
            self.maintenance_status_changed.emit(f"校准完成: {joint_desc}")
            
        except Exception as e:
            self.maintenance_status_changed.emit(f"完成校准错误: {str(e)}")
    
    def add_maintenance_record(self, record: MaintenanceRecord):
        """添加维护记录"""
        try:
            self.maintenance_records.append(record)
            self.maintenance_record_added.emit(record)
            
            # 更新维护计划
            if record.maintenance_type in self.maintenance_intervals:
                interval = self.maintenance_intervals[record.maintenance_type]
                next_maintenance = record.timestamp + interval
                self.maintenance_schedule[record.maintenance_type.value] = next_maintenance
            
            self.maintenance_status_changed.emit(f"维护记录已添加: {record.description}")
            
        except Exception as e:
            self.maintenance_status_changed.emit(f"添加维护记录错误: {str(e)}")
    
    def get_maintenance_records(self, maintenance_type: Optional[MaintenanceType] = None, 
                              start_date: Optional[float] = None, 
                              end_date: Optional[float] = None) -> List[MaintenanceRecord]:
        """获取维护记录"""
        records = self.maintenance_records
        
        # 按类型过滤
        if maintenance_type:
            records = [r for r in records if r.maintenance_type == maintenance_type]
        
        # 按日期过滤
        if start_date:
            records = [r for r in records if r.timestamp >= start_date]
        
        if end_date:
            records = [r for r in records if r.timestamp <= end_date]
        
        return records
    
    def get_diagnostics_results(self, test_type: Optional[DiagnosticsType] = None,
                               start_date: Optional[float] = None,
                               end_date: Optional[float] = None) -> List[DiagnosticsResult]:
        """获取诊断结果"""
        results = self.diagnostics_results
        
        # 按类型过滤
        if test_type:
            results = [r for r in results if r.test_type == test_type]
        
        # 按日期过滤
        if start_date:
            results = [r for r in results if r.timestamp >= start_date]
        
        if end_date:
            results = [r for r in results if r.timestamp <= end_date]
        
        return results
    
    def reset_error_count(self) -> bool:
        """重置错误计数"""
        try:
            if not self.is_connected():
                self.maintenance_status_changed.emit("维护管理器未连接")
                return False
            
            success = self.maintenance.reset_error_count()
            if success:
                self.maintenance_status_changed.emit("错误计数已重置")
                self.update_system_health()
                return True
            else:
                self.maintenance_status_changed.emit("重置错误计数失败")
                return False
                
        except Exception as e:
            self.maintenance_status_changed.emit(f"重置错误计数错误: {str(e)}")
            return False
    
    def reset_warning_count(self) -> bool:
        """重置警告计数"""
        try:
            if not self.is_connected():
                self.maintenance_status_changed.emit("维护管理器未连接")
                return False
            
            success = self.maintenance.reset_warning_count()
            if success:
                self.maintenance_status_changed.emit("警告计数已重置")
                self.update_system_health()
                return True
            else:
                self.maintenance_status_changed.emit("重置警告计数失败")
                return False
                
        except Exception as e:
            self.maintenance_status_changed.emit(f"重置警告计数错误: {str(e)}")
            return False
    
    def export_maintenance_log(self, file_path: str) -> bool:
        """导出维护日志"""
        try:
            # 准备导出数据
            export_data = {
                "export_time": time.time(),
                "robot_ip": self.robot_ip,
                "system_health": asdict(self.system_health) if self.system_health else None,
                "maintenance_records": [asdict(record) for record in self.maintenance_records],
                "diagnostics_results": [asdict(result) for result in self.diagnostics_results],
                "maintenance_schedule": self.maintenance_schedule
            }
            
            # 处理枚举类型
            for record_data in export_data["maintenance_records"]:
                record_data["maintenance_type"] = record_data["maintenance_type"].value
                record_data["status"] = record_data["status"].value
            
            for result_data in export_data["diagnostics_results"]:
                result_data["test_type"] = result_data["test_type"].value
            
            if export_data["system_health"]:
                export_data["system_health"]["overall_status"] = export_data["system_health"]["overall_status"].value
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            # 调用远程导出
            if self.is_connected():
                self.maintenance.export_maintenance_log(file_path)
            
            self.maintenance_status_changed.emit(f"维护日志已导出到: {file_path}")
            return True
            
        except Exception as e:
            self.maintenance_status_changed.emit(f"导出维护日志失败: {str(e)}")
            return False
    
    def import_maintenance_config(self, file_path: str) -> bool:
        """导入维护配置"""
        try:
            if not os.path.exists(file_path):
                self.maintenance_status_changed.emit(f"配置文件不存在: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 导入维护间隔配置
            if "maintenance_intervals" in config_data:
                for type_str, interval in config_data["maintenance_intervals"].items():
                    try:
                        maintenance_type = MaintenanceType(type_str)
                        self.maintenance_intervals[maintenance_type] = interval
                    except ValueError:
                        continue
            
            # 导入维护计划
            if "maintenance_schedule" in config_data:
                self.maintenance_schedule.update(config_data["maintenance_schedule"])
            
            # 调用远程导入
            if self.is_connected():
                self.maintenance.import_maintenance_config(file_path)
            
            self.maintenance_status_changed.emit(f"维护配置已导入: {file_path}")
            return True
            
        except Exception as e:
            self.maintenance_status_changed.emit(f"导入维护配置失败: {str(e)}")
            return False
    
    def update_firmware(self, firmware_path: str) -> bool:
        """更新固件"""
        try:
            if not self.is_connected():
                self.maintenance_status_changed.emit("维护管理器未连接")
                return False
            
            if not os.path.exists(firmware_path):
                self.maintenance_status_changed.emit(f"固件文件不存在: {firmware_path}")
                return False
            
            self.maintenance_status_changed.emit("开始固件更新...")
            
            # 模拟固件更新进度
            for progress in range(0, 101, 10):
                self.firmware_update_progress.emit(float(progress), f"更新进度: {progress}%")
                time.sleep(0.1)  # 模拟更新时间
            
            success = self.maintenance.update_firmware(firmware_path)
            if success:
                self.maintenance_status_changed.emit("固件更新完成")
                return True
            else:
                self.maintenance_status_changed.emit("固件更新失败")
                return False
                
        except Exception as e:
            self.maintenance_status_changed.emit(f"固件更新错误: {str(e)}")
            return False
    
    def backup_system(self, backup_path: str) -> bool:
        """系统备份"""
        try:
            if not self.is_connected():
                self.maintenance_status_changed.emit("维护管理器未连接")
                return False
            
            self.maintenance_status_changed.emit("开始系统备份...")
            
            # 模拟备份进度
            for progress in range(0, 101, 5):
                self.backup_progress.emit(float(progress), f"备份进度: {progress}%")
                time.sleep(0.05)  # 模拟备份时间
            
            success = self.maintenance.backup_system(backup_path)
            if success:
                self.maintenance_status_changed.emit(f"系统备份完成: {backup_path}")
                return True
            else:
                self.maintenance_status_changed.emit("系统备份失败")
                return False
                
        except Exception as e:
            self.maintenance_status_changed.emit(f"系统备份错误: {str(e)}")
            return False
    
    def restore_system(self, backup_path: str) -> bool:
        """系统恢复"""
        try:
            if not self.is_connected():
                self.maintenance_status_changed.emit("维护管理器未连接")
                return False
            
            if not os.path.exists(backup_path):
                self.maintenance_status_changed.emit(f"备份文件不存在: {backup_path}")
                return False
            
            self.maintenance_status_changed.emit("开始系统恢复...")
            
            success = self.maintenance.restore_system(backup_path)
            if success:
                self.maintenance_status_changed.emit(f"系统恢复完成: {backup_path}")
                return True
            else:
                self.maintenance_status_changed.emit("系统恢复失败")
                return False
                
        except Exception as e:
            self.maintenance_status_changed.emit(f"系统恢复错误: {str(e)}")
            return False
    
    def get_system_info(self) -> Optional[Dict[str, Any]]:
        """获取系统信息"""
        try:
            if not self.is_connected():
                return None
            
            return self.maintenance.get_system_info()
            
        except Exception as e:
            self.maintenance_status_changed.emit(f"获取系统信息错误: {str(e)}")
            return None
    
    def get_joint_info(self, joint_id: int) -> Optional[Dict[str, Any]]:
        """获取关节信息"""
        try:
            if not self.is_connected():
                return None
            
            if joint_id < 0 or joint_id >= 7:
                self.maintenance_status_changed.emit(f"无效的关节ID: {joint_id}")
                return None
            
            return self.maintenance.get_joint_info(joint_id)
            
        except Exception as e:
            self.maintenance_status_changed.emit(f"获取关节信息错误: {str(e)}")
            return None
    
    def get_maintenance_summary(self) -> Dict[str, Any]:
        """获取维护摘要"""
        return {
            "connected": self.is_connected(),
            "system_health": asdict(self.system_health) if self.system_health else None,
            "diagnostics_running": self.diagnostics_running,
            "calibration_running": self.calibration_running,
            "total_maintenance_records": len(self.maintenance_records),
            "total_diagnostics_results": len(self.diagnostics_results),
            "maintenance_schedule": self.maintenance_schedule,
            "last_update": time.time()
        }