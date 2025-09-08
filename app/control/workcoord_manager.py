'''
Author: LK
Date: 2025-01-XX XX:XX:XX
LastEditTime: 2025-01-XX XX:XX:XX
LastEditors: LK
FilePath: /Demo/app/control/workcoord_manager.py
'''

import threading
import time
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from dataclasses import dataclass, asdict
from enum import Enum

# 导入线程管理器和资源管理器
from ..core.thread_manager import get_thread_manager
from ..core.resource_manager import get_resource_manager, ResourceType, AccessMode

try:
    from flexiv import WorkCoord, Coord
except ImportError:
    # 仿真模式下的模拟类
    class WorkCoord:
        def __init__(self, robot_ip: str):
            self.robot_ip = robot_ip
            self.connected = False
            self.work_coords = {}
            self.current_coord = "WORLD"
        
        def connect(self) -> bool:
            self.connected = True
            return True
        
        def disconnect(self):
            self.connected = False
        
        def is_connected(self) -> bool:
            return self.connected
        
        def add_work_coord(self, name: str, coord: 'Coord') -> bool:
            self.work_coords[name] = coord
            return True
        
        def remove_work_coord(self, name: str) -> bool:
            if name in self.work_coords:
                del self.work_coords[name]
                return True
            return False
        
        def update_work_coord(self, name: str, coord: 'Coord') -> bool:
            if name in self.work_coords:
                self.work_coords[name] = coord
                return True
            return False
        
        def get_work_coord(self, name: str) -> Optional['Coord']:
            return self.work_coords.get(name)
        
        def get_work_coord_list(self) -> List[str]:
            return list(self.work_coords.keys())
        
        def set_current_work_coord(self, name: str) -> bool:
            if name in self.work_coords or name == "WORLD":
                self.current_coord = name
                return True
            return False
        
        def get_current_work_coord(self) -> str:
            return self.current_coord
        
        def calibrate_work_coord(self, name: str, points: List['Coord']) -> bool:
            # 模拟标定过程
            if len(points) >= 3:
                # 简单的平面拟合
                origin = points[0]
                self.work_coords[name] = origin
                return True
            return False
        
        def transform_coord(self, coord: 'Coord', from_frame: str, to_frame: str) -> 'Coord':
            # 简单的坐标变换模拟
            return coord
        
        def save_work_coords(self, file_path: str) -> bool:
            return True
        
        def load_work_coords(self, file_path: str) -> bool:
            return True
    
    class Coord:
        def __init__(self, pos: List[float] = None, rot: List[float] = None, ref: List[str] = None):
            self.pos = pos or [0.0, 0.0, 0.0]  # [x, y, z] in meters
            self.rot = rot or [0.0, 0.0, 0.0]  # [rx, ry, rz] in degrees
            self.ref = ref or ["WORLD", "WORLD_ORIGIN"]  # [coordinate_frame, reference_point]
        
        def to_matrix(self) -> np.ndarray:
            """转换为4x4变换矩阵"""
            # 简化的变换矩阵计算
            matrix = np.eye(4)
            matrix[0:3, 3] = self.pos
            return matrix
        
        def from_matrix(self, matrix: np.ndarray):
            """从4x4变换矩阵设置坐标"""
            self.pos = matrix[0:3, 3].tolist()
            # 简化的旋转角度提取
            self.rot = [0.0, 0.0, 0.0]
        
        def copy(self) -> 'Coord':
            return Coord(self.pos.copy(), self.rot.copy(), self.ref.copy())
        
        def __str__(self) -> str:
            return f"Coord(pos={self.pos}, rot={self.rot}, ref={self.ref})"

class CoordType(Enum):
    """坐标系类型"""
    WORLD = "WORLD"           # 世界坐标系
    BASE = "BASE"             # 基座坐标系
    TOOL = "TOOL"             # 工具坐标系
    WORK = "WORK"             # 工作坐标系
    USER = "USER"             # 用户坐标系
    FIXTURE = "FIXTURE"       # 夹具坐标系
    PART = "PART"             # 零件坐标系

class CalibrationMethod(Enum):
    """标定方法"""
    THREE_POINT = "three_point"     # 三点法
    FOUR_POINT = "four_point"       # 四点法
    PLANE_FIT = "plane_fit"         # 平面拟合
    MANUAL = "manual"               # 手动设置
    TEACH = "teach"                 # 示教

@dataclass
class WorkCoordDefinition:
    """工作坐标系定义"""
    name: str
    description: str
    coord_type: CoordType
    origin: Coord
    x_axis: Optional[Coord] = None
    y_axis: Optional[Coord] = None
    z_axis: Optional[Coord] = None
    calibration_method: CalibrationMethod = CalibrationMethod.MANUAL
    calibration_points: List[Coord] = None
    created_time: float = 0.0
    modified_time: float = 0.0
    active: bool = True
    
    def __post_init__(self):
        if self.calibration_points is None:
            self.calibration_points = []
        if self.created_time == 0.0:
            self.created_time = time.time()
        self.modified_time = time.time()

@dataclass
class CoordTransform:
    """坐标变换记录"""
    from_frame: str
    to_frame: str
    transform_matrix: np.ndarray
    timestamp: float
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

class WorkCoordManager(QObject):
    """工作坐标系管理器
    
    负责管理机器人工作坐标系，包括：
    - 工作坐标系定义和管理
    - 坐标系标定
    - 坐标变换
    - 坐标系切换
    - 坐标系保存和加载
    - 坐标系可视化
    """
    
    # 信号定义
    work_coord_added = pyqtSignal(str, object)  # name, WorkCoordDefinition
    work_coord_removed = pyqtSignal(str)  # name
    work_coord_updated = pyqtSignal(str, object)  # name, WorkCoordDefinition
    current_coord_changed = pyqtSignal(str, str)  # old_name, new_name
    calibration_started = pyqtSignal(str, str)  # coord_name, method
    calibration_completed = pyqtSignal(str, bool, str)  # coord_name, success, message
    coord_transform_completed = pyqtSignal(object, object)  # from_coord, to_coord
    workcoord_status_changed = pyqtSignal(str)  # status_message
    
    def __init__(self, robot=None, hardware=True, robot_ip: str = "192.168.2.100", parent=None):
        super().__init__(parent)
        
        self.robot = robot
        self.hardware = hardware
        self.robot_ip = robot_ip
        self.workcoord = None
        self.connected = False
        
        # 坐标系管理
        self.work_coords = {}  # name -> WorkCoordDefinition
        self.current_coord_name = "WORLD"
        
        # 标定数据
        self.calibration_points = {}  # coord_name -> List[Coord]
        self.calibration_in_progress = False
        self.current_calibration_coord = None
        self.current_calibration_method = None
        
        # 变换缓存
        self.transform_cache = {}  # (from_frame, to_frame) -> CoordTransform
        self.cache_timeout = 60.0  # 缓存超时时间（秒）
        
        # 监控线程
        self.monitor_thread = None
        self.monitor_lock = threading.Lock()
        self.stop_monitoring = threading.Event()
        
        # 初始化线程管理器和资源管理器
        self.thread_manager = get_thread_manager()
        self.resource_manager = get_resource_manager()
        
        # 注册工作坐标系资源
        self.resource_manager.register_resource(
            resource_id=f"workcoord_{self.robot_ip}",
            resource_type=ResourceType.CUSTOM,
            metadata={
                "robot_ip": self.robot_ip,
                "type": "workcoord"
            }
        )
        
        # 定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        
        # 预定义坐标系
        self.init_predefined_coords()
        
        # 初始化
        self.init_workcoord()
    
    def init_workcoord(self):
        """初始化工作坐标系管理器"""
        try:
            self.workcoord = WorkCoord(self.robot_ip)
            self.workcoord_status_changed.emit("工作坐标系管理器已初始化")
        except Exception as e:
            self.workcoord_status_changed.emit(f"工作坐标系管理器初始化失败: {str(e)}")
    
    def init_predefined_coords(self):
        """初始化预定义坐标系"""
        # 世界坐标系
        world_coord = WorkCoordDefinition(
            name="WORLD",
            description="世界坐标系（机器人基座）",
            coord_type=CoordType.WORLD,
            origin=Coord([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], ["WORLD", "WORLD_ORIGIN"])
        )
        self.work_coords["WORLD"] = world_coord
        
        # 基座坐标系
        base_coord = WorkCoordDefinition(
            name="BASE",
            description="机器人基座坐标系",
            coord_type=CoordType.BASE,
            origin=Coord([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], ["WORLD", "WORLD_ORIGIN"])
        )
        self.work_coords["BASE"] = base_coord
    
    def connect_workcoord(self) -> bool:
        """连接工作坐标系管理器"""
        try:
            if not self.workcoord:
                self.init_workcoord()
            
            if self.workcoord and self.workcoord.connect():
                self.connected = True
                self.workcoord_status_changed.emit("工作坐标系管理器已连接")
                
                # 同步远程坐标系
                self.sync_remote_coords()
                
                return True
            else:
                self.workcoord_status_changed.emit("工作坐标系管理器连接失败")
                return False
                
        except Exception as e:
            self.workcoord_status_changed.emit(f"工作坐标系管理器连接错误: {str(e)}")
            return False
    
    def disconnect_workcoord(self):
        """断开工作坐标系管理器连接"""
        try:
            self.stop_monitoring_workcoord()
            
            if self.workcoord and self.connected:
                self.workcoord.disconnect()
                self.connected = False
                self.workcoord_status_changed.emit("工作坐标系管理器已断开")
                
        except Exception as e:
            self.workcoord_status_changed.emit(f"工作坐标系管理器断开错误: {str(e)}")
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.connected and self.workcoord and self.workcoord.is_connected()
    
    def start_monitoring_workcoord(self, interval: float = 1.0):
        """开始监控工作坐标系"""
        if not self.is_connected():
            self.workcoord_status_changed.emit("工作坐标系管理器未连接，无法开始监控")
            return
        
        self.stop_monitoring.clear()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(
            target=self._workcoord_monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
        # 启动状态定时器
        self.status_timer.start(int(interval * 1000))
        
        self.workcoord_status_changed.emit("工作坐标系监控已启动")
    
    def stop_monitoring_workcoord(self):
        """停止监控工作坐标系"""
        self.stop_monitoring.set()
        
        # 停止定时器
        self.status_timer.stop()
        
        # 等待监控线程结束
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        
        self.workcoord_status_changed.emit("工作坐标系监控已停止")
    
    def _workcoord_monitor_loop(self, interval: float):
        """工作坐标系监控循环"""
        while not self.stop_monitoring.is_set():
            try:
                with self.monitor_lock:
                    if self.is_connected():
                        # 检查当前坐标系是否变化
                        current_coord = self.workcoord.get_current_work_coord()
                        if current_coord != self.current_coord_name:
                            old_coord = self.current_coord_name
                            self.current_coord_name = current_coord
                            self.current_coord_changed.emit(old_coord, current_coord)
                        
                        # 清理过期的变换缓存
                        self.cleanup_transform_cache()
                
                time.sleep(interval)
                
            except Exception as e:
                self.workcoord_status_changed.emit(f"工作坐标系监控错误: {str(e)}")
                time.sleep(interval)
    
    def sync_remote_coords(self):
        """同步远程坐标系"""
        try:
            if not self.is_connected():
                return
            
            # 获取远程坐标系列表
            remote_coords = self.workcoord.get_work_coord_list()
            
            for coord_name in remote_coords:
                if coord_name not in self.work_coords:
                    # 获取远程坐标系定义
                    coord = self.workcoord.get_work_coord(coord_name)
                    if coord:
                        # 创建本地定义
                        work_coord_def = WorkCoordDefinition(
                            name=coord_name,
                            description=f"远程坐标系: {coord_name}",
                            coord_type=CoordType.USER,
                            origin=coord
                        )
                        self.work_coords[coord_name] = work_coord_def
                        self.work_coord_added.emit(coord_name, work_coord_def)
            
            # 获取当前坐标系
            current_coord = self.workcoord.get_current_work_coord()
            if current_coord != self.current_coord_name:
                old_coord = self.current_coord_name
                self.current_coord_name = current_coord
                self.current_coord_changed.emit(old_coord, current_coord)
            
            self.workcoord_status_changed.emit("远程坐标系同步完成")
            
        except Exception as e:
            self.workcoord_status_changed.emit(f"同步远程坐标系失败: {str(e)}")
    
    def add_work_coord(self, work_coord_def: WorkCoordDefinition) -> bool:
        """添加工作坐标系"""
        try:
            if work_coord_def.name in self.work_coords:
                self.workcoord_status_changed.emit(f"坐标系已存在: {work_coord_def.name}")
                return False
            
            # 添加到本地
            self.work_coords[work_coord_def.name] = work_coord_def
            
            # 添加到远程
            if self.is_connected():
                success = self.workcoord.add_work_coord(work_coord_def.name, work_coord_def.origin)
                if not success:
                    # 回滚本地添加
                    self.work_coords.pop(work_coord_def.name, None)
                    self.workcoord_status_changed.emit(f"添加远程坐标系失败: {work_coord_def.name}")
                    return False
            
            self.work_coord_added.emit(work_coord_def.name, work_coord_def)
            self.workcoord_status_changed.emit(f"工作坐标系已添加: {work_coord_def.name}")
            return True
            
        except Exception as e:
            self.workcoord_status_changed.emit(f"添加工作坐标系错误: {str(e)}")
            return False
    
    def remove_work_coord(self, name: str) -> bool:
        """移除工作坐标系"""
        try:
            if name not in self.work_coords:
                self.workcoord_status_changed.emit(f"坐标系不存在: {name}")
                return False
            
            if name in ["WORLD", "BASE"]:
                self.workcoord_status_changed.emit(f"不能删除系统坐标系: {name}")
                return False
            
            # 从远程移除
            if self.is_connected():
                success = self.workcoord.remove_work_coord(name)
                if not success:
                    self.workcoord_status_changed.emit(f"移除远程坐标系失败: {name}")
                    return False
            
            # 从本地移除
            self.work_coords.pop(name, None)
            
            # 清理相关数据
            self.calibration_points.pop(name, None)
            
            # 如果是当前坐标系，切换到世界坐标系
            if self.current_coord_name == name:
                self.set_current_work_coord("WORLD")
            
            self.work_coord_removed.emit(name)
            self.workcoord_status_changed.emit(f"工作坐标系已移除: {name}")
            return True
            
        except Exception as e:
            self.workcoord_status_changed.emit(f"移除工作坐标系错误: {str(e)}")
            return False
    
    def update_work_coord(self, name: str, work_coord_def: WorkCoordDefinition) -> bool:
        """更新工作坐标系"""
        try:
            if name not in self.work_coords:
                self.workcoord_status_changed.emit(f"坐标系不存在: {name}")
                return False
            
            # 更新本地
            work_coord_def.modified_time = time.time()
            self.work_coords[name] = work_coord_def
            
            # 更新远程
            if self.is_connected():
                success = self.workcoord.update_work_coord(name, work_coord_def.origin)
                if not success:
                    self.workcoord_status_changed.emit(f"更新远程坐标系失败: {name}")
                    return False
            
            self.work_coord_updated.emit(name, work_coord_def)
            self.workcoord_status_changed.emit(f"工作坐标系已更新: {name}")
            return True
            
        except Exception as e:
            self.workcoord_status_changed.emit(f"更新工作坐标系错误: {str(e)}")
            return False
    
    def get_work_coord(self, name: str) -> Optional[WorkCoordDefinition]:
        """获取工作坐标系定义"""
        return self.work_coords.get(name)
    
    def get_work_coord_list(self) -> List[str]:
        """获取工作坐标系列表"""
        return list(self.work_coords.keys())
    
    def set_current_work_coord(self, name: str) -> bool:
        """设置当前工作坐标系"""
        try:
            if name not in self.work_coords:
                self.workcoord_status_changed.emit(f"坐标系不存在: {name}")
                return False
            
            # 设置远程当前坐标系
            if self.is_connected():
                success = self.workcoord.set_current_work_coord(name)
                if not success:
                    self.workcoord_status_changed.emit(f"设置远程当前坐标系失败: {name}")
                    return False
            
            # 更新本地当前坐标系
            old_coord = self.current_coord_name
            self.current_coord_name = name
            
            self.current_coord_changed.emit(old_coord, name)
            self.workcoord_status_changed.emit(f"当前工作坐标系已设置为: {name}")
            return True
            
        except Exception as e:
            self.workcoord_status_changed.emit(f"设置当前工作坐标系错误: {str(e)}")
            return False
    
    def get_current_work_coord(self) -> str:
        """获取当前工作坐标系名称"""
        return self.current_coord_name
    
    def start_calibration(self, name: str, method: CalibrationMethod) -> bool:
        """开始坐标系标定"""
        try:
            if self.calibration_in_progress:
                self.workcoord_status_changed.emit("标定正在进行中")
                return False
            
            self.calibration_in_progress = True
            self.current_calibration_coord = name
            self.current_calibration_method = method
            self.calibration_points[name] = []
            
            self.calibration_started.emit(name, method.value)
            self.workcoord_status_changed.emit(f"开始标定坐标系: {name}，方法: {method.value}")
            return True
            
        except Exception as e:
            self.workcoord_status_changed.emit(f"开始标定错误: {str(e)}")
            return False
    
    def add_calibration_point(self, coord: Coord) -> bool:
        """添加标定点"""
        try:
            if not self.calibration_in_progress or not self.current_calibration_coord:
                self.workcoord_status_changed.emit("没有正在进行的标定")
                return False
            
            coord_name = self.current_calibration_coord
            if coord_name not in self.calibration_points:
                self.calibration_points[coord_name] = []
            
            self.calibration_points[coord_name].append(coord.copy())
            
            point_count = len(self.calibration_points[coord_name])
            self.workcoord_status_changed.emit(f"已添加标定点 {point_count}: {coord}")
            return True
            
        except Exception as e:
            self.workcoord_status_changed.emit(f"添加标定点错误: {str(e)}")
            return False
    
    def complete_calibration(self) -> bool:
        """完成坐标系标定"""
        try:
            if not self.calibration_in_progress or not self.current_calibration_coord:
                self.workcoord_status_changed.emit("没有正在进行的标定")
                return False
            
            coord_name = self.current_calibration_coord
            method = self.current_calibration_method
            points = self.calibration_points.get(coord_name, [])
            
            # 检查点数是否足够
            min_points = {
                CalibrationMethod.THREE_POINT: 3,
                CalibrationMethod.FOUR_POINT: 4,
                CalibrationMethod.PLANE_FIT: 3,
                CalibrationMethod.MANUAL: 1,
                CalibrationMethod.TEACH: 1
            }
            
            required_points = min_points.get(method, 3)
            if len(points) < required_points:
                message = f"标定点不足，需要至少 {required_points} 个点，当前有 {len(points)} 个点"
                self.calibration_completed.emit(coord_name, False, message)
                return False
            
            # 执行标定计算
            success, result_coord, message = self.calculate_calibration(method, points)
            
            if success:
                # 创建或更新工作坐标系
                if coord_name in self.work_coords:
                    work_coord_def = self.work_coords[coord_name]
                    work_coord_def.origin = result_coord
                    work_coord_def.calibration_method = method
                    work_coord_def.calibration_points = points.copy()
                    work_coord_def.modified_time = time.time()
                else:
                    work_coord_def = WorkCoordDefinition(
                        name=coord_name,
                        description=f"标定坐标系 ({method.value})",
                        coord_type=CoordType.USER,
                        origin=result_coord,
                        calibration_method=method,
                        calibration_points=points.copy()
                    )
                    self.work_coords[coord_name] = work_coord_def
                
                # 添加到远程
                if self.is_connected():
                    if coord_name in self.work_coords:
                        self.workcoord.update_work_coord(coord_name, result_coord)
                    else:
                        self.workcoord.add_work_coord(coord_name, result_coord)
                
                # 发送信号
                if coord_name in self.work_coords:
                    self.work_coord_updated.emit(coord_name, work_coord_def)
                else:
                    self.work_coord_added.emit(coord_name, work_coord_def)
            
            # 清理标定状态
            self.calibration_in_progress = False
            self.current_calibration_coord = None
            self.current_calibration_method = None
            
            self.calibration_completed.emit(coord_name, success, message)
            return success
            
        except Exception as e:
            self.calibration_in_progress = False
            self.current_calibration_coord = None
            self.current_calibration_method = None
            
            message = f"标定计算错误: {str(e)}"
            self.calibration_completed.emit(coord_name or "unknown", False, message)
            return False
    
    def cancel_calibration(self):
        """取消坐标系标定"""
        if self.calibration_in_progress:
            coord_name = self.current_calibration_coord
            
            self.calibration_in_progress = False
            self.current_calibration_coord = None
            self.current_calibration_method = None
            
            if coord_name:
                self.calibration_points.pop(coord_name, None)
            
            self.workcoord_status_changed.emit("坐标系标定已取消")
    
    def calculate_calibration(self, method: CalibrationMethod, points: List[Coord]) -> Tuple[bool, Coord, str]:
        """计算标定结果"""
        try:
            if method == CalibrationMethod.THREE_POINT:
                return self.calculate_three_point_calibration(points)
            elif method == CalibrationMethod.FOUR_POINT:
                return self.calculate_four_point_calibration(points)
            elif method == CalibrationMethod.PLANE_FIT:
                return self.calculate_plane_fit_calibration(points)
            elif method == CalibrationMethod.MANUAL:
                return True, points[0].copy(), "手动设置坐标系"
            elif method == CalibrationMethod.TEACH:
                return True, points[0].copy(), "示教设置坐标系"
            else:
                return False, Coord(), "未知的标定方法"
                
        except Exception as e:
            return False, Coord(), f"标定计算错误: {str(e)}"
    
    def calculate_three_point_calibration(self, points: List[Coord]) -> Tuple[bool, Coord, str]:
        """三点法标定"""
        if len(points) < 3:
            return False, Coord(), "需要至少3个点"
        
        # 简化的三点法计算
        origin = points[0].copy()
        
        # 计算X轴方向（原点到第二点）
        x_vec = np.array(points[1].pos) - np.array(points[0].pos)
        x_vec = x_vec / np.linalg.norm(x_vec)
        
        # 计算Y轴方向（原点到第三点在XY平面的投影）
        y_temp = np.array(points[2].pos) - np.array(points[0].pos)
        y_vec = y_temp - np.dot(y_temp, x_vec) * x_vec
        y_vec = y_vec / np.linalg.norm(y_vec)
        
        # 计算Z轴方向（X轴叉乘Y轴）
        z_vec = np.cross(x_vec, y_vec)
        
        # 构建旋转矩阵并转换为欧拉角（简化）
        # 这里使用简化的角度计算
        origin.rot = [0.0, 0.0, 0.0]  # 简化处理
        
        return True, origin, "三点法标定完成"
    
    def calculate_four_point_calibration(self, points: List[Coord]) -> Tuple[bool, Coord, str]:
        """四点法标定"""
        if len(points) < 4:
            return False, Coord(), "需要至少4个点"
        
        # 简化的四点法计算，使用前三点进行标定
        return self.calculate_three_point_calibration(points[:3])
    
    def calculate_plane_fit_calibration(self, points: List[Coord]) -> Tuple[bool, Coord, str]:
        """平面拟合标定"""
        if len(points) < 3:
            return False, Coord(), "需要至少3个点"
        
        # 简化的平面拟合，使用第一个点作为原点
        origin = points[0].copy()
        
        # 计算平面法向量（简化）
        if len(points) >= 3:
            v1 = np.array(points[1].pos) - np.array(points[0].pos)
            v2 = np.array(points[2].pos) - np.array(points[0].pos)
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)
            
            # 设置Z轴为法向量方向（简化）
            origin.rot = [0.0, 0.0, 0.0]  # 简化处理
        
        return True, origin, "平面拟合标定完成"
    
    def transform_coord(self, coord: Coord, from_frame: str, to_frame: str) -> Optional[Coord]:
        """坐标变换"""
        try:
            if from_frame == to_frame:
                return coord.copy()
            
            # 检查缓存
            cache_key = (from_frame, to_frame)
            if cache_key in self.transform_cache:
                transform = self.transform_cache[cache_key]
                if time.time() - transform.timestamp < self.cache_timeout:
                    # 使用缓存的变换
                    result_coord = self.apply_transform(coord, transform.transform_matrix)
                    self.coord_transform_completed.emit(coord, result_coord)
                    return result_coord
            
            # 执行变换
            if self.is_connected():
                result_coord = self.workcoord.transform_coord(coord, from_frame, to_frame)
                if result_coord:
                    self.coord_transform_completed.emit(coord, result_coord)
                    return result_coord
            
            # 本地变换（简化）
            result_coord = self.local_transform_coord(coord, from_frame, to_frame)
            if result_coord:
                self.coord_transform_completed.emit(coord, result_coord)
                return result_coord
            
            return None
            
        except Exception as e:
            self.workcoord_status_changed.emit(f"坐标变换错误: {str(e)}")
            return None
    
    def local_transform_coord(self, coord: Coord, from_frame: str, to_frame: str) -> Optional[Coord]:
        """本地坐标变换（简化实现）"""
        try:
            from_coord_def = self.work_coords.get(from_frame)
            to_coord_def = self.work_coords.get(to_frame)
            
            if not from_coord_def or not to_coord_def:
                return None
            
            # 简化的变换：只处理位置偏移
            result_coord = coord.copy()
            
            # 从源坐标系变换到世界坐标系
            if from_frame != "WORLD":
                origin_offset = from_coord_def.origin.pos
                result_coord.pos[0] += origin_offset[0]
                result_coord.pos[1] += origin_offset[1]
                result_coord.pos[2] += origin_offset[2]
            
            # 从世界坐标系变换到目标坐标系
            if to_frame != "WORLD":
                origin_offset = to_coord_def.origin.pos
                result_coord.pos[0] -= origin_offset[0]
                result_coord.pos[1] -= origin_offset[1]
                result_coord.pos[2] -= origin_offset[2]
            
            # 更新参考坐标系
            result_coord.ref = [to_frame, f"{to_frame}_ORIGIN"]
            
            return result_coord
            
        except Exception as e:
            self.workcoord_status_changed.emit(f"本地坐标变换错误: {str(e)}")
            return None
    
    def apply_transform(self, coord: Coord, transform_matrix: np.ndarray) -> Coord:
        """应用变换矩阵"""
        result_coord = coord.copy()
        
        # 将位置转换为齐次坐标
        pos_homogeneous = np.array([coord.pos[0], coord.pos[1], coord.pos[2], 1.0])
        
        # 应用变换
        transformed_pos = transform_matrix @ pos_homogeneous
        
        # 更新位置
        result_coord.pos = transformed_pos[:3].tolist()
        
        return result_coord
    
    def cleanup_transform_cache(self):
        """清理过期的变换缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, transform in self.transform_cache.items()
            if current_time - transform.timestamp > self.cache_timeout
        ]
        
        for key in expired_keys:
            self.transform_cache.pop(key, None)
    
    def save_work_coords(self, file_path: str) -> bool:
        """保存工作坐标系到文件"""
        try:
            # 转换为可序列化的格式
            coords_data = {}
            for name, coord_def in self.work_coords.items():
                coord_data = asdict(coord_def)
                # 处理特殊字段
                coord_data['coord_type'] = coord_def.coord_type.value
                coord_data['calibration_method'] = coord_def.calibration_method.value
                coords_data[name] = coord_data
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(coords_data, f, indent=2, ensure_ascii=False)
            
            # 保存到远程
            if self.is_connected():
                self.workcoord.save_work_coords(file_path)
            
            self.workcoord_status_changed.emit(f"工作坐标系已保存到: {file_path}")
            return True
            
        except Exception as e:
            self.workcoord_status_changed.emit(f"保存工作坐标系失败: {str(e)}")
            return False
    
    def load_work_coords(self, file_path: str) -> bool:
        """从文件加载工作坐标系"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                coords_data = json.load(f)
            
            loaded_count = 0
            for name, coord_data in coords_data.items():
                # 转换回对象
                coord_data['coord_type'] = CoordType(coord_data['coord_type'])
                coord_data['calibration_method'] = CalibrationMethod(coord_data['calibration_method'])
                
                # 重建Coord对象
                origin_data = coord_data['origin']
                coord_data['origin'] = Coord(
                    pos=origin_data['pos'],
                    rot=origin_data['rot'],
                    ref=origin_data['ref']
                )
                
                # 重建标定点
                if 'calibration_points' in coord_data:
                    points = []
                    for point_data in coord_data['calibration_points']:
                        point = Coord(
                            pos=point_data['pos'],
                            rot=point_data['rot'],
                            ref=point_data['ref']
                        )
                        points.append(point)
                    coord_data['calibration_points'] = points
                
                work_coord_def = WorkCoordDefinition(**coord_data)
                
                # 添加到本地
                self.work_coords[name] = work_coord_def
                
                # 添加到远程
                if self.is_connected():
                    self.workcoord.add_work_coord(name, work_coord_def.origin)
                
                self.work_coord_added.emit(name, work_coord_def)
                loaded_count += 1
            
            # 从远程加载
            if self.is_connected():
                self.workcoord.load_work_coords(file_path)
            
            self.workcoord_status_changed.emit(f"已加载 {loaded_count} 个工作坐标系")
            return True
            
        except Exception as e:
            self.workcoord_status_changed.emit(f"加载工作坐标系失败: {str(e)}")
            return False
    
    def get_workcoord_summary(self) -> Dict[str, Any]:
        """获取工作坐标系摘要"""
        return {
            "connected": self.is_connected(),
            "current_coord": self.current_coord_name,
            "total_coords": len(self.work_coords),
            "calibration_in_progress": self.calibration_in_progress,
            "current_calibration_coord": self.current_calibration_coord,
            "current_calibration_method": self.current_calibration_method.value if self.current_calibration_method else None,
            "transform_cache_size": len(self.transform_cache),
            "last_update": time.time()
        }
    
    def update_status(self):
        """更新状态（定时器回调）"""
        if self.is_connected():
            # 定期同步远程坐标系
            self.sync_remote_coords()