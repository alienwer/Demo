'''
Author: LK
Date: 2025-02-07 22:08:05
LastEditTime: 2025-08-10 08:55:27
LastEditors: LK
FilePath: /Demo/app/control/robot_control.py
'''
import numpy as np
import threading
import logging
from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal
import os

try:
    from flexivrdk import Robot, Model, Mode, Tool
    FLEXIV_AVAILABLE = True
except ImportError:
    FLEXIV_AVAILABLE = False

class RobotControl(QObject, threading.Thread):
    status_updated = pyqtSignal(str)
    joint_updated = pyqtSignal(list)
    end_effector_updated = pyqtSignal(list)
    
    # 新增：完整的机器人状态信号
    robot_states_updated = pyqtSignal(object)  # 传递完整的RobotStates对象
    joint_velocity_updated = pyqtSignal(list)  # 关节速度
    joint_torque_updated = pyqtSignal(list)    # 关节力矩
    ft_sensor_updated = pyqtSignal(list)       # 力/力矩传感器数据
    mode_updated = pyqtSignal(str)             # 机器人模式

    # ========== Flexiv RDK 常用API集成 ==========
    plan_executed = pyqtSignal(str)
    plan_stopped = pyqtSignal(str)  # 新增：plan停止信号
    force_sensor_zeroed = pyqtSignal()
    auto_recovered = pyqtSignal()
    tool_updated = pyqtSignal(str)
    global_vars_updated = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    plan_list_updated = pyqtSignal(list)
    plan_info_updated = pyqtSignal(object)

    def __init__(self, robot=None, robot_id: str = "Rizon4-062468", robot_model=None, hardware: bool = True, initial_joint_angles: Optional[List[float]] = None):
        QObject.__init__(self)
        threading.Thread.__init__(self)
        self.robot = robot
        self.robot_id = robot_id
        self.robot_model = robot_model
        self.hardware = hardware and FLEXIV_AVAILABLE
        self.running = False
        self.daemon = True
        # 初始化Model和Tool实例（仅在硬件模式下）
        self.model = None
        self.tool = None
        # 仿真/教学模式变量
        # 如果提供了初始关节角度且在仿真模式下，使用提供的角度；否则使用默认的零位
        if initial_joint_angles is not None and len(initial_joint_angles) == 7 and not self.hardware:
            self.joint_angles = initial_joint_angles.copy()
        else:
            self.joint_angles = [0.0] * 7
        
        # Plan执行控制变量
        self.current_plan_name = None  # 当前执行的plan名称
        self.plan_execution_thread = None  # plan执行监控线程
        self.stop_plan_requested = False  # 停止plan请求标志
        
        # 速度设置（默认值，范围0.1-1.0）
        self.execution_speed = 1.0  # 执行速度倍率
        # 关节限制使用弧度制（根据Flexiv RDK文档要求）
        # 原度数限制: [(-180, 180), (-90, 90), (-170, 170), (-180, 180), (-120, 120), (-360, 360), (-180, 180)]
        import math
        self.joint_limits = [
            (-math.pi, math.pi),           # Joint 1: ±180° -> ±π rad
            (-math.pi/2, math.pi/2),       # Joint 2: ±90° -> ±π/2 rad
            (-170*math.pi/180, 170*math.pi/180),  # Joint 3: ±170° -> ±170π/180 rad
            (-math.pi, math.pi),           # Joint 4: ±180° -> ±π rad
            (-120*math.pi/180, 120*math.pi/180),  # Joint 5: ±120° -> ±120π/180 rad
            (-2*math.pi, 2*math.pi),       # Joint 6: ±360° -> ±2π rad
            (-math.pi, math.pi)            # Joint 7: ±180° -> ±π rad
        ]
        self.teaching_points: List[List[float]] = []
        self.sim_end_effector = [0.0, 0.0, 0.0]

    def set_joint_angle(self, joint_id: int, angle: float) -> bool:
        if not (0 <= joint_id < 7):
            return False
        min_angle, max_angle = self.joint_limits[joint_id]
        if not (min_angle <= angle <= max_angle):
            return False
        self.joint_angles[joint_id] = angle
        self.joint_updated.emit(self.joint_angles.copy())
        return True

    def get_joint_angles(self) -> List[float]:
        return self.joint_angles.copy()

    def set_joint_angles(self, angles: List[float]) -> bool:
        if len(angles) != 7:
            return False
        for i, angle in enumerate(angles):
            min_angle, max_angle = self.joint_limits[i]
            if not (min_angle <= angle <= max_angle):
                return False
        self.joint_angles = angles.copy()
        self.joint_updated.emit(self.joint_angles.copy())
        return True

    def add_teaching_point(self) -> None:
        self.teaching_points.append(self.joint_angles.copy())

    def clear_teaching_points(self) -> None:
        self.teaching_points.clear()

    def get_teaching_points(self) -> List[List[float]]:
        return self.teaching_points.copy()

    def interpolate_trajectory(self, start_point: List[float], end_point: List[float], steps: int) -> List[List[float]]:
        trajectory = []
        for i in range(steps):
            t = i / (steps - 1)
            point = [start + t * (end - start) for start, end in zip(start_point, end_point)]
            trajectory.append(point)
        return trajectory

    def generate_teaching_trajectory(self, steps_between_points: int = 50) -> List[List[float]]:
        if len(self.teaching_points) < 2:
            return []
        trajectory = []
        for i in range(len(self.teaching_points) - 1):
            segment = self.interpolate_trajectory(
                self.teaching_points[i],
                self.teaching_points[i + 1],
                steps_between_points
            )
            trajectory.extend(segment)
        return trajectory

    def update_robot_model(self, joint_angles):
        if not self.robot_model:
            return
        # 递归更新各连杆的MDH参数（略，按原modern实现）
        pass

    def run(self):
        if self.hardware:
            try:
                if self.robot is None:
                    from flexivrdk import Robot
                    self.robot = Robot(self.robot_id)
                # 初始化Model和Tool实例
                if self.model is None and FLEXIV_AVAILABLE:
                    self.model = Model(self.robot)
                    self.status_updated.emit("Model实例已初始化")
                if self.tool is None and FLEXIV_AVAILABLE:
                    self.tool = Tool(self.robot)
                    self.status_updated.emit("Tool实例已初始化")
                self.running = True
                self.robot.Enable()
                self.status_updated.emit("已使能")
                while self.running:
                    # 获取机器人状态数据
                    robot_states = self.robot.states()
                    
                    # 发送完整的状态对象
                    self.robot_states_updated.emit(robot_states)
                    
                    # 关节角度 (弧度制)
                    joint_angles = list(robot_states.q)
                    self.joint_angles = joint_angles
                    self.joint_updated.emit(joint_angles)
                    
                    # 关节速度 (弧度/秒)
                    joint_velocities = list(robot_states.dq)
                    self.joint_velocity_updated.emit(joint_velocities)
                    
                    # 关节力矩 (Nm)
                    joint_torques = list(robot_states.tau)
                    self.joint_torque_updated.emit(joint_torques)
                    
                    # 末端执行器位置 (TCP位置)
                    tcp_pose = list(robot_states.tcp_pose)
                    end_effector_pos = tcp_pose[0:3]  # 取位置部分 [x, y, z]
                    self.end_effector_updated.emit(end_effector_pos)
                    
                    # 力/力矩传感器数据 (TCP坐标系下的外部力)
                    if hasattr(robot_states, 'ext_wrench_in_tcp'):
                        ft_data = list(robot_states.ext_wrench_in_tcp)
                        self.ft_sensor_updated.emit(ft_data)
                    
                    # 机器人模式
                    current_mode = self.robot.mode()
                    self.mode_updated.emit(str(current_mode))
                    
                    # 更新机器人模型
                    self.update_robot_model(joint_angles)
                    
                    # 检查机器人状态
                    if self.robot.fault():
                        self.status_updated.emit("机器人故障状态")
                        # 注意：不要自动清除故障，应该由用户手动处理
                        # self.robot.ClearFault()
                    elif self.robot.operational():
                        self.status_updated.emit("机器人运行正常")
                    elif self.robot.connected():
                        self.status_updated.emit("机器人已连接但未使能")
                    else:
                        self.status_updated.emit("机器人连接断开")
                        break
                    
                    # 控制循环频率 (约50Hz，避免过于频繁)
                    threading.Event().wait(0.02)
                    
            except Exception as e:
                logging.error(f"机器人控制错误: {e}")
                self.status_updated.emit(f"错误: {str(e)}")
            finally:
                self.stop_robot()
        else:
            # 仿真/教学模式主循环
            self.running = True
            self.status_updated.emit("仿真/教学模式运行中")
            while self.running:
                # 可扩展：自动演示、轨迹回放等
                self.joint_updated.emit(self.joint_angles.copy())
                self.end_effector_updated.emit(self.sim_end_effector.copy())
                threading.Event().wait(0.05)  # 20Hz
            self.status_updated.emit("仿真/教学模式已停止")

    def stop_robot(self):
        self.running = False
        if self.hardware and self.robot and self.robot.connected():
            self.robot.Brake()
        self.status_updated.emit("已停止")

    def enable_robot(self):
        if self.hardware and self.robot is not None:
            try:
                if self.robot.fault():
                    self.robot.ClearFault()
                    self.status_updated.emit("故障已清除，尝试使能...")
                self.robot.Enable()
                import time
                for _ in range(10):  # 等待最多5秒
                    if self.robot.operational():
                        break
                    time.sleep(0.5)
                if self.robot.operational():
                    self.status_updated.emit("机器人已使能")
                else:
                    self.status_updated.emit("机器人未能成功使能")
            except Exception as e:
                self.status_updated.emit(f"使能失败: {str(e)}")
        else:
            self.status_updated.emit("机器人对象未初始化")

    def disable_robot(self):
        self.stop_robot()

    def get_plan_list(self):
        if self.hardware and self.robot is not None:
            try:
                # Mode已在顶部导入
                connected = self.robot.connected()
                operational = self.robot.operational()
                mode = self.robot.mode()
                self.status_updated.emit(f"连接: {connected}, 使能: {operational}, 模式: {mode}")
                if not connected:
                    self.error_signal.emit("机器人未连接，无法刷新Plan列表")
                    return []
                if not operational:
                    self.error_signal.emit("机器人未使能，无法刷新Plan列表")
                    return []
                
                # 保存当前模式
                current_mode = self.robot.mode()
                
                # 只有在非IDLE模式时才切换到IDLE模式
                if current_mode != Mode.IDLE:
                    self.robot.SwitchMode(Mode.IDLE)
                    self.status_updated.emit(f"切换到IDLE模式: {self.robot.mode()}")
                
                # 使用正确的API获取Plan列表
                plan_list = self.robot.plan_list()
                self.status_updated.emit(f"获取到Plan列表: {plan_list}")
                self.plan_list_updated.emit(plan_list)
                
                # 如果之前不是IDLE模式，恢复原来的模式
                if current_mode != Mode.IDLE:
                    self.robot.SwitchMode(current_mode)
                    self.status_updated.emit(f"恢复到原模式: {self.robot.mode()}")
                
                return plan_list
            except Exception as e:
                self.error_signal.emit(f"获取Plan列表失败: {str(e)}")
                return []
        else:
            self.error_signal.emit("请先连接并使能机器人，再刷新Plan列表")
        return []

    def get_plan_info(self):
        if self.hardware and self.robot is not None:
            try:
                # 使用正确的API获取Plan信息
                info = self.robot.plan_info()
                self.plan_info_updated.emit(info)
                return info
            except Exception as e:
                self.error_signal.emit(f"获取Plan信息失败: {str(e)}")
                return None
        return None

    def execute_plan(self, plan, allow_disconnect=True):
        if self.hardware and self.robot is not None:
            try:
                # 检查机器人状态
                if not self.robot.connected():
                    self.error_signal.emit("机器人未连接，无法执行Plan")
                    return
                if not self.robot.operational():
                    self.error_signal.emit("机器人未使能或不在运行状态，无法执行Plan")
                    return
                if self.robot.fault():
                    self.error_signal.emit("机器人处于故障状态，请先清除故障")
                    return
                
                # Mode已在顶部导入
                self.robot.SwitchMode(Mode.NRT_PLAN_EXECUTION)
                self.status_updated.emit("已切换到NRT_PLAN_EXECUTION模式")
                self.update_mode_signal()
                
                # 验证模式切换是否成功
                import time
                time.sleep(0.1)  # 等待模式切换完成
                current_mode = self.robot.mode()
                if current_mode != Mode.NRT_PLAN_EXECUTION:
                    self.error_signal.emit(f"模式切换失败，当前模式: {current_mode}")
                    return
                
                # 重置停止请求标志并记录当前plan
                self.stop_plan_requested = False
                self.current_plan_name = str(plan)
                
                # 设置执行速度（转换为百分比，范围1-100）
                velocity_scale = int(self.execution_speed * 100)
                self.robot.SetVelocityScale(velocity_scale)
                self.status_updated.emit(f"设置执行速度为: {velocity_scale}%")
                
                # 根据plan参数类型选择正确的ExecutePlan重载版本
                if isinstance(plan, int):
                    # 按索引执行plan
                    self.robot.ExecutePlan(plan, allow_disconnect, True)
                    self.status_updated.emit(f"执行Plan索引: {plan} (速度: {self.execution_speed:.1f}x)")
                else:
                    # 按名称执行plan
                    self.robot.ExecutePlan(str(plan), allow_disconnect, True)
                    self.status_updated.emit(f"执行Plan: {plan} (速度: {self.execution_speed:.1f}x)")
                
                # 检查plan是否开始执行
                import time
                time.sleep(0.2)  # 等待plan开始
                if self.robot.busy():
                    self.status_updated.emit(f"Plan {plan} 已开始执行")
                else:
                    self.status_updated.emit(f"警告: Plan {plan} 可能未开始执行")
                
                # 启动后台线程监控plan执行状态，避免阻塞UI
                def monitor_plan_execution():
                    try:
                        execution_start_time = time.time()
                        max_wait_time = 300  # 最大等待5分钟
                        
                        while self.robot.busy():
                            # 检查是否收到停止请求
                            if self.stop_plan_requested:
                                self.status_updated.emit(f"Plan {plan} 收到停止请求")
                                break
                            
                            # 检查是否超时
                            if time.time() - execution_start_time > max_wait_time:
                                self.error_signal.emit(f"Plan {plan} 执行超时（{max_wait_time}秒）")
                                break
                            
                            # 获取plan信息并更新状态
                            info = self.get_plan_info()
                            if info:
                                node_name = getattr(info, 'node_name', 'Unknown')
                                self.status_updated.emit(f"Plan {plan} 执行中 - 当前节点: {node_name}")
                            
                            threading.Event().wait(0.5)
                        
                        # 检查plan是否正常完成还是被停止
                        if not self.robot.busy():
                            if self.stop_plan_requested:
                                self.plan_stopped.emit(str(plan))
                                self.status_updated.emit(f"Plan {plan} 已被停止")
                            else:
                                self.plan_executed.emit(str(plan))
                                self.status_updated.emit(f"Plan {plan} 执行完成")
                            self.current_plan_name = None
                        
                    except Exception as e:
                        self.error_signal.emit(f"Plan监控失败: {str(e)}")
                
                # 在后台线程中监控执行状态
                monitor_thread = threading.Thread(target=monitor_plan_execution, daemon=True)
                monitor_thread.start()
                
            except Exception as e:
                self.error_signal.emit(f"Plan执行失败: {str(e)}")
    
    def stop_plan(self):
        """停止当前执行的plan"""
        if self.hardware and self.robot is not None:
            try:
                # 设置停止请求标志
                self.stop_plan_requested = True
                
                # 检查是否有plan正在执行
                if self.robot.busy():
                    # 停止当前执行的plan
                    self.robot.Stop()
                    self.status_updated.emit("正在停止Plan执行...")
                    
                    # 等待plan停止
                    import time
                    timeout = 5.0  # 5秒超时
                    start_time = time.time()
                    
                    while self.robot.busy() and (time.time() - start_time) < timeout:
                        time.sleep(0.1)
                    
                    if not self.robot.busy():
                        plan_name = self.current_plan_name or "Unknown"
                        self.plan_stopped.emit(plan_name)
                        self.status_updated.emit(f"Plan {plan_name} 已停止")
                        self.current_plan_name = None
                    else:
                        self.error_signal.emit("Plan停止超时，可能需要手动干预")
                else:
                    self.status_updated.emit("当前没有Plan在执行")
                    
            except Exception as e:
                self.error_signal.emit(f"停止Plan失败: {str(e)}")
        else:
            self.status_updated.emit("仿真模式下无法停止Plan")
    
    def set_execution_speed(self, speed: float):
        """设置plan执行速度倍率
        
        Args:
            speed: 速度倍率，范围0.1-1.0
        """
        if 0.1 <= speed <= 1.0:
            self.execution_speed = speed
            self.status_updated.emit(f"执行速度已设置为: {speed:.1f}x")
        else:
            self.error_signal.emit("速度倍率必须在0.1-1.0范围内")
    
    def get_execution_speed(self) -> float:
        """获取当前执行速度倍率"""
        return self.execution_speed

    def execute_primitive(self, primitive, params=None, properties=None):
        if self.hardware and self.robot is not None:
            try:
                # Mode已在顶部导入
                self.robot.SwitchMode(Mode.NRT_PRIMITIVE_EXECUTION)
                self.status_updated.emit("已切换到NRT_PRIMITIVE_EXECUTION模式")
                self.update_mode_signal()
                if params is None:
                    params = dict()
                if properties is None:
                    properties = dict()
                self.robot.ExecutePrimitive(primitive, params, properties)
                self.status_updated.emit(f"执行Primitive: {primitive}")
            except Exception as e:
                self.error_signal.emit(f"Primitive执行失败: {str(e)}")

    def update_mode_signal(self):
        try:
            if self.robot is not None:
                mode = self.robot.mode()
                self.status_updated.emit(f"当前模式: {mode}")
        except Exception:
            pass

    def zero_force_torque_sensor(self):
        """力/力矩传感器归零"""
        if self.hardware and self.robot is not None:
            try:
                # 检查当前模式，如果不是NRT_PRIMITIVE_EXECUTION则切换
                current_mode = self.robot.mode()
                if current_mode != Mode.NRT_PRIMITIVE_EXECUTION:
                    self.robot.SwitchMode(Mode.NRT_PRIMITIVE_EXECUTION)
                    self.status_updated.emit("已切换到NRT_PRIMITIVE_EXECUTION模式")
                    # 等待模式切换完成
                    import time
                    time.sleep(0.5)
                
                # 使用ExecutePrimitive方法执行ZeroFTSensor
                self.robot.ExecutePrimitive("ZeroFTSensor", {})
                self.force_sensor_zeroed.emit()
                self.status_updated.emit("力/力矩传感器归零命令已发送")
                
                # 监控primitive执行状态
                def monitor_zeroing():
                    try:
                        import time
                        # 等待primitive开始执行
                        time.sleep(0.2)
                        
                        # 检查是否还在执行
                        timeout = 10.0  # 10秒超时
                        start_time = time.time()
                        
                        while self.robot.busy() and (time.time() - start_time) < timeout:
                            time.sleep(0.1)
                        
                        if not self.robot.busy():
                            self.status_updated.emit("力/力矩传感器归零完成")
                            # 发送归零后的数据更新信号
                            zero_ft_data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                            self.ft_sensor_updated.emit(zero_ft_data)
                        else:
                            self.error_signal.emit("力/力矩传感器归零超时")
                            
                    except Exception as e:
                        self.error_signal.emit(f"力/力矩传感器归零监控失败: {str(e)}")
                
                # 在后台线程中监控归零状态
                import threading
                monitor_thread = threading.Thread(target=monitor_zeroing, daemon=True)
                monitor_thread.start()
                
            except Exception as e:
                self.error_signal.emit(f"力/力矩传感器归零失败: {str(e)}")
        elif not self.hardware:
            # 仿真模式下的处理
            try:
                # 在仿真模式下，重置力/力矩数据为零
                zero_ft_data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # [Fx, Fy, Fz, Tx, Ty, Tz]
                self.ft_sensor_updated.emit(zero_ft_data)
                self.force_sensor_zeroed.emit()
                self.status_updated.emit("仿真模式：力/力矩传感器已归零")
            except Exception as e:
                self.error_signal.emit(f"仿真模式力/力矩传感器归零失败: {str(e)}")
        else:
            self.error_signal.emit("机器人未连接，无法执行力/力矩传感器归零")

    def auto_recovery(self):
        if self.hardware and self.robot is not None:
            try:
                self.robot.RunAutoRecovery()
                self.auto_recovered.emit()
                self.status_updated.emit("自动恢复完成")
            except Exception as e:
                self.error_signal.emit(f"自动恢复失败: {str(e)}")

    def get_tool_list(self):
        """获取所有可用工具列表"""
        if self.hardware and self.robot is not None:
            try:
                # 确保Tool实例已初始化
                if self.tool is None:
                    self.tool = Tool(self.robot)
                    self.status_updated.emit("Tool实例已初始化")
                
                # 获取工具列表
                tool_list = self.tool.list()
                return tool_list
            except Exception as e:
                self.error_signal.emit(f"获取工具列表失败: {str(e)}")
                return []
        else:
            # 仿真模式返回示例工具列表
            return ["Flange", "Gripper", "Welder", "Camera"]
    
    def get_current_tool(self):
        """获取当前使用的工具名称"""
        if self.hardware and self.robot is not None:
            try:
                # 确保Tool实例已初始化
                if self.tool is None:
                    self.tool = Tool(self.robot)
                    self.status_updated.emit("Tool实例已初始化")
                
                # 获取当前工具名称
                current_tool = self.tool.name()
                return current_tool
            except Exception as e:
                self.error_signal.emit(f"获取当前工具失败: {str(e)}")
                return "Unknown"
        else:
            # 仿真模式返回默认工具
            return "Flange"
    
    def switch_tool(self, tool_name):
        """切换到指定工具"""
        if self.hardware and self.robot is not None:
            try:
                # 确保Tool实例已初始化
                if self.tool is None:
                    self.tool = Tool(self.robot)
                    self.status_updated.emit("Tool实例已初始化")
                
                # 检查工具是否存在
                if not self.tool.exist(tool_name):
                    self.error_signal.emit(f"工具 '{tool_name}' 不存在")
                    return
                
                # 切换工具
                self.tool.Switch(tool_name)
                self.tool_updated.emit(tool_name)
                self.status_updated.emit(f"工具已切换为: {tool_name}")
            except Exception as e:
                self.error_signal.emit(f"工具切换失败: {str(e)}")
        else:
            # 仿真模式
            self.tool_updated.emit(tool_name)
            self.status_updated.emit(f"仿真模式：工具已切换为: {tool_name}")

    def update_tool(self, tool_name, tool_params=None):
        """更新工具参数（保留原有方法以兼容性）"""
        if self.hardware and self.robot is not None:
            try:
                # 确保Tool实例已初始化
                if self.tool is None:
                    self.tool = Tool(self.robot)
                    self.status_updated.emit("Tool实例已初始化")
                
                # 如果没有提供工具参数，使用默认参数
                if tool_params is None:
                    from flexivrdk import ToolParams
                    tool_params = ToolParams()
                
                # 使用Tool类的Update方法
                self.tool.Update(tool_name, tool_params)
                self.tool_updated.emit(tool_name)
                self.status_updated.emit(f"工具已更新为: {tool_name}")
            except Exception as e:
                self.error_signal.emit(f"工具更新失败: {str(e)}")

    def get_global_variables(self):
        """获取机器人全局变量"""
        if self.hardware and self.robot is not None:
            try:
                vars = self.robot.global_variables()
                self.global_vars_updated.emit(vars)
                self.status_updated.emit("已获取机器人全局变量")
            except Exception as e:
                self.error_signal.emit(f"获取全局变量失败: {str(e)}")
        elif not self.hardware:
            # 仿真模式下提供示例全局变量数据
            try:
                # 根据API文档，全局变量格式为 {global_var_name: global_var_value(s)}
                # 布尔值用int 1和0表示，例如: {"camera_offset": [0.1, -0.2, 0.3], "start_plan": 1}
                sample_vars = {
                    "camera_offset": [0.1, -0.2, 0.3],  # 相机偏移量 (x, y, z)
                    "start_plan": 1,  # 启动计划标志 (布尔值用1表示)
                    "velocity_scale": 80,  # 速度缩放百分比
                    "force_threshold": [10.0, 10.0, 15.0, 2.0, 2.0, 2.0],  # 力阈值 [Fx, Fy, Fz, Mx, My, Mz]
                    "safety_mode": 0,  # 安全模式 (布尔值用0表示)
                    "tool_weight": 2.5,  # 工具重量 (kg)
                    "workspace_limits": [0.3, 0.8, -0.5, 0.5, 0.1, 1.2],  # 工作空间限制 [x_min, x_max, y_min, y_max, z_min, z_max]
                    "precision_mode": 1,  # 精密模式
                    "auto_recovery_enabled": 1,  # 自动恢复启用
                    "max_acceleration": 3.0  # 最大加速度
                }
                
                self.global_vars_updated.emit(sample_vars)
                self.status_updated.emit("仿真模式：已获取示例全局变量")
            except Exception as e:
                self.error_signal.emit(f"仿真模式获取全局变量失败: {str(e)}")
        else:
            self.error_signal.emit("机器人未连接，无法获取全局变量")

    def sync_urdf(self, template_urdf_path: str = None) -> bool:
        """
        同步机器人的实际运动学参数到模板URDF文件
        
        Args:
            template_urdf_path: 模板URDF文件路径，如果为None则自动查找
            
        Returns:
            bool: 同步是否成功
        """
        if not self.hardware:
            self.error_signal.emit("仿真模式下无法同步URDF")
            return False
            
        # 确保Model实例已初始化
        if self.model is None:
            # 尝试初始化Model实例
            if self.robot is not None and FLEXIV_AVAILABLE:
                try:
                    # Model已在顶部导入
                    self.model = Model(self.robot)
                    self.status_updated.emit("Model实例已初始化")
                except Exception as e:
                    self.error_signal.emit(f"Model实例初始化失败: {str(e)}")
                    return False
            else:
                self.error_signal.emit("Robot实例未初始化或Flexiv RDK不可用，无法同步URDF")
                return False
        
        # 如果没有提供模板路径，自动查找
        if template_urdf_path is None:
            # 查找项目中的模板URDF文件（修正路径到resources/urdf目录）
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            possible_paths = [
                os.path.join(project_root, 'resources', 'urdf', 'flexiv_rizon4s_kinematics.urdf'),
                os.path.join(project_root, 'resources', 'urdf', 'flexiv_rizon4_kinematics.urdf'),
                os.path.join(project_root, 'resources', 'urdf', 'flexiv_rizon10s_kinematics.urdf'),
                os.path.join(project_root, 'resources', 'urdf', 'flexiv_rizon10_kinematics.urdf')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    template_urdf_path = path
                    break
            
            if template_urdf_path is None:
                self.error_signal.emit("未找到模板URDF文件，请确保resources/urdf目录中存在URDF文件")
                return False
            
        if not os.path.exists(template_urdf_path):
            self.error_signal.emit(f"模板URDF文件不存在: {template_urdf_path}")
            return False
            
        try:
            self.status_updated.emit(f"开始同步URDF，使用模板: {os.path.basename(template_urdf_path)}")
            # 记录同步前的文件修改时间
            sync_before_time = os.path.getmtime(template_urdf_path)
            
            # 调用Flexiv RDK的SyncURDF方法
            self.model.SyncURDF(template_urdf_path)
            
            # 记录同步后的URDF文件路径
            self.last_synced_urdf_path = template_urdf_path
            
            # 验证文件是否被修改
            sync_after_time = os.path.getmtime(template_urdf_path)
            if sync_after_time > sync_before_time:
                self.status_updated.emit(f"URDF同步完成，文件已更新: {os.path.basename(template_urdf_path)}")
            else:
                self.status_updated.emit(f"URDF同步完成: {os.path.basename(template_urdf_path)}")
            
            return True
        except Exception as e:
            self.error_signal.emit(f"URDF同步失败: {str(e)}")
            return False