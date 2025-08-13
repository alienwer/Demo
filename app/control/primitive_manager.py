'''
Author: LK
Date: 2025-01-XX XX:XX:XX
LastEditTime: 2025-01-XX XX:XX:XX
LastEditors: LK
FilePath: /Demo/app/control/primitive_manager.py
'''

import time
import threading
from typing import Dict, Any, List, Optional, Union
from PyQt5.QtCore import QObject, pyqtSignal
from enum import Enum

try:
    from flexivrdk import Robot, Mode, Coord, JPos
    FLEXIV_AVAILABLE = True
except ImportError:
    FLEXIV_AVAILABLE = False
    # 仿真模式下的替代类
    class Coord:
        def __init__(self, pos, rot, ref):
            self.pos = pos
            self.rot = rot
            self.ref = ref
    
    class JPos:
        def __init__(self, joints, external=None):
            self.joints = joints
            self.external = external or []

class CoordinateSystem(Enum):
    """坐标系统枚举"""
    WORLD = "WORLD"
    WORK = "WORK"
    TCP = "TCP"
    TCP_START = "TCP_START"
    TRAJ_START = "TRAJ_START"
    TRAJ_GOAL = "TRAJ_GOAL"
    TRAJ_PREV = "TRAJ_PREV"

class PrimitiveCategory(Enum):
    """Primitive分类枚举"""
    WORKFLOW = "工作流控制"
    MOTION = "运动控制"
    BASIC_FORCE = "基础力控制"
    ADVANCED_FORCE = "高级力控制"
    ADAPTIVE_ASSEMBLY = "自适应装配"
    SURFACE_FINISHING = "表面处理"
    FLEXIBLE_HANDLING = "柔性处理"
    ADAPTIVE_GRASPING = "自适应抓取"
    ZERO_GRAVITY = "零重力浮动"
    SYNCHRONIZATION = "同步控制"
    REHABILITATION = "康复理疗"
    VISUAL_SERVOING = "视觉伺服"
    SHOWCASE = "展示应用"

class PrimitiveParams:
    """Primitive参数管理类"""
    
    # 定义所有Primitive的参数模式
    PRIMITIVE_SCHEMAS = {
        # 工作流控制
        "Home": {
            "category": PrimitiveCategory.WORKFLOW,
            "description": "机器人回到零位",
            "params": {},
            "required": []
        },
        "Hold": {
            "category": PrimitiveCategory.WORKFLOW,
            "description": "保持当前位置",
            "params": {
                "duration": {"type": "float", "unit": "s", "default": 1.0, "range": [0.1, 60.0]}
            },
            "required": []
        },
        "Stop": {
            "category": PrimitiveCategory.WORKFLOW,
            "description": "停止当前动作",
            "params": {},
            "required": []
        },
        "End": {
            "category": PrimitiveCategory.WORKFLOW,
            "description": "结束当前任务",
            "params": {},
            "required": []
        },
        
        # 运动控制 - 基于官方Rizon4(s) Primitive文档
        "MoveL": {
            "category": PrimitiveCategory.MOTION,
            "description": "控制机器人TCP直线运动到目标位置，可指定多个路径点",
            "params": {
                "target": {"type": "COORD", "unit": "m-deg", "required": True, "description": "目标位置和姿态"},
                "waypoints": {"type": "ARRAY_COORD", "unit": "m-deg", "default": [], "description": "中间路径点列表"},
                "vel": {"type": "float", "unit": "m/s", "default": 0.25, "range": [0.001, 2.2], "description": "TCP线速度"},
                "acc": {"type": "float", "unit": "m/s^2", "default": 1.5, "range": [0.1, 3.0], "description": "TCP线加速度"},
                "angVel": {"type": "float", "unit": "deg/s", "default": 150.0, "range": [10.0, 500.0], "description": "TCP角速度"},
                "jerk": {"type": "float", "unit": "m/s^3", "default": 50.0, "range": [50.0, 500.0], "description": "TCP加加速度"},
                "zoneRadius": {"type": "enum", "default": "Z50", "options": ["ZFine", "Z1", "Z5", "Z10", "Z15", "Z20", "Z30", "Z40", "Z50", "Z60", "Z80", "Z100", "Z150", "Z200"], "description": "路径点混合半径"},
                "targetTolerLevel": {"type": "int", "default": 3, "range": [0, 10], "description": "目标容差等级"}
            },
            "required": ["target"],
            "output_params": {
                "reachedTarget": {"type": "bool", "description": "是否到达目标位置"},
                "actualPose": {"type": "COORD", "description": "实际到达位置"}
            }
        },
        "MoveJ": {
            "category": PrimitiveCategory.MOTION,
            "description": "控制机器人关节运动到目标位置，可指定多个关节路径点",
            "params": {
                "target": {"type": "JPOS", "unit": "deg", "required": True, "description": "目标关节位置"},
                "waypoints": {"type": "ARRAY_JPOS", "unit": "deg", "default": [], "description": "中间关节路径点列表"},
                "jntVelScale": {"type": "int", "default": 20, "range": [1, 100], "description": "关节速度缩放百分比"},
                "zoneRadius": {"type": "enum", "default": "Z50", "options": ["ZFine", "Z5", "Z10", "Z15", "Z20", "Z30", "Z40", "Z50", "Z60", "Z80", "Z100", "Z150", "Z200", "ZSpline"], "description": "路径点混合半径"},
                "targetTolerLevel": {"type": "int", "default": 1, "range": [0, 10], "description": "目标容差等级"}
            },
            "required": ["target"],
            "output_params": {
                "reachedTarget": {"type": "bool", "description": "是否到达目标位置"},
                "actualJPos": {"type": "JPOS", "description": "实际到达关节位置"}
            }
        },
        "MovePTP": {
            "category": PrimitiveCategory.MOTION,
            "description": "控制机器人点到点运动到目标位置，自动规划最优路径",
            "params": {
                "target": {"type": "COORD", "unit": "m-deg", "required": True, "description": "目标位置和姿态"},
                "vel": {"type": "float", "unit": "m/s", "default": 0.25, "range": [0.001, 2.2], "description": "TCP线速度"},
                "acc": {"type": "float", "unit": "m/s^2", "default": 1.5, "range": [0.1, 3.0], "description": "TCP线加速度"},
                "angVel": {"type": "float", "unit": "deg/s", "default": 150.0, "range": [10.0, 500.0], "description": "TCP角速度"},
                "jerk": {"type": "float", "unit": "m/s^3", "default": 50.0, "range": [50.0, 500.0], "description": "TCP加加速度"},
                "targetTolerLevel": {"type": "int", "default": 3, "range": [0, 10], "description": "目标容差等级"}
            },
            "required": ["target"],
            "output_params": {
                "reachedTarget": {"type": "bool", "description": "是否到达目标位置"},
                "actualPose": {"type": "COORD", "description": "实际到达位置"}
            }
        },
        "MoveC": {
            "category": PrimitiveCategory.MOTION,
            "description": "控制机器人TCP圆弧运动到目标位置，通过中间点定义圆弧路径",
            "params": {
                "target": {"type": "COORD", "unit": "m-deg", "required": True, "description": "目标位置和姿态"},
                "via": {"type": "COORD", "unit": "m-deg", "required": True, "description": "圆弧中间点位置和姿态"},
                "vel": {"type": "float", "unit": "m/s", "default": 0.25, "range": [0.001, 2.2], "description": "TCP线速度"},
                "acc": {"type": "float", "unit": "m/s^2", "default": 1.5, "range": [0.1, 3.0], "description": "TCP线加速度"},
                "angVel": {"type": "float", "unit": "deg/s", "default": 150.0, "range": [10.0, 500.0], "description": "TCP角速度"},
                "jerk": {"type": "float", "unit": "m/s^3", "default": 50.0, "range": [50.0, 500.0], "description": "TCP加加速度"},
                "targetTolerLevel": {"type": "int", "default": 3, "range": [0, 10], "description": "目标容差等级"}
            },
            "required": ["target", "via"],
            "output_params": {
                "reachedTarget": {"type": "bool", "description": "是否到达目标位置"},
                "actualPose": {"type": "COORD", "description": "实际到达位置"},
                "arcLength": {"type": "float", "unit": "m", "description": "实际圆弧长度"}
            },
            "constraints": {
                "collinear_check": "起始点、中间点和目标点不能共线",
                "reachability": "所有点必须在机器人工作空间内"
            }
        },
        
        # 基础力控制
        "ZeroFTSensor": {
            "category": PrimitiveCategory.BASIC_FORCE,
            "description": "力/力矩传感器归零",
            "params": {},
            "required": []
        },
        "Contact": {
            "category": PrimitiveCategory.BASIC_FORCE,
            "description": "接触控制",
            "params": {
                "direction": {"type": "VEC_3d", "unit": "none", "default": [0, 0, -1]},
                "force": {"type": "float", "unit": "N", "default": 10.0, "range": [0.1, 100.0]},
                "vel": {"type": "float", "unit": "m/s", "default": 0.05, "range": [0.001, 0.5]},
                "maxDistance": {"type": "float", "unit": "m", "default": 0.1, "range": [0.001, 1.0]}
            },
            "required": ["direction"]
        },
        "MoveTraj": {
            "category": PrimitiveCategory.BASIC_FORCE,
            "description": "轨迹运动",
            "params": {
                "trajectory": {"type": "ARRAY_COORD", "unit": "m-deg", "required": True},
                "vel": {"type": "float", "unit": "m/s", "default": 0.25, "range": [0.001, 2.2]}
            },
            "required": ["trajectory"]
        },
        "MoveComp": {
            "category": PrimitiveCategory.BASIC_FORCE,
            "description": "柔顺运动",
            "params": {
                "target": {"type": "COORD", "unit": "m-deg", "required": True},
                "stiffness": {"type": "VEC_6d", "unit": "N/m", "default": [1000, 1000, 1000, 100, 100, 100]},
                "damping": {"type": "VEC_6d", "unit": "Ns/m", "default": [50, 50, 50, 5, 5, 5]}
            },
            "required": ["target"]
        },
        
        # 高级力控制
        "ContactAlign": {
            "category": PrimitiveCategory.ADVANCED_FORCE,
            "description": "接触对齐",
            "params": {
                "direction": {"type": "VEC_3d", "unit": "none", "required": True},
                "force": {"type": "float", "unit": "N", "default": 10.0, "range": [0.1, 100.0]},
                "alignTolerance": {"type": "float", "unit": "deg", "default": 5.0, "range": [0.1, 45.0]}
            },
            "required": ["direction"]
        },
        "ForceHybrid": {
            "category": PrimitiveCategory.ADVANCED_FORCE,
            "description": "混合力控制",
            "params": {
                "forceAxes": {"type": "VEC_6d", "unit": "bool", "default": [0, 0, 1, 0, 0, 0]},
                "targetForce": {"type": "VEC_6d", "unit": "N/Nm", "default": [0, 0, 10, 0, 0, 0]},
                "targetPose": {"type": "COORD", "unit": "m-deg", "required": True}
            },
            "required": ["targetPose"]
        },
        "ForceComp": {
            "category": PrimitiveCategory.ADVANCED_FORCE,
            "description": "力补偿",
            "params": {
                "compensation": {"type": "VEC_6d", "unit": "N/Nm", "default": [0, 0, 0, 0, 0, 0]},
                "duration": {"type": "float", "unit": "s", "default": 1.0, "range": [0.1, 60.0]}
            },
            "required": []
        },
        
        # 零重力浮动
        "FloatingCartesian": {
            "category": PrimitiveCategory.ZERO_GRAVITY,
            "description": "笛卡尔空间零重力浮动",
            "params": {
                "axes": {"type": "VEC_6d", "unit": "bool", "default": [1, 1, 1, 1, 1, 1]},
                "duration": {"type": "float", "unit": "s", "default": 10.0, "range": [0.1, 3600.0]}
            },
            "required": []
        },
        "FloatingJoint": {
            "category": PrimitiveCategory.ZERO_GRAVITY,
            "description": "关节空间零重力浮动",
            "params": {
                "joints": {"type": "VEC_7d", "unit": "bool", "default": [1, 1, 1, 1, 1, 1, 1]},
                "duration": {"type": "float", "unit": "s", "default": 10.0, "range": [0.1, 3600.0]}
            },
            "required": []
        },
        
        # 同步控制
        "SyncStart": {
            "category": PrimitiveCategory.SYNCHRONIZATION,
            "description": "同步开始",
            "params": {
                "syncId": {"type": "string", "required": True}
            },
            "required": ["syncId"]
        },
        "SyncEnd": {
            "category": PrimitiveCategory.SYNCHRONIZATION,
            "description": "同步结束",
            "params": {
                "syncId": {"type": "string", "required": True}
            },
            "required": ["syncId"]
        },
        "SyncHold": {
            "category": PrimitiveCategory.SYNCHRONIZATION,
            "description": "同步保持",
            "params": {
                "syncId": {"type": "string", "required": True},
                "timeout": {"type": "float", "unit": "s", "default": 30.0, "range": [1.0, 3600.0]}
            },
            "required": ["syncId"]
        }
    }
    
    @classmethod
    def get_primitive_list(cls) -> List[str]:
        """获取所有可用的Primitive列表"""
        return list(cls.PRIMITIVE_SCHEMAS.keys())
    
    @classmethod
    def get_primitives_by_category(cls, category: PrimitiveCategory) -> List[str]:
        """根据分类获取Primitive列表"""
        return [name for name, schema in cls.PRIMITIVE_SCHEMAS.items() 
                if schema["category"] == category]
    
    @classmethod
    def get_primitive_schema(cls, primitive_name: str) -> Dict[str, Any]:
        """获取指定Primitive的参数模式"""
        return cls.PRIMITIVE_SCHEMAS.get(primitive_name, {})
    
    @classmethod
    def validate_params(cls, primitive_name: str, params: Dict[str, Any]) -> tuple[bool, str]:
        """验证Primitive参数"""
        schema = cls.get_primitive_schema(primitive_name)
        if not schema:
            return False, f"未知的Primitive: {primitive_name}"
        
        # 检查必需参数
        required_params = schema.get("required", [])
        for req_param in required_params:
            if req_param not in params:
                return False, f"缺少必需参数: {req_param}"
        
        # 验证参数类型和范围
        param_schemas = schema.get("params", {})
        for param_name, param_value in params.items():
            if param_name not in param_schemas:
                continue  # 允许额外参数
            
            param_schema = param_schemas[param_name]
            param_type = param_schema.get("type")
            
            # 类型验证
            if param_type == "float" and not isinstance(param_value, (int, float)):
                return False, f"参数 {param_name} 应为数值类型"
            elif param_type == "int" and not isinstance(param_value, int):
                return False, f"参数 {param_name} 应为整数类型"
            elif param_type == "string" and not isinstance(param_value, str):
                return False, f"参数 {param_name} 应为字符串类型"
            elif param_type == "COORD":
                if not cls._validate_coord_param(param_value):
                    return False, f"参数 {param_name} 坐标格式错误"
            elif param_type == "JPOS":
                if not cls._validate_jpos_param(param_value):
                    return False, f"参数 {param_name} 关节位置格式错误"
            elif param_type == "ARRAY_COORD":
                if not isinstance(param_value, list) or not all(cls._validate_coord_param(coord) for coord in param_value):
                    return False, f"参数 {param_name} 坐标数组格式错误"
            elif param_type == "ARRAY_JPOS":
                if not isinstance(param_value, list) or not all(cls._validate_jpos_param(jpos) for jpos in param_value):
                    return False, f"参数 {param_name} 关节位置数组格式错误"
            elif param_type == "VEC_3d":
                if not isinstance(param_value, list) or len(param_value) != 3:
                    return False, f"参数 {param_name} 应为3维向量"
            elif param_type == "VEC_6d":
                if not isinstance(param_value, list) or len(param_value) != 6:
                    return False, f"参数 {param_name} 应为6维向量"
            elif param_type == "VEC_7d":
                if not isinstance(param_value, list) or len(param_value) != 7:
                    return False, f"参数 {param_name} 应为7维向量"
            elif param_type == "enum":
                if "options" in param_schema and param_value not in param_schema["options"]:
                    return False, f"参数 {param_name} 值 '{param_value}' 不在允许选项中: {param_schema['options']}"
            
            # 范围验证
            if "range" in param_schema and isinstance(param_value, (int, float)):
                min_val, max_val = param_schema["range"]
                if not (min_val <= param_value <= max_val):
                    return False, f"参数 {param_name} 超出范围 [{min_val}, {max_val}]"
        
        # 运动控制Primitive的特殊验证
        if primitive_name in ["MoveL", "MoveJ", "MovePTP", "MoveC"]:
            return cls._validate_motion_primitive(primitive_name, params)
        
        return True, "参数验证通过"
    
    @classmethod
    def _validate_coord_param(cls, coord_param: Any) -> bool:
        """验证坐标参数格式"""
        if not isinstance(coord_param, dict):
            return False
        
        required_keys = ["pos", "rot"]
        for key in required_keys:
            if key not in coord_param:
                return False
        
        # 验证位置和旋转向量长度
        if not isinstance(coord_param["pos"], list) or len(coord_param["pos"]) != 3:
            return False
        if not isinstance(coord_param["rot"], list) or len(coord_param["rot"]) != 3:
            return False
        
        return True
    
    @classmethod
    def _validate_jpos_param(cls, jpos_param: Any) -> bool:
        """验证关节位置参数格式"""
        if not isinstance(jpos_param, dict):
            return False
        
        if "joints" not in jpos_param:
            return False
        
        # 验证关节数量（Rizon4s为7轴）
        if not isinstance(jpos_param["joints"], list) or len(jpos_param["joints"]) != 7:
            return False
        
        return True
    
    @classmethod
    def _validate_motion_primitive(cls, primitive_name: str, params: Dict[str, Any]) -> tuple[bool, str]:
        """验证运动控制Primitive的特殊约束"""
        if primitive_name == "MoveC":
            # MoveC需要验证三点不共线
            if "target" in params and "via" in params:
                # 这里可以添加共线性检查逻辑
                # 暂时返回通过，实际应用中可以添加几何计算
                pass
        
        return True, "运动控制参数验证通过"

class PrimitiveManager(QObject):
    """Primitive管理器"""
    
    # 信号定义
    primitive_started = pyqtSignal(str)  # primitive_name
    primitive_completed = pyqtSignal(str, dict)  # primitive_name, result
    primitive_failed = pyqtSignal(str, str)  # primitive_name, error_msg
    primitive_progress = pyqtSignal(str, dict)  # primitive_name, state
    status_updated = pyqtSignal(str)
    
    def __init__(self, robot: Optional[Robot] = None, hardware: bool = True, parent=None):
        super().__init__(parent)
        self.robot = robot
        self.hardware = hardware and FLEXIV_AVAILABLE
        self.current_primitive = None
        self.primitive_thread = None
        self.stop_requested = False
        self.execution_lock = threading.RLock()
        
    def execute_primitive(self, primitive_name: str, params: Dict[str, Any] = None) -> bool:
        """执行指定的Primitive"""
        if params is None:
            params = {}
        
        # 参数验证
        is_valid, error_msg = PrimitiveParams.validate_params(primitive_name, params)
        if not is_valid:
            self.primitive_failed.emit(primitive_name, error_msg)
            return False
        
        # 检查是否有正在执行的Primitive
        with self.execution_lock:
            if self.current_primitive is not None:
                self.primitive_failed.emit(primitive_name, "已有Primitive正在执行")
                return False
            
            self.current_primitive = primitive_name
            self.stop_requested = False
        
        # 在后台线程中执行
        self.primitive_thread = threading.Thread(
            target=self._execute_primitive_thread,
            args=(primitive_name, params),
            daemon=True
        )
        self.primitive_thread.start()
        
        return True
    
    def _execute_primitive_thread(self, primitive_name: str, params: Dict[str, Any]):
        """在后台线程中执行Primitive"""
        try:
            self.primitive_started.emit(primitive_name)
            self.status_updated.emit(f"开始执行Primitive: {primitive_name}")
            
            if self.hardware and self.robot is not None:
                self._execute_hardware_primitive(primitive_name, params)
            else:
                self._execute_simulation_primitive(primitive_name, params)
            
            if not self.stop_requested:
                self.primitive_completed.emit(primitive_name, {})
                self.status_updated.emit(f"Primitive执行完成: {primitive_name}")
            
        except Exception as e:
            self.primitive_failed.emit(primitive_name, str(e))
            self.status_updated.emit(f"Primitive执行失败: {primitive_name} - {str(e)}")
        
        finally:
            with self.execution_lock:
                self.current_primitive = None
                self.primitive_thread = None
    
    def _execute_hardware_primitive(self, primitive_name: str, params: Dict[str, Any]):
        """在硬件模式下执行Primitive"""
        if not self.robot.connected():
            raise Exception("机器人未连接")
        
        if not self.robot.operational():
            raise Exception("机器人未使能")
        
        # 切换到NRT_PRIMITIVE_EXECUTION模式
        current_mode = self.robot.mode()
        if current_mode != Mode.NRT_PRIMITIVE_EXECUTION:
            self.robot.SwitchMode(Mode.NRT_PRIMITIVE_EXECUTION)
            time.sleep(0.1)
        
        try:
            # 转换参数格式
            converted_params = self._convert_params_for_rdk(params)
            
            # 执行Primitive
            self.robot.ExecutePrimitive(primitive_name, converted_params)
            
            # 根据Primitive类型设置不同的监控策略
            self._monitor_primitive_execution(primitive_name, params)
            
        finally:
            # 恢复原模式
            if current_mode != Mode.NRT_PRIMITIVE_EXECUTION:
                try:
                    self.robot.SwitchMode(current_mode)
                except Exception as e:
                    # 模式切换失败时记录错误但不抛出异常
                    print(f"警告: 恢复控制模式失败 - {str(e)}")
    
    def _execute_simulation_primitive(self, primitive_name: str, params: Dict[str, Any]):
        """在仿真模式下执行Primitive"""
        # 仿真执行时间（根据Primitive类型调整）
        schema = PrimitiveParams.get_primitive_schema(primitive_name)
        category = schema.get("category", PrimitiveCategory.WORKFLOW)
        
        if category == PrimitiveCategory.MOTION:
            simulation_time = 3.0  # 运动类Primitive模拟3秒
        elif category == PrimitiveCategory.BASIC_FORCE:
            simulation_time = 2.0  # 力控制类Primitive模拟2秒
        else:
            simulation_time = 1.0  # 其他类型模拟1秒
        
        # 模拟执行过程
        steps = 10
        for i in range(steps):
            if self.stop_requested:
                break
            
            time.sleep(simulation_time / steps)
            
            # 发送进度更新
            progress = (i + 1) / steps
            state = {
                "progress": progress,
                "reachedTarget": progress >= 1.0,
                "timePeriod": (i + 1) * simulation_time / steps
            }
            self.primitive_progress.emit(primitive_name, state)
        
        # 确保仿真完成后有短暂延迟，让信号处理完成
        time.sleep(0.1)
    
    def _monitor_primitive_execution(self, primitive_name: str, params: Dict[str, Any] = None):
        """监控Primitive执行状态"""
        # 根据Primitive类型设置不同的超时时间
        timeout = self._get_primitive_timeout(primitive_name, params)
        start_time = time.time()
        
        while not self.stop_requested and (time.time() - start_time) < timeout:
            if not self.robot.busy():
                break
            
            # 获取机器人状态信息
            try:
                states = self.robot.states()
                # 构造状态字典用于进度更新
                progress_info = {
                    "tcp_pose": states.tcp_pose,
                    "joint_pos": states.q,
                    "tcp_force": states.ext_wrench_in_tcp,
                    "execution_time": time.time() - start_time,
                    "timeout": timeout
                }
                self.primitive_progress.emit(primitive_name, progress_info)
            except Exception as e:
                # 如果获取状态失败，仍然继续监控
                pass
            
            time.sleep(0.1)
        
        if self.robot.busy() and not self.stop_requested:
            raise Exception(f"Primitive执行超时: {primitive_name} (超时时间: {timeout}秒)")
    
    def _get_primitive_timeout(self, primitive_name: str, params: Dict[str, Any] = None) -> float:
        """根据Primitive类型和参数计算合适的超时时间"""
        schema = PrimitiveParams.get_primitive_schema(primitive_name)
        category = schema.get("category", PrimitiveCategory.WORKFLOW)
        
        # 基础超时时间
        base_timeout = {
            PrimitiveCategory.WORKFLOW: 10.0,
            PrimitiveCategory.MOTION: 30.0,
            PrimitiveCategory.BASIC_FORCE: 60.0,
            PrimitiveCategory.ADVANCED_FORCE: 120.0,
            PrimitiveCategory.ZERO_GRAVITY: 3600.0,  # 零重力模式可能需要很长时间
            PrimitiveCategory.SYNCHRONIZATION: 30.0
        }.get(category, 30.0)
        
        # 对于运动控制Primitive，根据速度参数调整超时时间
        if category == PrimitiveCategory.MOTION and params:
            vel = params.get("vel", 0.25)  # 默认速度
            if vel > 0:
                # 估算运动时间并添加安全余量
                estimated_distance = 1.0  # 假设最大运动距离1米
                estimated_time = estimated_distance / vel
                calculated_timeout = estimated_time * 5  # 5倍安全余量
                # 确保慢速运动有更长的超时时间
                base_timeout = calculated_timeout + 10.0  # 添加固定的基础时间
        
        return min(base_timeout, 300.0)  # 最大不超过5分钟
    
    def _convert_params_for_rdk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """将参数转换为RDK格式"""
        converted = {}
        
        for key, value in params.items():
            if isinstance(value, dict) and "pos" in value and "rot" in value:
                # 转换为Coord对象
                converted[key] = Coord(value["pos"], value["rot"], value.get("ref", ["WORLD", "WORLD_ORIGIN"]))
            elif isinstance(value, dict) and "joints" in value:
                # 转换为JPos对象
                converted[key] = JPos(value["joints"], value.get("external", []))
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                # 转换坐标数组
                if "pos" in value[0]:
                    converted[key] = [Coord(item["pos"], item["rot"], item.get("ref", ["WORLD", "WORLD_ORIGIN"])) for item in value]
                elif "joints" in value[0]:
                    converted[key] = [JPos(item["joints"], item.get("external", [])) for item in value]
                else:
                    converted[key] = value
            else:
                converted[key] = value
        
        return converted
    
    def stop_current_primitive(self) -> bool:
        """停止当前执行的Primitive"""
        with self.execution_lock:
            if self.current_primitive is None:
                return False
            
            self.stop_requested = True
            
            if self.hardware and self.robot is not None:
                try:
                    self.robot.Stop()
                except:
                    pass
            
            self.status_updated.emit(f"已请求停止Primitive: {self.current_primitive}")
            return True
    
    def get_current_primitive(self) -> Optional[str]:
        """获取当前执行的Primitive名称"""
        return self.current_primitive
    
    def is_executing(self) -> bool:
        """检查是否有Primitive正在执行"""
        return self.current_primitive is not None
    
    def get_available_primitives(self) -> Dict[PrimitiveCategory, List[str]]:
        """获取按分类组织的可用Primitive列表"""
        result = {}
        for category in PrimitiveCategory:
            primitives = PrimitiveParams.get_primitives_by_category(category)
            if primitives:
                result[category] = primitives
        return result
    
    def create_coord(self, x: float, y: float, z: float, rx: float, ry: float, rz: float, 
                    ref_coord: str = "WORLD", ref_origin: str = "WORLD_ORIGIN") -> Dict[str, Any]:
        """创建坐标参数"""
        return {
            "pos": [x, y, z],
            "rot": [rx, ry, rz],
            "ref": [ref_coord, ref_origin]
        }
    
    def create_jpos(self, joints: List[float], external: List[float] = None) -> Dict[str, Any]:
        """创建关节位置参数"""
        return {
            "joints": joints,
            "external": external or []
        }