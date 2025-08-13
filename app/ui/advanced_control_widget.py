'''
Author: LK
Date: 2025-01-XX XX:XX:XX
LastEditTime: 2025-01-XX XX:XX:XX
LastEditors: LK
FilePath: /Demo/app/ui/advanced_control_widget.py
'''

import sys
import json
import time
from typing import Dict, Any, List, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QProgressBar, QTableWidget, QTableWidgetItem,
    QTreeWidget, QTreeWidgetItem, QGroupBox, QSplitter, QFrame,
    QScrollArea, QListWidget, QListWidgetItem, QSlider, QDial,
    QMessageBox, QFileDialog, QInputDialog, QColorDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPalette

# 导入管理器模块
try:
    from ..control.primitive_manager import PrimitiveManager
    from ..control.safety_manager import SafetyManager
    from ..control.scheduler_manager import SchedulerManager
    from ..control.workcoord_manager import WorkCoordManager
    from ..control.maintenance_manager import MaintenanceManager
    from ..control.fileio_manager import FileIOManager
    from ..control.device_manager import DeviceManager
except ImportError:
    # 如果导入失败，使用占位符类
    class PrimitiveManager: pass
    class SafetyManager: pass
    class SchedulerManager: pass
    class WorkCoordManager: pass
    class MaintenanceManager: pass
    class FileIOManager: pass
    class DeviceManager: pass

class AdvancedControlWidget(QWidget):
    """高级控制面板
    
    集成所有高级功能模块：
    - Primitive原语控制
    - Safety安全管理
    - Scheduler任务调度
    - WorkCoord工作坐标
    - Maintenance维护管理
    - FileIO文件传输
    - Device设备管理
    """
    
    # 信号定义
    status_updated = pyqtSignal(str)  # 状态更新
    error_occurred = pyqtSignal(str)  # 错误发生
    
    def __init__(self, robot_control=None, parent=None):
        super().__init__(parent)
        
        self.robot_control = robot_control
        
        # 管理器实例
        self.primitive_manager = None
        self.safety_manager = None
        self.scheduler_manager = None
        self.workcoord_manager = None
        self.maintenance_manager = None
        self.fileio_manager = None
        self.device_manager = None
        
        # 初始化UI
        self.init_ui()
        
        # 初始化管理器
        self.init_managers()
        
        # 连接信号
        self.connect_signals()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 创建各个功能标签页
        self.create_primitive_tab()
        self.create_safety_tab()
        self.create_scheduler_tab()
        self.create_workcoord_tab()
        self.create_maintenance_tab()
        self.create_fileio_tab()
        self.create_device_tab()
        
        # 状态栏
        self.status_label = QLabel("高级控制面板已就绪")
        self.status_label.setStyleSheet("QLabel { padding: 5px; background-color: #f0f0f0; }")
        layout.addWidget(self.status_label)
    
    def create_primitive_tab(self):
        """创建Primitive原语控制标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 原语选择区域
        primitive_group = QGroupBox("原语控制")
        primitive_layout = QGridLayout(primitive_group)
        
        # 原语类别选择
        primitive_layout.addWidget(QLabel("原语类别:"), 0, 0)
        self.primitive_category_combo = QComboBox()
        self.primitive_category_combo.addItems([
            "运动控制", "工作流", "基础力控制", "高级力控制",
            "自适应装配", "表面处理", "柔性搬运", "自适应抓取",
            "零重力浮动", "康复理疗", "视觉伺服", "展示应用"
        ])
        primitive_layout.addWidget(self.primitive_category_combo, 0, 1)
        
        # 原语选择
        primitive_layout.addWidget(QLabel("原语名称:"), 1, 0)
        self.primitive_name_combo = QComboBox()
        primitive_layout.addWidget(self.primitive_name_combo, 1, 1)
        
        # 参数配置区域
        self.primitive_params_widget = QWidget()
        self.primitive_params_layout = QVBoxLayout(self.primitive_params_widget)
        
        # 执行控制
        control_layout = QHBoxLayout()
        self.execute_primitive_btn = QPushButton("执行原语")
        self.stop_primitive_btn = QPushButton("停止原语")
        self.stop_primitive_btn.setEnabled(False)
        control_layout.addWidget(self.execute_primitive_btn)
        control_layout.addWidget(self.stop_primitive_btn)
        control_layout.addStretch()
        
        # 状态显示
        self.primitive_status_label = QLabel("状态: 就绪")
        self.primitive_progress_bar = QProgressBar()
        
        layout.addWidget(primitive_group)
        layout.addWidget(QLabel("参数配置:"))
        layout.addWidget(self.primitive_params_widget)
        layout.addLayout(control_layout)
        layout.addWidget(self.primitive_status_label)
        layout.addWidget(self.primitive_progress_bar)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "原语控制")
    
    def create_safety_tab(self):
        """创建Safety安全管理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 安全状态监控
        safety_status_group = QGroupBox("安全状态监控")
        status_layout = QGridLayout(safety_status_group)
        
        self.safety_status_labels = {}
        safety_items = [
            ("系统状态", "system_status"),
            ("碰撞检测", "collision_detection"),
            ("限位保护", "limit_protection"),
            ("紧急停止", "emergency_stop"),
            ("安全门", "safety_door"),
            ("光幕保护", "light_curtain")
        ]
        
        for i, (name, key) in enumerate(safety_items):
            status_layout.addWidget(QLabel(f"{name}:"), i, 0)
            label = QLabel("正常")
            label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            self.safety_status_labels[key] = label
            status_layout.addWidget(label, i, 1)
        
        # 安全配置
        safety_config_group = QGroupBox("安全配置")
        config_layout = QGridLayout(safety_config_group)
        
        # 碰撞检测阈值
        config_layout.addWidget(QLabel("碰撞检测阈值:"), 0, 0)
        self.collision_threshold_spin = QDoubleSpinBox()
        self.collision_threshold_spin.setRange(0.1, 10.0)
        self.collision_threshold_spin.setValue(2.0)
        self.collision_threshold_spin.setSuffix(" N")
        config_layout.addWidget(self.collision_threshold_spin, 0, 1)
        
        # 速度限制
        config_layout.addWidget(QLabel("最大速度:"), 1, 0)
        self.max_velocity_spin = QDoubleSpinBox()
        self.max_velocity_spin.setRange(0.1, 5.0)
        self.max_velocity_spin.setValue(1.0)
        self.max_velocity_spin.setSuffix(" m/s")
        config_layout.addWidget(self.max_velocity_spin, 1, 1)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        self.enable_safety_btn = QPushButton("启用安全系统")
        self.disable_safety_btn = QPushButton("禁用安全系统")
        self.emergency_stop_btn = QPushButton("紧急停止")
        self.emergency_stop_btn.setStyleSheet("QPushButton { background-color: red; color: white; font-weight: bold; }")
        
        control_layout.addWidget(self.enable_safety_btn)
        control_layout.addWidget(self.disable_safety_btn)
        control_layout.addWidget(self.emergency_stop_btn)
        control_layout.addStretch()
        
        layout.addWidget(safety_status_group)
        layout.addWidget(safety_config_group)
        layout.addLayout(control_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "安全管理")
    
    def create_scheduler_tab(self):
        """创建Scheduler任务调度标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # 左侧：任务列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 任务列表
        left_layout.addWidget(QLabel("任务队列:"))
        self.task_list_widget = QListWidget()
        left_layout.addWidget(self.task_list_widget)
        
        # 任务控制按钮
        task_control_layout = QHBoxLayout()
        self.add_task_btn = QPushButton("添加任务")
        self.remove_task_btn = QPushButton("删除任务")
        self.start_scheduler_btn = QPushButton("开始调度")
        self.stop_scheduler_btn = QPushButton("停止调度")
        
        task_control_layout.addWidget(self.add_task_btn)
        task_control_layout.addWidget(self.remove_task_btn)
        task_control_layout.addWidget(self.start_scheduler_btn)
        task_control_layout.addWidget(self.stop_scheduler_btn)
        
        left_layout.addLayout(task_control_layout)
        
        # 右侧：任务详情
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 任务详情
        task_details_group = QGroupBox("任务详情")
        details_layout = QGridLayout(task_details_group)
        
        details_layout.addWidget(QLabel("任务名称:"), 0, 0)
        self.task_name_edit = QLineEdit()
        details_layout.addWidget(self.task_name_edit, 0, 1)
        
        details_layout.addWidget(QLabel("任务类型:"), 1, 0)
        self.task_type_combo = QComboBox()
        self.task_type_combo.addItems(["原语执行", "运动控制", "数据采集", "文件传输"])
        details_layout.addWidget(self.task_type_combo, 1, 1)
        
        details_layout.addWidget(QLabel("优先级:"), 2, 0)
        self.task_priority_spin = QSpinBox()
        self.task_priority_spin.setRange(1, 10)
        self.task_priority_spin.setValue(5)
        details_layout.addWidget(self.task_priority_spin, 2, 1)
        
        details_layout.addWidget(QLabel("任务参数:"), 3, 0)
        self.task_params_edit = QTextEdit()
        self.task_params_edit.setMaximumHeight(100)
        details_layout.addWidget(self.task_params_edit, 3, 1)
        
        right_layout.addWidget(task_details_group)
        
        # 调度状态
        scheduler_status_group = QGroupBox("调度状态")
        status_layout = QGridLayout(scheduler_status_group)
        
        self.scheduler_status_label = QLabel("状态: 停止")
        self.current_task_label = QLabel("当前任务: 无")
        self.completed_tasks_label = QLabel("已完成: 0")
        self.failed_tasks_label = QLabel("失败: 0")
        
        status_layout.addWidget(self.scheduler_status_label, 0, 0)
        status_layout.addWidget(self.current_task_label, 0, 1)
        status_layout.addWidget(self.completed_tasks_label, 1, 0)
        status_layout.addWidget(self.failed_tasks_label, 1, 1)
        
        right_layout.addWidget(scheduler_status_group)
        right_layout.addStretch()
        
        # 添加到分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(tab, "任务调度")
    
    def create_workcoord_tab(self):
        """创建WorkCoord工作坐标标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 坐标系列表
        coord_list_group = QGroupBox("工作坐标系")
        list_layout = QVBoxLayout(coord_list_group)
        
        self.coord_tree_widget = QTreeWidget()
        self.coord_tree_widget.setHeaderLabels(["名称", "类型", "状态", "描述"])
        list_layout.addWidget(self.coord_tree_widget)
        
        # 坐标系操作按钮
        coord_control_layout = QHBoxLayout()
        self.add_coord_btn = QPushButton("添加坐标系")
        self.edit_coord_btn = QPushButton("编辑坐标系")
        self.delete_coord_btn = QPushButton("删除坐标系")
        self.calibrate_coord_btn = QPushButton("标定坐标系")
        self.switch_coord_btn = QPushButton("切换坐标系")
        
        coord_control_layout.addWidget(self.add_coord_btn)
        coord_control_layout.addWidget(self.edit_coord_btn)
        coord_control_layout.addWidget(self.delete_coord_btn)
        coord_control_layout.addWidget(self.calibrate_coord_btn)
        coord_control_layout.addWidget(self.switch_coord_btn)
        coord_control_layout.addStretch()
        
        list_layout.addLayout(coord_control_layout)
        
        # 坐标系详情
        coord_details_group = QGroupBox("坐标系详情")
        details_layout = QGridLayout(coord_details_group)
        
        # 位置信息
        details_layout.addWidget(QLabel("位置 (X, Y, Z):"), 0, 0)
        self.coord_position_labels = [QLabel("0.000") for _ in range(3)]
        pos_layout = QHBoxLayout()
        for i, label in enumerate(self.coord_position_labels):
            pos_layout.addWidget(QLabel(f"{['X', 'Y', 'Z'][i]}:"))
            pos_layout.addWidget(label)
        details_layout.addLayout(pos_layout, 0, 1)
        
        # 姿态信息
        details_layout.addWidget(QLabel("姿态 (RX, RY, RZ):"), 1, 0)
        self.coord_rotation_labels = [QLabel("0.000") for _ in range(3)]
        rot_layout = QHBoxLayout()
        for i, label in enumerate(self.coord_rotation_labels):
            rot_layout.addWidget(QLabel(f"{['RX', 'RY', 'RZ'][i]}:"))
            rot_layout.addWidget(label)
        details_layout.addLayout(rot_layout, 1, 1)
        
        # 当前坐标系
        details_layout.addWidget(QLabel("当前坐标系:"), 2, 0)
        self.current_coord_label = QLabel("世界坐标系")
        self.current_coord_label.setStyleSheet("QLabel { font-weight: bold; color: blue; }")
        details_layout.addWidget(self.current_coord_label, 2, 1)
        
        layout.addWidget(coord_list_group)
        layout.addWidget(coord_details_group)
        
        self.tab_widget.addTab(tab, "工作坐标")
    
    def create_maintenance_tab(self):
        """创建Maintenance维护管理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 系统状态
        system_status_group = QGroupBox("系统状态")
        status_layout = QGridLayout(system_status_group)
        
        # 状态指示器
        status_items = [
            ("系统健康度", "system_health"),
            ("运行时间", "uptime"),
            ("CPU使用率", "cpu_usage"),
            ("内存使用率", "memory_usage"),
            ("磁盘使用率", "disk_usage"),
            ("网络状态", "network_status")
        ]
        
        self.maintenance_status_labels = {}
        for i, (name, key) in enumerate(status_items):
            status_layout.addWidget(QLabel(f"{name}:"), i, 0)
            label = QLabel("正常")
            self.maintenance_status_labels[key] = label
            status_layout.addWidget(label, i, 1)
        
        # 维护操作
        maintenance_ops_group = QGroupBox("维护操作")
        ops_layout = QGridLayout(maintenance_ops_group)
        
        # 诊断测试
        ops_layout.addWidget(QLabel("诊断测试:"), 0, 0)
        self.diagnostic_combo = QComboBox()
        self.diagnostic_combo.addItems(["系统自检", "关节测试", "传感器测试", "通信测试"])
        ops_layout.addWidget(self.diagnostic_combo, 0, 1)
        self.run_diagnostic_btn = QPushButton("运行诊断")
        ops_layout.addWidget(self.run_diagnostic_btn, 0, 2)
        
        # 校准操作
        ops_layout.addWidget(QLabel("校准操作:"), 1, 0)
        self.calibration_combo = QComboBox()
        self.calibration_combo.addItems(["关节校准", "工具校准", "力传感器校准", "视觉校准"])
        ops_layout.addWidget(self.calibration_combo, 1, 1)
        self.run_calibration_btn = QPushButton("开始校准")
        ops_layout.addWidget(self.run_calibration_btn, 1, 2)
        
        # 系统备份
        ops_layout.addWidget(QLabel("系统备份:"), 2, 0)
        self.backup_system_btn = QPushButton("创建备份")
        self.restore_system_btn = QPushButton("恢复备份")
        backup_layout = QHBoxLayout()
        backup_layout.addWidget(self.backup_system_btn)
        backup_layout.addWidget(self.restore_system_btn)
        ops_layout.addLayout(backup_layout, 2, 1, 1, 2)
        
        # 维护记录
        maintenance_log_group = QGroupBox("维护记录")
        log_layout = QVBoxLayout(maintenance_log_group)
        
        self.maintenance_log_widget = QTextEdit()
        self.maintenance_log_widget.setReadOnly(True)
        self.maintenance_log_widget.setMaximumHeight(150)
        log_layout.addWidget(self.maintenance_log_widget)
        
        # 清除日志按钮
        self.clear_log_btn = QPushButton("清除日志")
        log_layout.addWidget(self.clear_log_btn)
        
        layout.addWidget(system_status_group)
        layout.addWidget(maintenance_ops_group)
        layout.addWidget(maintenance_log_group)
        
        self.tab_widget.addTab(tab, "维护管理")
    
    def create_fileio_tab(self):
        """创建FileIO文件传输标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # 左侧：本地文件
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("本地文件:"))
        self.local_file_tree = QTreeWidget()
        self.local_file_tree.setHeaderLabels(["名称", "大小", "修改时间"])
        left_layout.addWidget(self.local_file_tree)
        
        # 右侧：远程文件
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_layout.addWidget(QLabel("远程文件:"))
        self.remote_file_tree = QTreeWidget()
        self.remote_file_tree.setHeaderLabels(["名称", "大小", "修改时间"])
        right_layout.addWidget(self.remote_file_tree)
        
        # 中间：传输控制
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        
        # 传输按钮
        self.upload_btn = QPushButton("上传 →")
        self.download_btn = QPushButton("← 下载")
        self.sync_btn = QPushButton("同步")
        
        middle_layout.addStretch()
        middle_layout.addWidget(self.upload_btn)
        middle_layout.addWidget(self.download_btn)
        middle_layout.addWidget(self.sync_btn)
        middle_layout.addStretch()
        
        # 传输进度
        progress_group = QGroupBox("传输进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.transfer_progress_bar = QProgressBar()
        self.transfer_status_label = QLabel("就绪")
        
        progress_layout.addWidget(self.transfer_progress_bar)
        progress_layout.addWidget(self.transfer_status_label)
        
        middle_layout.addWidget(progress_group)
        
        # 添加到分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(middle_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 2)
        
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(tab, "文件传输")
    
    def create_device_tab(self):
        """创建Device设备管理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 设备发现
        discovery_group = QGroupBox("设备发现")
        discovery_layout = QHBoxLayout(discovery_group)
        
        discovery_layout.addWidget(QLabel("网络范围:"))
        self.network_range_edit = QLineEdit("192.168.2.0/24")
        discovery_layout.addWidget(self.network_range_edit)
        
        self.discover_devices_btn = QPushButton("发现设备")
        self.refresh_devices_btn = QPushButton("刷新")
        discovery_layout.addWidget(self.discover_devices_btn)
        discovery_layout.addWidget(self.refresh_devices_btn)
        discovery_layout.addStretch()
        
        # 设备列表
        device_list_group = QGroupBox("设备列表")
        list_layout = QVBoxLayout(device_list_group)
        
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(6)
        self.device_table.setHorizontalHeaderLabels(["IP地址", "名称", "型号", "状态", "延迟", "操作"])
        list_layout.addWidget(self.device_table)
        
        # 设备详情
        device_details_group = QGroupBox("设备详情")
        details_layout = QGridLayout(device_details_group)
        
        self.device_detail_labels = {}
        detail_items = [
            ("IP地址", "ip"),
            ("设备名称", "name"),
            ("设备型号", "model"),
            ("序列号", "serial"),
            ("固件版本", "firmware"),
            ("硬件版本", "hardware"),
            ("连接状态", "status"),
            ("网络延迟", "latency")
        ]
        
        for i, (name, key) in enumerate(detail_items):
            row, col = i // 2, (i % 2) * 2
            details_layout.addWidget(QLabel(f"{name}:"), row, col)
            label = QLabel("--")
            self.device_detail_labels[key] = label
            details_layout.addWidget(label, row, col + 1)
        
        layout.addWidget(discovery_group)
        layout.addWidget(device_list_group)
        layout.addWidget(device_details_group)
        
        self.tab_widget.addTab(tab, "设备管理")
    
    def init_managers(self):
        """初始化管理器"""
        try:
            # 获取机器人对象
            robot = None
            hardware = True
            
            if self.robot_control:
                robot = self.robot_control.robot
                hardware = self.robot_control.hardware
            
            # 初始化各个管理器，传递正确的参数
            self.primitive_manager = PrimitiveManager(robot=robot, hardware=hardware)
            self.safety_manager = SafetyManager(robot=robot, hardware=hardware)
            self.scheduler_manager = SchedulerManager(robot=robot, hardware=hardware)
            self.workcoord_manager = WorkCoordManager(robot=robot, hardware=hardware)
            self.maintenance_manager = MaintenanceManager(robot=robot, hardware=hardware)
            self.fileio_manager = FileIOManager(robot=robot, hardware=hardware)
            self.device_manager = DeviceManager()
            
            self.status_updated.emit("所有管理器已初始化")
            
        except Exception as e:
            self.error_occurred.emit(f"管理器初始化失败: {str(e)}")
    
    def connect_signals(self):
        """连接信号"""
        try:
            # 连接各个管理器的信号
            if self.primitive_manager:
                # 修复信号名称：使用正确的信号名称
                self.primitive_manager.status_updated.connect(
                    lambda status: self.primitive_status_label.setText(f"状态: {status}")
                )
                self.primitive_manager.primitive_started.connect(
                    lambda name: self.primitive_status_label.setText(f"执行中: {name}")
                )
                self.primitive_manager.primitive_completed.connect(
                    lambda name, result: self.primitive_status_label.setText(f"完成: {name}")
                )
                self.primitive_manager.primitive_failed.connect(
                    lambda name, error: self.primitive_status_label.setText(f"失败: {name} - {error}")
                )
                self.primitive_manager.primitive_progress.connect(
                    lambda name, state: self.primitive_progress_bar.setValue(int(state.get('progress', 0)))
                )
            
            if self.safety_manager:
                self.safety_manager.safety_status_changed.connect(
                    self.update_safety_status
                )
            
            if self.scheduler_manager:
                self.scheduler_manager.scheduler_status_changed.connect(
                    lambda status: self.scheduler_status_label.setText(f"状态: {status}")
                )
            
            if self.workcoord_manager:
                self.workcoord_manager.workcoord_status_changed.connect(
                    lambda status: self.status_updated.emit(f"工作坐标: {status}")
                )
            
            if self.maintenance_manager:
                self.maintenance_manager.maintenance_status_changed.connect(
                    lambda status: self.status_updated.emit(f"维护: {status}")
                )
            
            if self.fileio_manager:
                self.fileio_manager.fileio_status_changed.connect(
                    lambda status: self.status_updated.emit(f"文件传输: {status}")
                )
            
            if self.device_manager:
                self.device_manager.device_discovered.connect(
                    self.add_device_to_table
                )
                self.device_manager.device_status_changed.connect(
                    self.update_device_status
                )
                self.device_manager.network_status_changed.connect(
                    lambda status: self.status_updated.emit(f"设备网络: {status}")
                )
            
            # 连接UI控件信号
            self.connect_ui_signals()
            
            self.status_updated.emit("所有信号连接完成")
            
        except Exception as e:
            self.error_occurred.emit(f"信号连接失败: {str(e)}")
    
    def connect_ui_signals(self):
        """连接UI控件信号"""
        # Primitive控件信号
        self.primitive_category_combo.currentTextChanged.connect(
            self.update_primitive_list
        )
        self.execute_primitive_btn.clicked.connect(self.execute_primitive)
        self.stop_primitive_btn.clicked.connect(self.stop_primitive)
        
        # Safety控件信号
        self.enable_safety_btn.clicked.connect(self.enable_safety)
        self.disable_safety_btn.clicked.connect(self.disable_safety)
        self.emergency_stop_btn.clicked.connect(self.emergency_stop)
        
        # Scheduler控件信号
        self.add_task_btn.clicked.connect(self.add_task)
        self.remove_task_btn.clicked.connect(self.remove_task)
        self.start_scheduler_btn.clicked.connect(self.start_scheduler)
        self.stop_scheduler_btn.clicked.connect(self.stop_scheduler)
        
        # WorkCoord控件信号
        self.add_coord_btn.clicked.connect(self.add_coordinate_system)
        self.calibrate_coord_btn.clicked.connect(self.calibrate_coordinate_system)
        
        # Maintenance控件信号
        self.run_diagnostic_btn.clicked.connect(self.run_diagnostic)
        self.run_calibration_btn.clicked.connect(self.run_calibration)
        
        # FileIO控件信号
        self.upload_btn.clicked.connect(self.upload_file)
        self.download_btn.clicked.connect(self.download_file)
        
        # Device控件信号
        self.discover_devices_btn.clicked.connect(self.discover_devices)
        self.refresh_devices_btn.clicked.connect(self.refresh_devices)
    
    # Primitive相关方法
    def update_primitive_list(self, category: str):
        """更新原语列表"""
        self.primitive_name_combo.clear()
        
        # 根据类别添加相应的原语
        primitive_map = {
            "运动控制": ["Home", "MoveJ", "MoveL", "MoveC", "Stop"],
            "工作流": ["Plan", "Loop", "If", "Wait", "SetVar"],
            "基础力控制": ["ZeroFTSensor", "SetForceMode", "ForceMove"],
            "高级力控制": ["Compliance", "Impedance", "AdmittanceControl"],
            "自适应装配": ["SpiralSearch", "PegInHole", "SnapFit"],
            "表面处理": ["SurfaceFollow", "Polishing", "Grinding"],
            "柔性搬运": ["GentleMove", "FlexibleGrasp", "AdaptivePlace"],
            "自适应抓取": ["AutoGrasp", "ForceGrasp", "VisionGrasp"],
            "零重力浮动": ["FloatingMode", "GravityComp", "TeachMode"],
            "康复理疗": ["PassiveMove", "AssistedMove", "ResistanceMove"],
            "视觉伺服": ["VisualServo", "EyeInHand", "EyeToHand"],
            "展示应用": ["Demo1", "Demo2", "Demo3"]
        }
        
        primitives = primitive_map.get(category, [])
        self.primitive_name_combo.addItems(primitives)
    
    def execute_primitive(self):
        """执行原语"""
        try:
            primitive_name = self.primitive_name_combo.currentText()
            if not primitive_name:
                return
            
            # 获取参数（简化实现）
            params = {}
            
            if self.primitive_manager:
                success = self.primitive_manager.execute_primitive(primitive_name, params)
                if success:
                    self.execute_primitive_btn.setEnabled(False)
                    self.stop_primitive_btn.setEnabled(True)
                    self.status_updated.emit(f"开始执行原语: {primitive_name}")
                else:
                    self.error_occurred.emit(f"执行原语失败: {primitive_name}")
            
        except Exception as e:
            self.error_occurred.emit(f"执行原语错误: {str(e)}")
    
    def stop_primitive(self):
        """停止原语"""
        try:
            if self.primitive_manager:
                self.primitive_manager.stop_current_primitive()
                self.execute_primitive_btn.setEnabled(True)
                self.stop_primitive_btn.setEnabled(False)
                self.status_updated.emit("原语已停止")
                
        except Exception as e:
            self.error_occurred.emit(f"停止原语错误: {str(e)}")
    
    # Safety相关方法
    def update_safety_status(self, status_dict: Dict[str, Any]):
        """更新安全状态"""
        for key, value in status_dict.items():
            if key in self.safety_status_labels:
                label = self.safety_status_labels[key]
                label.setText(str(value))
                
                # 根据状态设置颜色
                if value in ["正常", "安全", "启用"]:
                    label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
                elif value in ["警告", "注意"]:
                    label.setStyleSheet("QLabel { color: orange; font-weight: bold; }")
                else:
                    label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
    
    def enable_safety(self):
        """启用安全系统"""
        try:
            if self.safety_manager:
                self.safety_manager.enable_safety_system()
                self.status_updated.emit("安全系统已启用")
        except Exception as e:
            self.error_occurred.emit(f"启用安全系统错误: {str(e)}")
    
    def disable_safety(self):
        """禁用安全系统"""
        try:
            if self.safety_manager:
                self.safety_manager.disable_safety_system()
                self.status_updated.emit("安全系统已禁用")
        except Exception as e:
            self.error_occurred.emit(f"禁用安全系统错误: {str(e)}")
    
    def emergency_stop(self):
        """紧急停止"""
        try:
            if self.safety_manager:
                self.safety_manager.emergency_stop()
                self.status_updated.emit("紧急停止已激活")
        except Exception as e:
            self.error_occurred.emit(f"紧急停止错误: {str(e)}")
    
    # Scheduler相关方法
    def add_task(self):
        """添加任务"""
        try:
            task_name = self.task_name_edit.text()
            task_type = self.task_type_combo.currentText()
            priority = self.task_priority_spin.value()
            params = self.task_params_edit.toPlainText()
            
            if not task_name:
                self.error_occurred.emit("请输入任务名称")
                return
            
            # 添加到任务列表
            item = QListWidgetItem(f"{task_name} ({task_type}) [优先级: {priority}]")
            self.task_list_widget.addItem(item)
            
            # 清空输入
            self.task_name_edit.clear()
            self.task_params_edit.clear()
            
            self.status_updated.emit(f"任务已添加: {task_name}")
            
        except Exception as e:
            self.error_occurred.emit(f"添加任务错误: {str(e)}")
    
    def remove_task(self):
        """删除任务"""
        try:
            current_item = self.task_list_widget.currentItem()
            if current_item:
                self.task_list_widget.takeItem(self.task_list_widget.row(current_item))
                self.status_updated.emit("任务已删除")
        except Exception as e:
            self.error_occurred.emit(f"删除任务错误: {str(e)}")
    
    def start_scheduler(self):
        """开始调度"""
        try:
            if self.scheduler_manager:
                self.scheduler_manager.start_scheduler()
                self.status_updated.emit("任务调度器已启动")
        except Exception as e:
            self.error_occurred.emit(f"启动调度器错误: {str(e)}")
    
    def stop_scheduler(self):
        """停止调度"""
        try:
            if self.scheduler_manager:
                self.scheduler_manager.stop_scheduler()
                self.status_updated.emit("任务调度器已停止")
        except Exception as e:
            self.error_occurred.emit(f"停止调度器错误: {str(e)}")
    
    # WorkCoord相关方法
    def add_coordinate_system(self):
        """添加坐标系"""
        try:
            name, ok = QInputDialog.getText(self, "添加坐标系", "坐标系名称:")
            if ok and name:
                # 添加到树形控件
                item = QTreeWidgetItem([name, "用户定义", "未标定", "新建坐标系"])
                self.coord_tree_widget.addTopLevelItem(item)
                self.status_updated.emit(f"坐标系已添加: {name}")
        except Exception as e:
            self.error_occurred.emit(f"添加坐标系错误: {str(e)}")
    
    def calibrate_coordinate_system(self):
        """标定坐标系"""
        try:
            current_item = self.coord_tree_widget.currentItem()
            if current_item:
                coord_name = current_item.text(0)
                # 这里应该启动标定流程
                self.status_updated.emit(f"开始标定坐标系: {coord_name}")
        except Exception as e:
            self.error_occurred.emit(f"标定坐标系错误: {str(e)}")
    
    # Maintenance相关方法
    def run_diagnostic(self):
        """运行诊断"""
        try:
            diagnostic_type = self.diagnostic_combo.currentText()
            if self.maintenance_manager:
                self.maintenance_manager.run_diagnostic_test(diagnostic_type)
                self.status_updated.emit(f"开始运行诊断: {diagnostic_type}")
        except Exception as e:
            self.error_occurred.emit(f"运行诊断错误: {str(e)}")
    
    def run_calibration(self):
        """运行校准"""
        try:
            calibration_type = self.calibration_combo.currentText()
            if self.maintenance_manager:
                self.maintenance_manager.start_calibration(calibration_type)
                self.status_updated.emit(f"开始校准: {calibration_type}")
        except Exception as e:
            self.error_occurred.emit(f"运行校准错误: {str(e)}")
    
    # FileIO相关方法
    def upload_file(self):
        """上传文件"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择上传文件")
            if file_path:
                if self.fileio_manager:
                    remote_path = f"/flexiv/uploads/{os.path.basename(file_path)}"
                    self.fileio_manager.upload_file(file_path, remote_path)
                    self.status_updated.emit(f"开始上传文件: {os.path.basename(file_path)}")
        except Exception as e:
            self.error_occurred.emit(f"上传文件错误: {str(e)}")
    
    def download_file(self):
        """下载文件"""
        try:
            # 这里应该从远程文件列表中选择文件
            self.status_updated.emit("下载功能待实现")
        except Exception as e:
            self.error_occurred.emit(f"下载文件错误: {str(e)}")
    
    # Device相关方法
    def discover_devices(self):
        """发现设备"""
        try:
            if self.device_manager:
                self.device_manager.discover_devices()
                self.status_updated.emit("开始发现设备...")
        except Exception as e:
            self.error_occurred.emit(f"发现设备错误: {str(e)}")
    
    def refresh_devices(self):
        """刷新设备列表"""
        try:
            self.device_table.setRowCount(0)
            self.discover_devices()
        except Exception as e:
            self.error_occurred.emit(f"刷新设备错误: {str(e)}")
    
    def add_device_to_table(self, device_info):
        """添加设备到表格"""
        try:
            row = self.device_table.rowCount()
            self.device_table.insertRow(row)
            
            self.device_table.setItem(row, 0, QTableWidgetItem(device_info.ip))
            self.device_table.setItem(row, 1, QTableWidgetItem(device_info.name))
            self.device_table.setItem(row, 2, QTableWidgetItem(device_info.model))
            self.device_table.setItem(row, 3, QTableWidgetItem(device_info.status.value))
            
            latency = f"{device_info.ping_latency:.1f}ms" if device_info.ping_latency else "--"
            self.device_table.setItem(row, 4, QTableWidgetItem(latency))
            
            # 操作按钮
            connect_btn = QPushButton("连接")
            connect_btn.clicked.connect(lambda: self.connect_device(device_info.ip))
            self.device_table.setCellWidget(row, 5, connect_btn)
            
        except Exception as e:
            self.error_occurred.emit(f"添加设备到表格错误: {str(e)}")
    
    def update_device_status(self, ip: str, status: str):
        """更新设备状态"""
        try:
            for row in range(self.device_table.rowCount()):
                if self.device_table.item(row, 0).text() == ip:
                    self.device_table.setItem(row, 3, QTableWidgetItem(status))
                    break
        except Exception as e:
            self.error_occurred.emit(f"更新设备状态错误: {str(e)}")
    
    def connect_device(self, ip: str):
        """连接设备"""
        try:
            if self.device_manager:
                success = self.device_manager.connect_device(ip)
                if success:
                    self.status_updated.emit(f"设备连接成功: {ip}")
                else:
                    self.error_occurred.emit(f"设备连接失败: {ip}")
        except Exception as e:
            self.error_occurred.emit(f"连接设备错误: {str(e)}")
    
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_label.setText(message)
        self.status_updated.emit(message)
    
    def show_error(self, message: str):
        """显示错误信息"""
        QMessageBox.critical(self, "错误", message)
        self.error_occurred.emit(message)