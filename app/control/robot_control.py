'''
Author: LK
Date: 2025-02-07 22:08:05
LastEditTime: 2025-08-12 17:45:37
LastEditors: LK
FilePath: /Demo/app/control/robot_control.py
'''
import numpy as np
import threading
import logging
from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal
import os
import time
import subprocess
import socket

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
        # 线程锁，防止多线程并发访问Robot对象导致mutex错误
        self.robot_lock = threading.RLock()
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

    def check_network_connection(self, robot_ip="192.168.2.100", timeout=3):
        """
        检查与机器人的网络连接状态
        """
        try:
            # 尝试ping机器人IP
            result = subprocess.run(
                ["ping", "-c", "1", "-W", str(timeout * 1000), robot_ip],
                capture_output=True,
                text=True,
                timeout=timeout + 1
            )
            
            if result.returncode == 0:
                # 提取延迟信息
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if "time=" in line:
                        time_part = line.split("time=")[1].split()[0]
                        latency = float(time_part)
                        self.status_updated.emit(f"网络连接正常，延迟: {latency}ms")
                        return True, latency
                return True, None
            else:
                self.status_updated.emit(f"无法ping通机器人IP: {robot_ip}")
                return False, None
                
        except subprocess.TimeoutExpired:
            self.status_updated.emit(f"网络连接超时 (>{timeout}s)")
            return False, None
        except Exception as e:
            self.status_updated.emit(f"网络检查失败: {str(e)}")
            return False, None
    
    def check_tcp_connection(self, robot_ip="192.168.2.100", port=8080, timeout=3):
        """
        检查TCP连接到机器人
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((robot_ip, port))
            sock.close()
            
            if result == 0:
                self.status_updated.emit(f"TCP连接到 {robot_ip}:{port} 成功")
                return True
            else:
                self.status_updated.emit(f"TCP连接到 {robot_ip}:{port} 失败")
                return False
                
        except Exception as e:
            self.status_updated.emit(f"TCP连接检查失败: {str(e)}")
            return False

    def update_robot_model(self, joint_angles):
        if not self.robot_model:
            return
        # 递归更新各连杆的MDH参数（略，按原modern实现）
        pass

    def run(self):
        if self.hardware:
            try:
                # 初始化机器人连接（带重试机制）
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        with self.robot_lock:
                            if self.robot is None:
                                from flexivrdk import Robot
                                self.robot = Robot(self.robot_id)
                                self.status_updated.emit(f"已连接到机器人: {self.robot_id}")
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            self.status_updated.emit(f"连接尝试 {attempt + 1} 失败，重试中...")
                            time.sleep(2)
                        else:
                            raise e
                
                # 初始化Model和Tool实例
                if self.model is None and FLEXIV_AVAILABLE:
                    try:
                        self.model = Model(self.robot)
                        self.status_updated.emit("Model实例已初始化")
                    except Exception as e:
                        logging.warning(f"Model实例初始化失败: {e}")
                        self.status_updated.emit(f"Model初始化失败: {str(e)}")
                        # Model初始化失败不影响其他功能，继续运行
                        
                if self.tool is None and FLEXIV_AVAILABLE:
                    try:
                        self.tool = Tool(self.robot)
                        self.status_updated.emit("Tool实例已初始化")
                    except Exception as e:
                        logging.warning(f"Tool实例初始化失败: {e}")
                        self.status_updated.emit(f"Tool初始化失败: {str(e)}")
                        # Tool初始化失败不影响其他功能，继续运行
                
                # 检查机器人连接状态和使能（使用线程锁保护）
                enable_success = False
                for attempt in range(3):  # 最多尝试3次使能
                    try:
                        with self.robot_lock:
                            # 检查连接状态
                            if not self.robot.connected():
                                self.status_updated.emit("机器人未连接，尝试重新连接...")
                                time.sleep(1)
                                continue
                            
                            # 首先检查机器人当前使能状态 - 按照API文档建议
                            try:
                                current_operational = self.robot.operational()
                                operational_status = self.robot.operational_status()
                                
                                self.status_updated.emit(f"自动检查机器人状态: {operational_status}")
                                
                                if current_operational:
                                    self.status_updated.emit("机器人已处于使能状态，跳过自动使能")
                                    enable_success = True
                                    break
                                
                                # 检查是否需要先处理其他状态
                                if not self.robot.estop_released():
                                    self.status_updated.emit("急停未释放，无法自动使能")
                                    break
                                
                            except Exception as e:
                                logging.error(f"状态检查失败: {e}")
                                self.status_updated.emit(f"状态检查失败: {str(e)}")
                                continue
                            
                            # 检查并清除故障
                            if self.robot.fault():
                                try:
                                    self.robot.ClearFault()
                                    self.status_updated.emit("故障已清除，等待系统稳定...")
                                    time.sleep(2)  # 增加等待时间确保故障完全清除
                                except Exception as e:
                                    logging.error(f"清除故障失败: {e}")
                                    self.status_updated.emit(f"清除故障失败: {str(e)}")
                                    continue
                            
                            # 检查恢复状态
                            if self.robot.recovery():
                                self.status_updated.emit("机器人处于恢复状态，无法自动使能")
                                break
                            
                            # 使能机器人（带重试机制）
                            self.status_updated.emit(f"状态检查通过，自动使能机器人 (第{attempt + 1}次)...")
                            self.robot.Enable()
                            self.status_updated.emit("使能命令已发送，等待机器人就绪...")
                            
                            # 等待机器人变为operational状态
                            for i in range(30):  # 增加等待时间到15秒
                                if self.robot.operational():
                                    self.status_updated.emit("机器人已使能的就绪")
                                    enable_success = True
                                    break
                                time.sleep(0.5)
                            
                            if enable_success:
                                break
                            else:
                                self.status_updated.emit(f"使能尝试 {attempt + 1} 超时")
                                
                    except Exception as e:
                        logging.error(f"机器人使能尝试 {attempt + 1} 失败: {e}")
                        self.status_updated.emit(f"使能尝试 {attempt + 1} 失败: {str(e)}")
                        if "Failed to deliver the request" in str(e):
                             self.status_updated.emit("网络通信失败，开始网络诊断...")
                             # 进行网络连接诊断
                             network_ok, latency = self.check_network_connection()
                             if not network_ok:
                                 self.status_updated.emit("网络连接异常，请检查网络设置")
                             elif latency and latency > 100:
                                 self.status_updated.emit(f"网络延迟较高({latency}ms)，可能影响通信")
                             time.sleep(3)  # 网络问题时等待更长时间
                        else:
                            time.sleep(1)
                
                if not enable_success:
                    self.status_updated.emit("机器人使能失败，但继续运行监控模式")
                    # 不返回，继续运行以监控机器人状态
                
                self.running = True
                while self.running:
                    try:
                        # 使用线程锁保护Robot对象访问
                        with self.robot_lock:
                            # 检查连接状态
                            if not self.robot.connected():
                                self.status_updated.emit("机器人连接断开")
                                break
                            
                            # 获取机器人状态数据
                            robot_states = self.robot.states()
                            
                            # 检查机器人状态
                            if self.robot.fault():
                                self.status_updated.emit("机器人故障状态")
                                # 注意：不要自动清除故障，应该由用户手动处理
                                # self.robot.ClearFault()
                            elif self.robot.operational():
                                pass  # 正常运行，不频繁更新状态信息
                            else:
                                self.status_updated.emit("机器人已连接但未使能")
                            
                            # 机器人模式
                            current_mode = self.robot.mode()
                            self.mode_updated.emit(str(current_mode))
                        
                        # 在锁外处理数据，避免长时间持有锁
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
                        
                        # 末端执行器位置和姿态 (TCP完整姿态)
                        tcp_pose = list(robot_states.tcp_pose)
                        # TCP姿态格式: [x, y, z, qw, qx, qy, qz] (位置 + 四元数)
                        self.end_effector_updated.emit(tcp_pose)  # 发送完整的TCP姿态数据
                        
                        # 力/力矩传感器数据 (TCP坐标系下的外部力)
                        if hasattr(robot_states, 'ext_wrench_in_tcp'):
                            ft_data = list(robot_states.ext_wrench_in_tcp)
                            self.ft_sensor_updated.emit(ft_data)
                        
                        # 更新机器人模型
                        self.update_robot_model(joint_angles)
                        
                    except Exception as e:
                        logging.warning(f"获取机器人状态时出错: {e}")
                        # 继续运行，不因单次状态获取失败而退出
                    
                    # 控制循环频率 (约50Hz，避免过于频繁)
                    time.sleep(0.02)
                    
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
        # 注意：Brake()方法仅适用于医疗机器人，工业机器人不支持此功能
        # if self.hardware and self.robot and self.robot.connected():
        #     self.robot.Brake(True)  # 仅医疗机器人支持
        self.status_updated.emit("已停止")
    
    def stop(self):
        """停止线程运行"""
        self.stop_robot()

    def enable_robot(self):
        if self.hardware and self.robot is not None:
            try:
                with self.robot_lock:
                    # 检查连接状态
                    if not self.robot.connected():
                        self.status_updated.emit("机器人未连接，无法使能")
                        return
                    
                    # 首先检查机器人当前使能状态 - 按照API文档建议
                    try:
                        current_operational = self.robot.operational()
                        operational_status = self.robot.operational_status()
                        
                        self.status_updated.emit(f"当前机器人状态: {operational_status}")
                        
                        if current_operational:
                            self.status_updated.emit("机器人已处于使能状态，无需重复使能")
                            return
                        
                        # 检查是否需要先处理其他状态
                        if not self.robot.estop_released():
                            self.status_updated.emit("急停未释放，请先释放急停按钮")
                            return
                        
                        if self.robot.fault():
                            self.status_updated.emit("检测到故障状态，正在清除故障...")
                            try:
                                self.robot.ClearFault()
                                self.status_updated.emit("故障已清除，等待系统稳定...")
                                time.sleep(2)  # 等待故障完全清除
                            except Exception as e:
                                logging.error(f"清除故障失败: {e}")
                                self.status_updated.emit(f"清除故障失败: {str(e)}")
                                return
                        
                        if self.robot.recovery():
                            self.status_updated.emit("机器人处于恢复状态，请先完成恢复操作")
                            return
                            
                    except Exception as e:
                        logging.error(f"检查机器人状态失败: {e}")
                        self.status_updated.emit(f"检查机器人状态失败: {str(e)}")
                        return
            
            except Exception as e:
                logging.error(f"状态检查失败: {e}")
                self.status_updated.emit(f"状态检查失败: {str(e)}")
                return
            
            # 使能重试机制
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    with self.robot_lock:
                        
                        # 发送使能命令 - 状态检查已通过
                        self.status_updated.emit(f"状态检查通过，开始使能机器人 (第{attempt + 1}次)...")
                        self.robot.Enable()
                        self.status_updated.emit("使能命令已发送，等待机器人就绪...")
                        
                        # 等待机器人变为operational状态
                        for i in range(30):  # 等待最多15秒
                            if self.robot.operational():
                                self.status_updated.emit("机器人已成功使能")
                                return  # 成功使能，退出函数
                            time.sleep(0.5)
                        
                        # 如果到这里说明超时了
                        self.status_updated.emit(f"使能尝试 {attempt + 1} 超时")
                        
                except Exception as e:
                    logging.error(f"使能尝试 {attempt + 1} 失败: {e}")
                    error_msg = str(e)
                    
                    if "Failed to deliver the request" in error_msg:
                         self.status_updated.emit(f"网络通信失败 (尝试 {attempt + 1}): 开始网络诊断...")
                         # 进行网络连接诊断
                         network_ok, latency = self.check_network_connection()
                         if not network_ok:
                             self.status_updated.emit("网络连接异常，请检查网络设置")
                         elif latency and latency > 100:
                             self.status_updated.emit(f"网络延迟较高({latency}ms)，可能影响通信")
                         time.sleep(3)  # 网络问题等待更长时间
                    elif "mutex lock failed" in error_msg:
                        self.status_updated.emit(f"系统锁定错误 (尝试 {attempt + 1}): 等待系统恢复")
                        time.sleep(2)
                    else:
                        self.status_updated.emit(f"使能失败 (尝试 {attempt + 1}): {error_msg}")
                        time.sleep(1)
                    
                    # 如果是最后一次尝试，不再重试
                    if attempt == max_attempts - 1:
                        self.status_updated.emit("所有使能尝试均失败")
                        return
            
            # 如果所有尝试都失败了
            self.status_updated.emit("机器人使能失败，请检查机器人状态和网络连接")
        else:
            self.status_updated.emit("机器人对象未初始化，无法使能")

    def disable_robot(self):
        self.stop_robot()

    def get_plan_list(self):
        """获取机器人Plan列表
        
        根据Flexiv RDK官方示例，必须先切换到NRT_PLAN_EXECUTION模式才能正确获取Plan列表。
        这是官方推荐的标准流程，可以避免"No reply from the robot"错误。
        """
        if self.hardware and self.robot is not None:
            try:
                # 检查机器人基本状态
                connected = self.robot.connected()
                operational = self.robot.operational()
                current_mode = self.robot.mode()
                
                self.status_updated.emit(f"机器人状态 - 连接: {connected}, 使能: {operational}, 模式: {current_mode}")
                
                if not connected:
                    self.error_signal.emit("机器人未连接，无法获取Plan列表")
                    return []
                
                if not operational:
                    self.error_signal.emit("机器人未使能，无法获取Plan列表")
                    return []
                
                # 检查机器人是否有故障
                if self.robot.fault():
                    self.error_signal.emit("机器人存在故障，无法获取Plan列表")
                    return []
                
                # 记录原始模式，用于后续恢复
                original_mode = current_mode
                
                # 按照官方示例，切换到NRT_PLAN_EXECUTION模式
                if current_mode != Mode.NRT_PLAN_EXECUTION:
                    self.status_updated.emit("按照官方示例，切换到NRT_PLAN_EXECUTION模式")
                    self.robot.SwitchMode(Mode.NRT_PLAN_EXECUTION)
                    
                    # 等待模式切换完成
                    timeout = 10  # 10秒超时
                    start_time = time.time()
                    while self.robot.mode() != Mode.NRT_PLAN_EXECUTION:
                        if time.time() - start_time > timeout:
                            self.error_signal.emit("切换到NRT_PLAN_EXECUTION模式超时")
                            return []
                        time.sleep(0.1)
                    
                    self.status_updated.emit("成功切换到NRT_PLAN_EXECUTION模式")
                
                # 按照官方示例，在获取Plan列表前检查机器人busy状态
                # 确保机器人不在执行其他任务
                if self.robot.busy():
                    self.status_updated.emit("机器人正忙，等待任务完成...")
                    timeout = 30  # 30秒超时
                    start_time = time.time()
                    while self.robot.busy():
                        if time.time() - start_time > timeout:
                            self.error_signal.emit("等待机器人空闲超时")
                            return []
                        time.sleep(0.5)
                    self.status_updated.emit("机器人已空闲")
                
                # 添加额外等待时间，确保模式切换完全稳定
                time.sleep(1.0)
                
                # 获取Plan列表
                self.status_updated.emit("正在获取Plan列表...")
                plan_list = self.robot.plan_list()
                
                if plan_list:
                    self.status_updated.emit(f"成功获取到 {len(plan_list)} 个Plan: {plan_list}")
                    self.plan_list_updated.emit(plan_list)
                else:
                    self.status_updated.emit("获取到空Plan列表，机器人中可能没有加载任何Plan")
                    self.plan_list_updated.emit([])
                
                # 如果之前切换了模式，尝试恢复到原始模式
                if original_mode != Mode.NRT_PLAN_EXECUTION:
                    try:
                        self.status_updated.emit(f"恢复到原始模式: {original_mode}")
                        self.robot.SwitchMode(original_mode)
                        
                        # 等待模式恢复完成
                        timeout = 5  # 5秒超时
                        start_time = time.time()
                        while self.robot.mode() != original_mode:
                            if time.time() - start_time > timeout:
                                self.status_updated.emit("恢复原始模式超时，但Plan列表已获取成功")
                                break
                            time.sleep(0.1)
                        
                        if self.robot.mode() == original_mode:
                            self.status_updated.emit("成功恢复到原始模式")
                    except Exception as e:
                        self.status_updated.emit(f"恢复原始模式失败: {e}，但Plan列表已获取成功")
                
                return plan_list if plan_list else []
                
            except Exception as e:
                error_msg = f"获取Plan列表失败: {str(e)}"
                self.status_updated.emit(error_msg)
                self.error_signal.emit(error_msg)
                logging.error(f"获取Plan列表异常: {e}")
                return []
        
        elif not self.hardware:
            # 仿真模式下的模拟Plan列表
            simulation_plans = [
                "demo_plan_1",
                "demo_plan_2", 
                "pick_and_place",
                "trajectory_demo",
                "calibration_routine"
            ]
            self.status_updated.emit(f"仿真模式 - 获取到Plan列表: {simulation_plans}")
            self.plan_list_updated.emit(simulation_plans)
            return simulation_plans
        
        else:
            self.error_signal.emit("请先连接并使能机器人，再获取Plan列表")
            return []

    def get_plan_info(self):
        if self.hardware and self.robot is not None:
            try:
                # 检查机器人状态
                if not self.robot.connected():
                    self.error_signal.emit("机器人未连接，无法获取Plan信息")
                    return None
                if not self.robot.operational():
                    self.error_signal.emit("机器人未使能，无法获取Plan信息")
                    return None
                
                # 保存当前模式
                current_mode = self.robot.mode()
                mode_switched = False
                
                # 确保在NRT_PLAN_EXECUTION模式下获取plan信息
                if current_mode != Mode.NRT_PLAN_EXECUTION:
                    try:
                        self.robot.SwitchMode(Mode.NRT_PLAN_EXECUTION)
                        mode_switched = True
                        time.sleep(0.1)
                        self.status_updated.emit(f"切换到NRT_PLAN_EXECUTION模式以获取Plan信息")
                    except Exception as e:
                        self.error_signal.emit(f"无法切换到NRT_PLAN_EXECUTION模式: {str(e)}")
                        return None
                
                # 使用正确的API获取Plan信息
                info = self.robot.plan_info()
                self.plan_info_updated.emit(info)
                
                # 恢复原模式
                if mode_switched:
                    try:
                        self.robot.SwitchMode(current_mode)
                        self.status_updated.emit(f"恢复到原模式: {self.robot.mode()}")
                    except Exception as e:
                        self.status_updated.emit(f"恢复模式失败: {str(e)}")
                
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
                # 检查机器人状态
                if not self.robot.connected():
                    self.error_signal.emit("机器人未连接，无法执行Primitive")
                    return
                if not self.robot.operational():
                    self.error_signal.emit("机器人未使能，无法执行Primitive")
                    return
                
                # 保存当前模式
                current_mode = self.robot.mode()
                mode_switched = False
                
                # 切换到NRT_PRIMITIVE_EXECUTION模式
                if current_mode != Mode.NRT_PRIMITIVE_EXECUTION:
                    self.robot.SwitchMode(Mode.NRT_PRIMITIVE_EXECUTION)
                    mode_switched = True
                    time.sleep(0.1)
                    self.status_updated.emit("已切换到NRT_PRIMITIVE_EXECUTION模式")
                    self.update_mode_signal()
                
                if params is None:
                    params = dict()
                if properties is None:
                    properties = dict()
                self.robot.ExecutePrimitive(primitive, params, properties)
                self.status_updated.emit(f"执行Primitive: {primitive}")
                
                # 恢复原模式
                if mode_switched:
                    try:
                        self.robot.SwitchMode(current_mode)
                        self.status_updated.emit(f"恢复到原模式: {self.robot.mode()}")
                    except Exception as e:
                        self.status_updated.emit(f"恢复模式失败: {str(e)}")
                        
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
                # 检查机器人状态
                if not self.robot.connected():
                    self.error_signal.emit("机器人未连接，无法执行力/力矩传感器归零")
                    return
                if not self.robot.operational():
                    self.error_signal.emit("机器人未使能，无法执行力/力矩传感器归零")
                    return
                
                # 保存当前模式
                current_mode = self.robot.mode()
                mode_switched = False
                
                # 切换到NRT_PRIMITIVE_EXECUTION模式
                if current_mode != Mode.NRT_PRIMITIVE_EXECUTION:
                    self.robot.SwitchMode(Mode.NRT_PRIMITIVE_EXECUTION)
                    mode_switched = True
                    self.status_updated.emit("已切换到NRT_PRIMITIVE_EXECUTION模式")
                    # 等待模式切换完成
                    time.sleep(0.5)
                
                # 使用ExecutePrimitive方法执行ZeroFTSensor
                self.robot.ExecutePrimitive("ZeroFTSensor", {})
                self.force_sensor_zeroed.emit()
                self.status_updated.emit("力/力矩传感器归零命令已发送")
                
                # 监控primitive执行状态
                def monitor_zeroing():
                    try:
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
                        
                        # 恢复原模式
                        if mode_switched:
                            try:
                                self.robot.SwitchMode(current_mode)
                                self.status_updated.emit(f"恢复到原模式: {self.robot.mode()}")
                            except Exception as e:
                                self.status_updated.emit(f"恢复模式失败: {str(e)}")
                            
                    except Exception as e:
                        self.error_signal.emit(f"力/力矩传感器归零监控失败: {str(e)}")
                        # 即使出错也尝试恢复模式
                        if mode_switched:
                            try:
                                self.robot.SwitchMode(current_mode)
                            except:
                                pass
                
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
                
                # 确保机器人处于IDLE模式（Tool.Switch()要求）
                with self.robot_lock:
                    current_mode = self.robot.mode()
                    if current_mode != Mode.IDLE:
                        self.status_updated.emit(f"当前模式: {current_mode}, 切换到IDLE模式...")
                        self.robot.SwitchMode(Mode.IDLE)
                        
                        # 等待模式切换完成
                        max_wait_time = 5.0  # 最大等待5秒
                        start_time = time.time()
                        while time.time() - start_time < max_wait_time:
                            if self.robot.mode() == Mode.IDLE:
                                break
                            time.sleep(0.1)
                        
                        # 验证模式切换是否成功
                        if self.robot.mode() != Mode.IDLE:
                            self.error_signal.emit("无法切换到IDLE模式，工具切换失败")
                            return
                        
                        self.status_updated.emit("已切换到IDLE模式")
                    
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
                
                # 确保机器人处于IDLE模式（Tool.Update()要求）
                with self.robot_lock:
                    current_mode = self.robot.mode()
                    if current_mode != Mode.IDLE:
                        self.status_updated.emit(f"当前模式: {current_mode}, 切换到IDLE模式...")
                        self.robot.SwitchMode(Mode.IDLE)
                        
                        # 等待模式切换完成
                        max_wait_time = 5.0  # 最大等待5秒
                        start_time = time.time()
                        while time.time() - start_time < max_wait_time:
                            if self.robot.mode() == Mode.IDLE:
                                break
                            time.sleep(0.1)
                        
                        # 验证模式切换是否成功
                        if self.robot.mode() != Mode.IDLE:
                            self.error_signal.emit("无法切换到IDLE模式，工具更新失败")
                            return
                        
                        self.status_updated.emit("已切换到IDLE模式")
                    
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
    
    def set_global_variables(self, variables: dict):
        """设置机器人全局变量"""
        if self.hardware and self.robot is not None:
            try:
                # 根据API文档，SetGlobalVariables接受格式为 {global_var_name: global_var_value(s)}
                # 布尔值用int 1和0表示
                self.robot.SetGlobalVariables(variables)
                self.status_updated.emit(f"已设置 {len(variables)} 个全局变量")
                
                # 设置完成后重新获取全局变量以确认更新
                self.get_global_variables()
                
            except Exception as e:
                self.error_signal.emit(f"设置全局变量失败: {str(e)}")
        elif not self.hardware:
            # 仿真模式下模拟设置全局变量
            try:
                # 在仿真模式下，我们可以更新示例数据来模拟设置过程
                self.status_updated.emit(f"仿真模式：已设置 {len(variables)} 个全局变量")
                
                # 模拟设置后重新获取全局变量
                self.get_global_variables()
                
            except Exception as e:
                self.error_signal.emit(f"仿真模式设置全局变量失败: {str(e)}")
        else:
            self.error_signal.emit("机器人未连接，无法设置全局变量")

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
                    logging.warning(f"Model实例初始化失败: {e}")
                    self.error_signal.emit(f"Model实例初始化失败，URDF同步功能不可用: {str(e)}")
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