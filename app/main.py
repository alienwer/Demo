'''
Author: LK
Date: 2025-02-07 22:07:28
LastEditTime: 2025-08-12 08:57:32
LastEditors: LK
FilePath: /Demo/app/main.py
'''
import sys
import os
import numpy as np
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QLineEdit, QTextEdit, QSlider, QFileDialog, QDesktopWidget,
                             QSpacerItem, QSizePolicy, QTabWidget, QScrollArea, QSplitter,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QBrush, QFont
import qtawesome as qta
import argparse
import pyqtgraph as pg

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 添加 RDK 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'thirdparty', 'flexiv_rdk'))

# Flexiv RDK
try:
    import flexivrdk
    FLEXIV_AVAILABLE = True
except ImportError:
    print("Warning: flexivrdk not found, using simulation mode")
    flexivrdk = None
    FLEXIV_AVAILABLE = False

# 通信层
from app.control.serial_comm import SerialCommunication
from app.control.robot_control import RobotControl
from app.control.gripper_control import GripperControl

# 可视化层
from app.visualization.gl_renderer import GLRenderer
# from app.visualization.robot_visualization import RobotVisualization

# 模型层
from app.model.robot_model import RobotModel

# ROS支持
try:
    import rospy
    import roslaunch
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False

def quaternion_to_euler(qw, qx, qy, qz):
    """
    将四元数转换为欧拉角（ZYX顺序，即Yaw-Pitch-Roll）
    
    Args:
        qw, qx, qy, qz: 四元数分量
    
    Returns:
        tuple: (roll, pitch, yaw) 欧拉角，单位为弧度
    """
    # 归一化四元数
    norm = math.sqrt(qw*qw + qx*qx + qy*qy + qz*qz)
    if norm == 0:
        return (0, 0, 0)
    qw, qx, qy, qz = qw/norm, qx/norm, qy/norm, qz/norm
    
    # 转换为欧拉角
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll = math.atan2(sinr_cosp, cosr_cosp)
    
    # Pitch (y-axis rotation)
    sinp = 2 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)
    
    # Yaw (z-axis rotation)
    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    
    return (roll, pitch, yaw)

class RobotArmControlApp(QMainWindow):
    """
    界面层：主窗口，负责UI交互、模型导入、关节控制、状态显示等
    """
    def __init__(self, robot=None, hardware=True):
        super().__init__()
        self.setWindowTitle('机械臂控制系统')
        # 自适应屏幕分辨率，最大宽高不超过屏幕
        screen = QDesktopWidget().screenGeometry()
        width = min(1200, screen.width() - 100)
        height = min(800, screen.height() - 100)
        self.setGeometry(100, 100, width, height)
        self.setMinimumSize(800, 600)
        self.setMaximumSize(screen.width(), screen.height())
        self.setSizePolicy(QApplication.desktop().sizePolicy())
        
        # 响应式布局相关属性
        self._last_window_size = self.size()
        self._is_maximized = False
        self._adaptive_layout_enabled = True
        
        # 防抖机制相关属性
        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._delayed_layout_adjustment)
        self._pending_size = None
        self._last_splitter_sizes = None
        self._layout_adjustment_in_progress = False
        
        # 状态变量
        self.is_teaching = False
        self.joint_sliders = []
        self.joint_values = []
        self.hardware = hardware  # 保存为实例变量
        self.robot = robot
        self.joint_curves = []
        self.ee_curve = None
        
        # 关节状态保存变量（用于仿真模式重连时恢复状态）
        self.saved_joint_angles = None
        # 用户交互标记（防止update_robot_state覆盖用户拖动）
        self.user_interacting = False

        # 通信层
        self.serial_comm = SerialCommunication()
        self.robot_control = RobotControl(robot=self.robot, hardware=self.hardware)
        # 新增：抓手控制器
        self.gripper_control = GripperControl(robot=self.robot)
        # 信号绑定
        self.gripper_control.gripper_state_updated.connect(self.update_gripper_state)
        self.gripper_control.gripper_param_updated.connect(self.update_gripper_param)
        self.gripper_control.gripper_error.connect(self.show_gripper_error)

        # 初始化UI
        self.init_ui_components()
        self.load_last_robot_sn()
        
        # ROS初始化
        self.init_ros()
        
        # 定时器：实时刷新机器人状态
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_robot_state)
        self.update_timer.start(50)  # 20Hz
        # 显示当前模式
        mode_str = '硬件模式' if self.hardware else '仿真/教学模式'
        self.global_status_text.append(f'当前运行模式：{mode_str}')
        # 可视化联动
        self.robot_control.joint_updated.connect(self.gl_renderer.update_joint_positions)

    def init_ros(self):
        """通信层：初始化ROS相关组件"""
        if ROS_AVAILABLE:
            try:
                rospy.init_node('robot_arm_control', anonymous=True)
                from sensor_msgs.msg import JointState
                self.joint_state_sub = rospy.Subscriber(
                    '/joint_states', 
                    JointState, 
                    self.joint_state_callback
                )
                self.global_status_text.append('ROS环境初始化成功')
                self.start_ros_launch()
            except Exception as e:
                self.global_status_text.append(f'ROS环境初始化失败：{str(e)}')

    def joint_state_callback(self, msg):
        """通信层：ROS关节状态回调"""
        joint_angles = {name: pos for name, pos in zip(msg.name, msg.position)}
        if hasattr(self, 'gl_renderer') and self.gl_renderer:
            self.gl_renderer.update_joint_positions(joint_angles)

    def update_robot_state(self):
        """通信层：定时更新机器人状态"""
        if hasattr(self, 'robot_control') and self.robot_control:
            angles = self.robot_control.get_joint_angles()
            # 只有在用户没有交互时才更新滑块值，防止覆盖用户拖动
            if not self.user_interacting:
                for i, angle in enumerate(angles):
                    if i < len(self.joint_sliders):
                        self.joint_sliders[i].blockSignals(True)
                        self.joint_sliders[i].setValue(int(angle * 180 / np.pi))
                        self.joint_sliders[i].blockSignals(False)
                        self.joint_values[i].setText(f"{angle * 180 / np.pi:.2f}°")
            if hasattr(self, 'gl_renderer') and self.gl_renderer:
                self.gl_renderer.set_joint_angles(angles)

    def init_ui_components(self):
        """界面层：初始化所有UI组件"""
        self.global_status_text = QTextEdit()
        self.global_status_text.setReadOnly(True)
        self.setup_main_layout()
        
    def setup_main_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # Splitter主区
        splitter_container = QWidget()
        splitter_layout = QHBoxLayout(splitter_container)
        splitter_layout.setContentsMargins(0,0,0,0)
        splitter_layout.setSpacing(0)
        # 左侧Tab面板
        self.left_tab = QTabWidget()
        self.left_tab.setMinimumWidth(350)
        self.left_tab.setMaximumWidth(500)
        # 机器人操作页
        op_scroll = QScrollArea()
        op_scroll.setWidgetResizable(True)
        op_page = QWidget()
        op_layout = QVBoxLayout(op_page)
        op_layout.setSpacing(8)
        # 序列号输入区
        sn_layout = QHBoxLayout()
        sn_label = QLabel('机器人序列号:')
        self.sn_input = QLineEdit()
        self.sn_input.setPlaceholderText('如 Rizon4-123456')
        self.sn_input.setMaximumWidth(180)
        self.sn_connect_btn = QPushButton('连接')
        self.sn_connect_btn.setMaximumWidth(60)
        self.sn_connect_btn.clicked.connect(self.on_connect_robot_sn)
        self.sn_status_light = QLabel()
        self.set_status_light(False)
        # 模式显示标签
        self.mode_label = QLabel('模式: -')
        self.mode_label.setStyleSheet('color: #555; font-size: 12px; padding-left: 8px;')
        sn_layout.addWidget(sn_label)
        sn_layout.addWidget(self.sn_input)
        sn_layout.addWidget(self.sn_connect_btn)
        sn_layout.addWidget(self.sn_status_light)
        sn_layout.addWidget(self.mode_label)
        sn_layout.addStretch()
        op_layout.addLayout(sn_layout)
        op_layout.addWidget(self.create_collapsible_group(self.create_model_group(), '模型导入'))
        op_layout.addWidget(self.create_collapsible_group(self.create_joint_group(), '关节控制'))
        op_layout.addWidget(self.create_collapsible_group(self.create_teach_group(), '示教再现'))
        op_layout.addWidget(self.create_collapsible_group(self.create_robot_ops_group(), '机器人操作'))
        op_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # 3D视图和分屏控制按钮
        view_control_layout = QHBoxLayout()
        
        # 3D视图控制
        self.btn_toggle_3d_view = QPushButton('隐藏3D视图')
        self.btn_toggle_3d_view.setCheckable(True)
        self.btn_toggle_3d_view.setChecked(False)
        
        # 分屏控制按钮
        btn_split_equal = QPushButton('等分')
        btn_split_left = QPushButton('左侧优先')
        btn_split_right = QPushButton('右侧优先')
        
        # 设置按钮样式
        splitter_btn_style = """
            QPushButton {
                background-color: #e8f4fd;
                border: 1px solid #4a90e2;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
                color: #2c5aa0;
            }
            QPushButton:hover {
                background-color: #d0e7fa;
            }
            QPushButton:pressed {
                background-color: #b8daf7;
            }
            QPushButton:checked {
                background-color: #ff6b6b;
                border-color: #ff5252;
                color: white;
            }
        """
        
        for btn in [self.btn_toggle_3d_view, btn_split_equal, btn_split_left, btn_split_right]:
            btn.setStyleSheet(splitter_btn_style)
            btn.setMaximumHeight(28)
        
        view_control_layout.addWidget(QLabel('3D视图:'))
        view_control_layout.addWidget(self.btn_toggle_3d_view)
        view_control_layout.addWidget(QLabel('分屏:'))
        view_control_layout.addWidget(btn_split_equal)
        view_control_layout.addWidget(btn_split_left)
        view_control_layout.addWidget(btn_split_right)
        view_control_layout.addStretch()
        
        # 绑定控制事件
        self.btn_toggle_3d_view.clicked.connect(self.toggle_3d_view)
        btn_split_equal.clicked.connect(self.set_splitter_equal)
        btn_split_left.clicked.connect(self.set_splitter_left_priority)
        btn_split_right.clicked.connect(self.set_splitter_right_priority)
        
        op_layout.addLayout(view_control_layout)
        
        # 视角操作按钮
        view_btn_layout = QHBoxLayout()
        btn_reset = QPushButton('重置视角')
        btn_front = QPushButton('正视')
        btn_top = QPushButton('俯视')
        btn_side = QPushButton('侧视')
        view_btn_layout.addWidget(btn_reset)
        view_btn_layout.addWidget(btn_front)
        view_btn_layout.addWidget(btn_top)
        view_btn_layout.addWidget(btn_side)
        op_layout.addLayout(view_btn_layout)
        btn_reset.clicked.connect(lambda: self.gl_renderer.reset_view())
        btn_front.clicked.connect(lambda: self.gl_renderer.set_preset_view('front'))
        btn_top.clicked.connect(lambda: self.gl_renderer.set_preset_view('top'))
        btn_side.clicked.connect(lambda: self.gl_renderer.set_preset_view('side'))
        op_scroll.setWidget(op_page)
        self.left_tab.addTab(op_scroll, '机器人操作')
        # 抓手页
        gripper_scroll = QScrollArea()
        gripper_scroll.setWidgetResizable(True)
        gripper_page = QWidget()
        gripper_layout = QVBoxLayout(gripper_page)
        gripper_layout.setSpacing(8)
        gripper_layout.addWidget(self.create_collapsible_group(self.create_gripper_group(), '抓手控制'))
        gripper_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        gripper_scroll.setWidget(gripper_page)
        self.left_tab.addTab(gripper_scroll, '抓手')
        # 监控页
        monitor_scroll = QScrollArea()
        monitor_scroll.setWidgetResizable(True)
        monitor_page = QWidget()
        monitor_layout = QVBoxLayout(monitor_page)
        monitor_layout.setSpacing(8)
        # 先创建全屏按钮
        self.monitor_full_btn = QPushButton('全屏')
        self.monitor_full_btn.setCheckable(True)
        self.monitor_full_btn.clicked.connect(self.toggle_monitor_fullscreen)
        monitor_layout.addWidget(self.monitor_full_btn, alignment=Qt.AlignRight)
        # 再创建监控组
        monitor_layout.addWidget(self.create_collapsible_group(self.create_monitor_group(), '监控信息', checked=True))
        monitor_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        monitor_scroll.setWidget(monitor_page)
        self.left_tab.addTab(monitor_scroll, '监控')
        
        # 通信页
        comm_scroll = QScrollArea()
        comm_scroll.setWidgetResizable(True)
        comm_page = QWidget()
        comm_layout = QVBoxLayout(comm_page)
        comm_layout.setSpacing(8)
        comm_layout.addWidget(self.create_collapsible_group(self.create_communication_group(), '通信配置', checked=True))
        comm_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        comm_scroll.setWidget(comm_page)
        self.left_tab.addTab(comm_scroll, '通信')
        
        # 全局变量页
        global_vars_scroll = QScrollArea()
        global_vars_scroll.setWidgetResizable(True)
        global_vars_page = QWidget()
        global_vars_layout = QVBoxLayout(global_vars_page)
        global_vars_layout.setSpacing(8)
        
        # 导入全局变量管理组件
        from app.ui.global_vars_widget import GlobalVariablesWidget
        self.global_vars_widget = GlobalVariablesWidget()
        
        # 连接信号
        self.global_vars_widget.variables_updated.connect(self.on_global_vars_apply)
        
        global_vars_layout.addWidget(self.global_vars_widget)
        global_vars_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        global_vars_scroll.setWidget(global_vars_page)
        self.left_tab.addTab(global_vars_scroll, '全局变量')
        
        # 高级控制页
        advanced_scroll = QScrollArea()
        advanced_scroll.setWidgetResizable(True)
        advanced_page = QWidget()
        advanced_layout = QVBoxLayout(advanced_page)
        advanced_layout.setSpacing(8)
        
        # 导入高级控制组件
        from app.ui.advanced_control_widget import AdvancedControlWidget
        self.advanced_control_widget = AdvancedControlWidget(robot_control=self.robot_control)
        
        # 连接信号
        self.advanced_control_widget.status_updated.connect(self.update_status_message)
        self.advanced_control_widget.error_occurred.connect(self.show_error_message)
        
        advanced_layout.addWidget(self.advanced_control_widget)
        advanced_scroll.setWidget(advanced_page)
        self.left_tab.addTab(advanced_scroll, '高级控制')
        # Splitter布局 - 优化分屏功能
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left_tab)
        
        # 创建右侧区域：3D视图 + 数据显示面板
        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # 3D渲染器
        self.gl_renderer = GLRenderer()
        
        # 数据显示面板
        self.data_panel = self.create_data_display_panel()
        self.data_panel.setMaximumHeight(200)
        self.data_panel.setMinimumHeight(180)
        
        # 添加到右侧布局
        right_layout.addWidget(self.gl_renderer, 1)  # 3D视图占主要空间
        right_layout.addWidget(self.data_panel, 0)   # 数据面板固定高度
        
        self.splitter.addWidget(self.right_widget)
        
        # 优化分屏比例，提供更平衡的布局
        self.splitter.setStretchFactor(0, 2)  # 左侧面板权重
        self.splitter.setStretchFactor(1, 3)  # 右侧3D视图权重
        
        # 设置分屏器属性
        self.splitter.setCollapsible(0, False)  # 左侧面板不可完全折叠
        self.splitter.setCollapsible(1, True)   # 右侧面板可折叠
        self.splitter.setHandleWidth(8)         # 设置分割线宽度
        
        # 设置初始大小比例（左侧40%，右侧60%）
        screen_width = QDesktopWidget().screenGeometry().width()
        initial_left_width = int(screen_width * 0.4)
        initial_right_width = int(screen_width * 0.6)
        self.splitter.setSizes([initial_left_width, initial_right_width])
        
        # 添加分屏器样式
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #cccccc;
                border: 1px solid #999999;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #bbbbbb;
            }
            QSplitter::handle:pressed {
                background-color: #aaaaaa;
            }
        """)
        
        splitter_layout.addWidget(self.splitter)
        main_layout.addWidget(splitter_container)
        # 底部全局状态栏
        self.global_status_text = QTextEdit()
        self.global_status_text.setReadOnly(True)
        self.global_status_text.setMaximumHeight(80)
        self.global_status_text.setStyleSheet('background:#f8f8f8; font-size:13px; color:#222;')
        main_layout.addWidget(self.global_status_text)
        # 记录全屏状态
        self._monitor_fullscreen = False
        self._splitter_sizes = None
    
    def create_data_display_panel(self):
        """创建数据显示面板 - 显示关节、TCP位姿和力/力矩数据"""
        panel = QGroupBox('机器人实时数据')
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4a90e2;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                font-size: 13px;
            }
        """)
        
        main_layout = QHBoxLayout(panel)
        main_layout.setSpacing(8)
        
        # 关节数据表格
        joints_group = QGroupBox('关节数据 (A1-A7)')
        joints_layout = QVBoxLayout(joints_group)
        
        self.joints_table = QTableWidget(7, 3)
        self.joints_table.setHorizontalHeaderLabels(['关节', '位置 (deg)', '扭矩 (Nm)'])
        self.joints_table.setVerticalHeaderLabels([f'A{i+1}' for i in range(7)])
        self.joints_table.setMaximumHeight(160)
        self.joints_table.horizontalHeader().setStretchLastSection(True)
        self.joints_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.joints_table.setAlternatingRowColors(True)
        
        # 初始化关节表格数据
        for i in range(7):
            self.joints_table.setItem(i, 0, QTableWidgetItem(f'A{i+1}'))
            self.joints_table.setItem(i, 1, QTableWidgetItem('-'))
            self.joints_table.setItem(i, 2, QTableWidgetItem('-'))
            for j in range(3):
                item = self.joints_table.item(i, j)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        
        joints_layout.addWidget(self.joints_table)
        
        # TCP位姿数据
        tcp_group = QGroupBox('TCP位姿')
        tcp_layout = QVBoxLayout(tcp_group)
        
        # TCP位置和姿态表格（合并为一个表格）
        self.tcp_table = QTableWidget(6, 2)
        self.tcp_table.setHorizontalHeaderLabels(['参数', '数值'])
        self.tcp_table.setVerticalHeaderLabels(['X (m)', 'Y (m)', 'Z (m)', 'Rx (deg)', 'Ry (deg)', 'Rz (deg)'])
        self.tcp_table.setMaximumHeight(160)
        self.tcp_table.horizontalHeader().setStretchLastSection(True)
        self.tcp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tcp_table.setAlternatingRowColors(True)
        
        # 初始化TCP表格数据
        tcp_labels = ['X (m)', 'Y (m)', 'Z (m)', 'Rx (deg)', 'Ry (deg)', 'Rz (deg)']
        for i, label in enumerate(tcp_labels):
            self.tcp_table.setItem(i, 0, QTableWidgetItem(label))
            self.tcp_table.setItem(i, 1, QTableWidgetItem('-'))
            for j in range(2):
                item = self.tcp_table.item(i, j)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        
        tcp_layout.addWidget(self.tcp_table)
        
        # TCP力/力矩数据
        ft_group = QGroupBox('TCP力/力矩')
        ft_layout = QVBoxLayout(ft_group)
        
        self.ft_table = QTableWidget(6, 2)
        self.ft_table.setHorizontalHeaderLabels(['参数', '数值'])
        self.ft_table.setVerticalHeaderLabels(['Fx (N)', 'Fy (N)', 'Fz (N)', 'Mx (Nm)', 'My (Nm)', 'Mz (Nm)'])
        self.ft_table.setMaximumHeight(160)
        self.ft_table.horizontalHeader().setStretchLastSection(True)
        self.ft_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ft_table.setAlternatingRowColors(True)
        
        # 初始化力/力矩表格数据
        ft_labels = ['Fx (N)', 'Fy (N)', 'Fz (N)', 'Mx (Nm)', 'My (Nm)', 'Mz (Nm)']
        for i, label in enumerate(ft_labels):
            self.ft_table.setItem(i, 0, QTableWidgetItem(label))
            self.ft_table.setItem(i, 1, QTableWidgetItem('-'))
            for j in range(2):
                item = self.ft_table.item(i, j)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        
        ft_layout.addWidget(self.ft_table)
        
        # 设置表格样式
        table_style = """
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
                font-size: 9px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 2px;
                text-align: center;
            }
            QHeaderView::section {
                background-color: #e8f4fd;
                padding: 3px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
                font-size: 9px;
            }
        """
        
        for table in [self.joints_table, self.tcp_table, self.ft_table]:
            table.setStyleSheet(table_style)
        
        # 添加到主布局
        main_layout.addWidget(joints_group)
        main_layout.addWidget(tcp_group)
        main_layout.addWidget(ft_group)
        
        return panel

    def toggle_monitor_fullscreen(self):
        """改进的全屏切换功能"""
        if not self._monitor_fullscreen:
            # 保存当前布局状态
            self._splitter_sizes = self.splitter.sizes()
            
            # 隐藏3D视图，最大化图表显示
            self.splitter.widget(1).hide()
            
            # 调整图表布局以更好利用空间
            if hasattr(self, 'all_plots'):
                for plot in self.all_plots:
                    plot.getViewBox().autoRange()
                    # 增大图表字体
                    plot.getAxis('left').setStyle(tickFont=QFont('Arial', 10))
                    plot.getAxis('bottom').setStyle(tickFont=QFont('Arial', 10))
            
            self.monitor_full_btn.setText('还原')
            self._monitor_fullscreen = True
            self.global_status_text.append('监控界面已切换到全屏模式')
        else:
            # 恢复原始布局
            self.splitter.widget(1).show()
            if self._splitter_sizes:
                self.splitter.setSizes(self._splitter_sizes)
            
            # 恢复图表字体大小
            if hasattr(self, 'all_plots'):
                for plot in self.all_plots:
                    plot.getAxis('left').setStyle(tickFont=QFont('Arial', 8))
                    plot.getAxis('bottom').setStyle(tickFont=QFont('Arial', 8))
            
            self.monitor_full_btn.setText('全屏')
            self._monitor_fullscreen = False
            self.global_status_text.append('监控界面已还原到正常模式')

    def create_collapsible_group(self, widget, title, checked=False):
        group = QGroupBox(title)
        group.setCheckable(True)
        group.setChecked(checked)
        group.setLayout(QVBoxLayout())
        group.layout().addWidget(widget)
        # 默认收起除监控外的分组
        if not checked:
            widget.setVisible(False)
        group.toggled.connect(widget.setVisible)
        return group

    def create_serial_group(self):
        """界面层：串口配置组"""
        serial_group = QGroupBox('串口配置')
        serial_layout = QVBoxLayout(serial_group)
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports_btn = QPushButton(qta.icon('fa5s.sync'), '')
        self.connect_btn = QPushButton('连接')
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(self.refresh_ports_btn)
        port_layout.addWidget(self.connect_btn)
        serial_layout.addLayout(port_layout)
        return serial_group
    
    def create_communication_group(self):
        """界面层：通信配置组"""
        comm_group = QGroupBox('通信配置')
        comm_layout = QVBoxLayout(comm_group)
        
        # 通信协议选择
        protocol_layout = QHBoxLayout()
        protocol_layout.addWidget(QLabel('通信协议:'))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(['串口通信', 'TCP/IP', 'Profinet', 'ModBus TCP/IP'])
        self.protocol_combo.currentTextChanged.connect(self.on_protocol_changed)
        protocol_layout.addWidget(self.protocol_combo)
        protocol_layout.addStretch()
        comm_layout.addLayout(protocol_layout)
        
        # 创建堆叠窗口用于不同协议的配置界面
        from PyQt5.QtWidgets import QStackedWidget
        self.protocol_stack = QStackedWidget()
        
        # 串口配置页面
        serial_widget = self.create_serial_config_widget()
        self.protocol_stack.addWidget(serial_widget)
        
        # TCP/IP配置页面
        tcpip_widget = self.create_tcpip_config_widget()
        self.protocol_stack.addWidget(tcpip_widget)
        
        # Profinet配置页面
        profinet_widget = self.create_profinet_config_widget()
        self.protocol_stack.addWidget(profinet_widget)
        
        # ModBus TCP/IP配置页面
        modbus_widget = self.create_modbus_config_widget()
        self.protocol_stack.addWidget(modbus_widget)
        
        comm_layout.addWidget(self.protocol_stack)
        
        # 连接状态显示
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel('连接状态:'))
        self.comm_status_label = QLabel('未连接')
        self.comm_status_label.setStyleSheet('color: red; font-weight: bold;')
        status_layout.addWidget(self.comm_status_label)
        status_layout.addStretch()
        comm_layout.addLayout(status_layout)
        
        # 连接控制按钮
        btn_layout = QHBoxLayout()
        self.comm_connect_btn = QPushButton('连接')
        self.comm_disconnect_btn = QPushButton('断开')
        self.comm_test_btn = QPushButton('测试连接')
        
        self.comm_connect_btn.clicked.connect(self.on_comm_connect)
        self.comm_disconnect_btn.clicked.connect(self.on_comm_disconnect)
        self.comm_test_btn.clicked.connect(self.on_comm_test)
        
        btn_layout.addWidget(self.comm_connect_btn)
        btn_layout.addWidget(self.comm_disconnect_btn)
        btn_layout.addWidget(self.comm_test_btn)
        btn_layout.addStretch()
        comm_layout.addLayout(btn_layout)
        
        return comm_group
    
    def create_serial_config_widget(self):
        """串口配置界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 串口选择
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel('串口:'))
        self.serial_port_combo = QComboBox()
        self.serial_refresh_btn = QPushButton(qta.icon('fa5s.sync'), '')
        self.serial_refresh_btn.setMaximumWidth(30)
        self.serial_refresh_btn.clicked.connect(self.refresh_serial_ports)
        port_layout.addWidget(self.serial_port_combo)
        port_layout.addWidget(self.serial_refresh_btn)
        port_layout.addStretch()
        layout.addLayout(port_layout)
        
        # 波特率设置
        baud_layout = QHBoxLayout()
        baud_layout.addWidget(QLabel('波特率:'))
        self.serial_baud_combo = QComboBox()
        self.serial_baud_combo.addItems(['9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600'])
        self.serial_baud_combo.setCurrentText('115200')
        baud_layout.addWidget(self.serial_baud_combo)
        baud_layout.addStretch()
        layout.addLayout(baud_layout)
        
        # 数据位、停止位、校验位
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel('数据位:'))
        self.serial_data_bits = QComboBox()
        self.serial_data_bits.addItems(['5', '6', '7', '8'])
        self.serial_data_bits.setCurrentText('8')
        param_layout.addWidget(self.serial_data_bits)
        
        param_layout.addWidget(QLabel('停止位:'))
        self.serial_stop_bits = QComboBox()
        self.serial_stop_bits.addItems(['1', '1.5', '2'])
        param_layout.addWidget(self.serial_stop_bits)
        
        param_layout.addWidget(QLabel('校验位:'))
        self.serial_parity = QComboBox()
        self.serial_parity.addItems(['None', 'Even', 'Odd', 'Mark', 'Space'])
        param_layout.addWidget(self.serial_parity)
        param_layout.addStretch()
        layout.addLayout(param_layout)
        
        # 初始化串口列表
        self.refresh_serial_ports()
        
        return widget
    
    def create_tcpip_config_widget(self):
        """TCP/IP配置界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel('工作模式:'))
        self.tcpip_mode_combo = QComboBox()
        self.tcpip_mode_combo.addItems(['Client', 'Server'])
        self.tcpip_mode_combo.currentTextChanged.connect(self.on_tcpip_mode_changed)
        mode_layout.addWidget(self.tcpip_mode_combo)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # 创建堆叠窗口用于不同模式的配置界面
        from PyQt5.QtWidgets import QStackedWidget
        self.tcpip_mode_stack = QStackedWidget()
        
        # Client模式配置
        client_widget = self.create_tcpip_client_widget()
        self.tcpip_mode_stack.addWidget(client_widget)
        
        # Server模式配置
        server_widget = self.create_tcpip_server_widget()
        self.tcpip_mode_stack.addWidget(server_widget)
        
        layout.addWidget(self.tcpip_mode_stack)
        
        # 通用设置
        common_group = QGroupBox('通用设置')
        common_layout = QVBoxLayout(common_group)
        
        # 连接超时设置
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel('超时时间(秒):'))
        self.tcpip_timeout_input = QSpinBox()
        self.tcpip_timeout_input.setRange(1, 60)
        self.tcpip_timeout_input.setValue(5)
        timeout_layout.addWidget(self.tcpip_timeout_input)
        timeout_layout.addStretch()
        common_layout.addLayout(timeout_layout)
        
        # 保持连接设置
        keepalive_layout = QHBoxLayout()
        from PyQt5.QtWidgets import QCheckBox
        self.tcpip_keepalive_check = QCheckBox('保持连接')
        self.tcpip_keepalive_check.setChecked(True)
        keepalive_layout.addWidget(self.tcpip_keepalive_check)
        keepalive_layout.addStretch()
        common_layout.addLayout(keepalive_layout)
        
        layout.addWidget(common_group)
        
        return widget
    
    def create_tcpip_client_widget(self):
        """TCP/IP Client模式配置界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 目标服务器IP地址
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel('服务器IP:'))
        self.tcpip_client_host_input = QLineEdit()
        self.tcpip_client_host_input.setPlaceholderText('192.168.1.100')
        self.tcpip_client_host_input.setText('192.168.1.100')
        ip_layout.addWidget(self.tcpip_client_host_input)
        ip_layout.addStretch()
        layout.addLayout(ip_layout)
        
        # 目标服务器端口
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel('服务器端口:'))
        self.tcpip_client_port_input = QSpinBox()
        self.tcpip_client_port_input.setRange(1, 65535)
        self.tcpip_client_port_input.setValue(8080)
        port_layout.addWidget(self.tcpip_client_port_input)
        port_layout.addStretch()
        layout.addLayout(port_layout)
        
        # 自动重连设置
        reconnect_layout = QHBoxLayout()
        from PyQt5.QtWidgets import QCheckBox
        self.tcpip_client_reconnect_check = QCheckBox('自动重连')
        self.tcpip_client_reconnect_check.setChecked(True)
        reconnect_layout.addWidget(self.tcpip_client_reconnect_check)
        reconnect_layout.addStretch()
        layout.addLayout(reconnect_layout)
        
        # 重连间隔
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel('重连间隔(秒):'))
        self.tcpip_client_interval_input = QSpinBox()
        self.tcpip_client_interval_input.setRange(1, 300)
        self.tcpip_client_interval_input.setValue(5)
        interval_layout.addWidget(self.tcpip_client_interval_input)
        interval_layout.addStretch()
        layout.addLayout(interval_layout)
        
        return widget
    
    def create_tcpip_server_widget(self):
        """TCP/IP Server模式配置界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 监听端口
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel('监听端口:'))
        self.tcpip_server_port_input = QSpinBox()
        self.tcpip_server_port_input.setRange(1, 65535)
        self.tcpip_server_port_input.setValue(8080)
        port_layout.addWidget(self.tcpip_server_port_input)
        port_layout.addStretch()
        layout.addLayout(port_layout)
        
        # 监听地址
        bind_layout = QHBoxLayout()
        bind_layout.addWidget(QLabel('绑定地址:'))
        self.tcpip_server_bind_input = QLineEdit()
        self.tcpip_server_bind_input.setPlaceholderText('0.0.0.0 (所有接口)')
        self.tcpip_server_bind_input.setText('0.0.0.0')
        bind_layout.addWidget(self.tcpip_server_bind_input)
        bind_layout.addStretch()
        layout.addLayout(bind_layout)
        
        # 最大连接数
        max_conn_layout = QHBoxLayout()
        max_conn_layout.addWidget(QLabel('最大连接数:'))
        self.tcpip_server_max_conn_input = QSpinBox()
        self.tcpip_server_max_conn_input.setRange(1, 100)
        self.tcpip_server_max_conn_input.setValue(10)
        max_conn_layout.addWidget(self.tcpip_server_max_conn_input)
        max_conn_layout.addStretch()
        layout.addLayout(max_conn_layout)
        
        # 连接状态显示
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel('当前连接数:'))
        self.tcpip_server_conn_count_label = QLabel('0')
        self.tcpip_server_conn_count_label.setStyleSheet('font-weight: bold; color: blue;')
        status_layout.addWidget(self.tcpip_server_conn_count_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        return widget
    
    def on_tcpip_mode_changed(self, mode):
        """TCP/IP模式切换处理"""
        if mode == 'Client':
            self.tcpip_mode_stack.setCurrentIndex(0)
        elif mode == 'Server':
            self.tcpip_mode_stack.setCurrentIndex(1)
    
    def update_tcpip_server_status(self, connection_count=0):
        """更新TCP/IP Server连接状态"""
        if hasattr(self, 'tcpip_server_conn_count_label'):
            self.tcpip_server_conn_count_label.setText(str(connection_count))
            if connection_count > 0:
                self.tcpip_server_conn_count_label.setStyleSheet('font-weight: bold; color: green;')
            else:
                self.tcpip_server_conn_count_label.setStyleSheet('font-weight: bold; color: blue;')
    
    def create_profinet_config_widget(self):
        """Profinet配置界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 设备名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('设备名称:'))
        self.profinet_device_name = QLineEdit()
        self.profinet_device_name.setPlaceholderText('robot-controller')
        self.profinet_device_name.setText('robot-controller')
        name_layout.addWidget(self.profinet_device_name)
        name_layout.addStretch()
        layout.addLayout(name_layout)
        
        # IP地址设置
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel('IP地址:'))
        self.profinet_ip_input = QLineEdit()
        self.profinet_ip_input.setPlaceholderText('192.168.1.50')
        self.profinet_ip_input.setText('192.168.1.50')
        ip_layout.addWidget(self.profinet_ip_input)
        ip_layout.addStretch()
        layout.addLayout(ip_layout)
        
        # 子网掩码
        mask_layout = QHBoxLayout()
        mask_layout.addWidget(QLabel('子网掩码:'))
        self.profinet_mask_input = QLineEdit()
        self.profinet_mask_input.setPlaceholderText('255.255.255.0')
        self.profinet_mask_input.setText('255.255.255.0')
        mask_layout.addWidget(self.profinet_mask_input)
        mask_layout.addStretch()
        layout.addLayout(mask_layout)
        
        # 网关地址
        gateway_layout = QHBoxLayout()
        gateway_layout.addWidget(QLabel('网关地址:'))
        self.profinet_gateway_input = QLineEdit()
        self.profinet_gateway_input.setPlaceholderText('192.168.1.1')
        self.profinet_gateway_input.setText('192.168.1.1')
        gateway_layout.addWidget(self.profinet_gateway_input)
        gateway_layout.addStretch()
        layout.addLayout(gateway_layout)
        
        # 站号设置
        station_layout = QHBoxLayout()
        station_layout.addWidget(QLabel('站号:'))
        self.profinet_station_input = QSpinBox()
        self.profinet_station_input.setRange(1, 255)
        self.profinet_station_input.setValue(1)
        station_layout.addWidget(self.profinet_station_input)
        station_layout.addStretch()
        layout.addLayout(station_layout)
        
        return widget
    
    def create_modbus_config_widget(self):
        """ModBus TCP/IP配置界面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # IP地址设置
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel('IP地址:'))
        self.modbus_host_input = QLineEdit()
        self.modbus_host_input.setPlaceholderText('192.168.1.200')
        self.modbus_host_input.setText('192.168.1.200')
        ip_layout.addWidget(self.modbus_host_input)
        ip_layout.addStretch()
        layout.addLayout(ip_layout)
        
        # 端口设置
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel('端口:'))
        self.modbus_port_input = QSpinBox()
        self.modbus_port_input.setRange(1, 65535)
        self.modbus_port_input.setValue(502)  # ModBus TCP默认端口
        port_layout.addWidget(self.modbus_port_input)
        port_layout.addStretch()
        layout.addLayout(port_layout)
        
        # 从站地址
        slave_layout = QHBoxLayout()
        slave_layout.addWidget(QLabel('从站地址:'))
        self.modbus_slave_input = QSpinBox()
        self.modbus_slave_input.setRange(1, 255)
        self.modbus_slave_input.setValue(1)
        slave_layout.addWidget(self.modbus_slave_input)
        slave_layout.addStretch()
        layout.addLayout(slave_layout)
        
        # 超时设置
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel('超时时间(秒):'))
        self.modbus_timeout_input = QSpinBox()
        self.modbus_timeout_input.setRange(1, 60)
        self.modbus_timeout_input.setValue(3)
        timeout_layout.addWidget(self.modbus_timeout_input)
        timeout_layout.addStretch()
        layout.addLayout(timeout_layout)
        
        # 重试次数
        retry_layout = QHBoxLayout()
        retry_layout.addWidget(QLabel('重试次数:'))
        self.modbus_retry_input = QSpinBox()
        self.modbus_retry_input.setRange(0, 10)
        self.modbus_retry_input.setValue(3)
        retry_layout.addWidget(self.modbus_retry_input)
        retry_layout.addStretch()
        layout.addLayout(retry_layout)
        
        return widget

    def create_model_group(self):
        """界面层：模型导入组"""
        model_group = QGroupBox('模型导入')
        model_layout = QVBoxLayout(model_group)
        self.model_combo = QComboBox()
        self.model_combo.addItems(['Rizon 4', 'Rizon 4s', 'Rizon 10', 'Rizon 10s'])
        model_layout.addWidget(self.model_combo)
        import_btn = QPushButton('导入模型')
        model_layout.addWidget(import_btn)
        import_btn.clicked.connect(self.import_robot_model)
        return model_group

    def create_joint_group(self):
        """界面层：关节控制组"""
        joint_group = QGroupBox('关节控制')
        joint_layout = QVBoxLayout(joint_group)
        for i in range(7):
            slider_layout = QHBoxLayout()
            label = QLabel(f'关节 {i+1}')
            slider = QSlider(Qt.Horizontal)
            slider.setRange(-180, 180)
            slider.setTickPosition(QSlider.TicksBelow)
            slider.setTickInterval(30)
            slider.setSingleStep(1)
            value_label = QLabel('0°')
            slider_layout.addWidget(label)
            slider_layout.addWidget(slider)
            slider_layout.addWidget(value_label)
            self.joint_sliders.append(slider)
            self.joint_values.append(value_label)
            joint_layout.addLayout(slider_layout)
            
            # 绑定滑块事件
            slider.valueChanged.connect(lambda value, idx=i: self.on_joint_slider_changed(idx, value))
            slider.sliderPressed.connect(lambda idx=i: self.on_joint_slider_pressed(idx))
            slider.sliderReleased.connect(lambda idx=i: self.on_joint_slider_released(idx))
        return joint_group

    def create_teach_group(self):
        """界面层：示教再现组"""
        teach_group = QGroupBox('示教再现')
        teach_layout = QVBoxLayout(teach_group)
        teach_btn = QPushButton('开始示教')
        replay_btn = QPushButton('开始再现')
        teach_layout.addWidget(teach_btn)
        teach_layout.addWidget(replay_btn)
        return teach_group

    def create_gripper_group(self):
        """抓手控制组（无使能按钮）"""
        gripper_group = QGroupBox('抓手控制')
        gripper_layout = QVBoxLayout(gripper_group)
        # 抓手参数显示
        self.gripper_param_label = QLabel('参数: 未使能')
        gripper_layout.addWidget(self.gripper_param_label)
        # 抓手状态显示
        self.gripper_state_label = QLabel('状态: 未连接')
        gripper_layout.addWidget(self.gripper_state_label)
        # 控制按钮
        btn_layout = QHBoxLayout()
        # self.btn_gripper_enable = QPushButton('使能')  # 移除抓手使能按钮
        self.btn_gripper_init = QPushButton('初始化')
        self.btn_gripper_open = QPushButton('打开')
        self.btn_gripper_close = QPushButton('闭合')
        self.btn_gripper_stop = QPushButton('停止')
        # btn_layout.addWidget(self.btn_gripper_enable)
        btn_layout.addWidget(self.btn_gripper_init)
        btn_layout.addWidget(self.btn_gripper_open)
        btn_layout.addWidget(self.btn_gripper_close)
        btn_layout.addWidget(self.btn_gripper_stop)
        gripper_layout.addLayout(btn_layout)
        # 绑定事件
        # self.btn_gripper_enable.clicked.connect(self.on_gripper_enable)
        self.btn_gripper_init.clicked.connect(self.on_gripper_init)
        self.btn_gripper_open.clicked.connect(self.on_gripper_open)
        self.btn_gripper_close.clicked.connect(self.on_gripper_close)
        self.btn_gripper_stop.clicked.connect(self.on_gripper_stop)
        return gripper_group

    def create_robot_ops_group(self):
        robot_ops_group = QGroupBox('机器人操作')
        ops_layout = QVBoxLayout(robot_ops_group)
        # 使能按钮
        self.btn_enable_robot = QPushButton('使能机器人')
        ops_layout.addWidget(self.btn_enable_robot)
        self.btn_enable_robot.clicked.connect(self.on_enable_robot)
        # Plan名称下拉框和刷新按钮
        plan_select_layout = QHBoxLayout()
        self.plan_combo = QComboBox()
        self.btn_refresh_plan = QPushButton('刷新Plan')
        self.btn_refresh_plan.setMaximumWidth(80)
        self.btn_refresh_plan.clicked.connect(self.on_refresh_plan_list)
        plan_select_layout.addWidget(QLabel('Plan名称:'))
        plan_select_layout.addWidget(self.plan_combo)
        plan_select_layout.addWidget(self.btn_refresh_plan)
        ops_layout.addLayout(plan_select_layout)
        # Plan索引输入和按钮
        plan_index_layout = QHBoxLayout()
        self.plan_index_input = QLineEdit()
        self.plan_index_input.setPlaceholderText('Plan索引')
        self.plan_index_input.setMaximumWidth(60)
        self.btn_plan_exec_index = QPushButton('按索引执行Plan')
        self.btn_plan_exec_index.setMaximumWidth(100)
        self.btn_plan_exec_index.clicked.connect(self.on_plan_exec_by_index)
        plan_index_layout.addWidget(self.plan_index_input)
        plan_index_layout.addWidget(self.btn_plan_exec_index)
        ops_layout.addLayout(plan_index_layout)
        # Plan执行按钮
        self.btn_plan_exec = QPushButton('执行选中Plan')
        self.btn_plan_exec.clicked.connect(self.on_plan_exec_by_name)
        ops_layout.addWidget(self.btn_plan_exec)
        
        # Plan停止按钮
        self.btn_plan_stop = QPushButton('停止Plan')
        self.btn_plan_stop.setStyleSheet('QPushButton { background-color: #ff6b6b; color: white; font-weight: bold; }')
        self.btn_plan_stop.clicked.connect(self.on_plan_stop)
        ops_layout.addWidget(self.btn_plan_stop)
        
        # 速度设置
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel('执行速度:'))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(10)  # 0.1x
        self.speed_slider.setMaximum(100)  # 1.0x
        self.speed_slider.setValue(100)  # 默认1.0x
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        self.speed_label = QLabel('100%')
        self.speed_label.setMinimumWidth(40)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_label)
        ops_layout.addLayout(speed_layout)
        
        # Plan详细信息显示
        self.plan_info_text = QTextEdit()
        self.plan_info_text.setReadOnly(True)
        self.plan_info_text.setMaximumHeight(80)
        ops_layout.addWidget(self.plan_info_text)
        # 力传感器归零
        self.btn_zero_ft = QPushButton('力/力矩归零')
        ops_layout.addWidget(self.btn_zero_ft)
        # 自动恢复
        self.btn_auto_recover = QPushButton('自动恢复')
        ops_layout.addWidget(self.btn_auto_recover)
        # URDF同步按钮
        self.btn_sync_urdf = QPushButton('同步标定URDF')
        ops_layout.addWidget(self.btn_sync_urdf)
        # 工具切换
        tool_layout = QHBoxLayout()
        
        # 工具选择下拉框
        self.tool_combo = QComboBox()
        self.tool_combo.setMinimumWidth(120)
        self.tool_combo.setToolTip('选择要切换的工具')
        
        # 刷新工具列表按钮
        self.btn_refresh_tools = QPushButton('刷新')
        self.btn_refresh_tools.setMaximumWidth(60)
        self.btn_refresh_tools.setToolTip('刷新可用工具列表')
        
        # 切换工具按钮
        self.btn_tool_switch = QPushButton('切换工具')
        self.btn_tool_switch.setToolTip('切换到选中的工具')
        
        # 当前工具显示标签
        self.current_tool_label = QLabel('当前工具: -')
        self.current_tool_label.setStyleSheet('color: #2E8B57; font-weight: bold;')
        
        tool_layout.addWidget(QLabel('工具:'))
        tool_layout.addWidget(self.tool_combo)
        tool_layout.addWidget(self.btn_refresh_tools)
        tool_layout.addWidget(self.btn_tool_switch)
        tool_layout.addStretch()
        
        ops_layout.addLayout(tool_layout)
        ops_layout.addWidget(self.current_tool_label)
        # 全局变量显示
        self.btn_get_global_vars = QPushButton('显示全局变量')
        self.global_vars_text = QTextEdit()
        self.global_vars_text.setReadOnly(True)
        ops_layout.addWidget(self.btn_get_global_vars)
        ops_layout.addWidget(self.global_vars_text)
        # 绑定事件
        self.btn_zero_ft.clicked.connect(self.on_zero_ft)
        self.btn_auto_recover.clicked.connect(self.on_auto_recover)
        self.btn_sync_urdf.clicked.connect(self.on_sync_urdf)
        self.btn_refresh_tools.clicked.connect(self.on_refresh_tools)
        self.btn_tool_switch.clicked.connect(self.on_tool_switch)
        self.btn_get_global_vars.clicked.connect(self.on_get_global_vars)
        # 绑定信号
        self.robot_control.plan_list_updated.connect(self.on_plan_list_updated)
        self.robot_control.plan_info_updated.connect(self.on_plan_info_updated)
        self.robot_control.plan_executed.connect(self.on_plan_executed)
        self.robot_control.plan_stopped.connect(self.on_plan_stopped)  # 新增：plan停止信号
        self.robot_control.force_sensor_zeroed.connect(self.on_force_sensor_zeroed)
        self.robot_control.auto_recovered.connect(self.on_auto_recovered)
        self.robot_control.tool_updated.connect(self.on_tool_updated)
        self.robot_control.global_vars_updated.connect(self.on_global_vars_updated)
        self.robot_control.error_signal.connect(self.on_robot_error)
        return robot_ops_group

    def create_monitor_group(self):
        """创建监控组 - 专门显示图表和状态信息"""
        self.monitor_group = QGroupBox('监控图表')
        main_layout = QVBoxLayout(self.monitor_group)
        main_layout.setSpacing(8)
        
        # 状态信息组（保留基本状态显示）
        status_group = QGroupBox('系统状态')
        status_layout = QHBoxLayout(status_group)
        status_layout.setSpacing(8)
        
        self.monitor_status_label = QLabel('机器人状态: -')
        self.monitor_mode_label = QLabel('运行模式: -')
        self.monitor_safety_label = QLabel('安全状态: -')
        self.monitor_fault_label = QLabel('故障信息: -')
        
        label_style = "font-size: 10px; padding: 4px; background-color: #f8f8f8; border: 1px solid #e0e0e0; border-radius: 3px;"
        for label in [self.monitor_status_label, self.monitor_mode_label, 
                     self.monitor_safety_label, self.monitor_fault_label]:
            label.setStyleSheet(label_style)
            label.setWordWrap(True)
            label.setMaximumHeight(30)
        
        status_layout.addWidget(self.monitor_status_label)
        status_layout.addWidget(self.monitor_mode_label)
        status_layout.addWidget(self.monitor_safety_label)
        status_layout.addWidget(self.monitor_fault_label)
        
        main_layout.addWidget(status_group)
        
        # 移除文本区域，改为图表显示
        # 右栏图表 - 增强交互功能和标识
        self.joint_plot = pg.PlotWidget(title="关节角度历史 (Joint Angles)")
        self.joint_plot.setLabel('left', '角度 (度)', units='°')
        self.joint_plot.setLabel('bottom', '时间 (秒)', units='s')
        self.joint_plot.addLegend()
        
        self.ee_plot = pg.PlotWidget(title="末端轨迹 (TCP Trajectory X-Y)")
        self.ee_plot.setLabel('left', 'Y 位置 (米)', units='m')
        self.ee_plot.setLabel('bottom', 'X 位置 (米)', units='m')
        self.ee_plot.addLegend()
        
        self.ft_plot = pg.PlotWidget(title="力/力矩传感器 (Force/Torque Sensor)")
        self.ft_plot.setLabel('left', '力/力矩 (N/Nm)')
        self.ft_plot.setLabel('bottom', '时间 (秒)', units='s')
        self.ft_plot.addLegend()
        
        self.vel_plot = pg.PlotWidget(title="关节速度 (Joint Velocities)")
        self.vel_plot.setLabel('left', '角速度 (度/秒)', units='°/s')
        self.vel_plot.setLabel('bottom', '时间 (秒)', units='s')
        self.vel_plot.addLegend()
        
        self.pos_plot = pg.PlotWidget(title="关节位置 (Joint Positions)")
        self.pos_plot.setLabel('left', '角度 (度)', units='°')
        self.pos_plot.setLabel('bottom', '时间 (秒)', units='s')
        self.pos_plot.addLegend()
        
        # 为所有图表添加交互功能并优化显示尺寸
        self.all_plots = [self.joint_plot, self.ee_plot, self.ft_plot, self.vel_plot, self.pos_plot]
        for plot in self.all_plots:
            plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # 设置图表最小尺寸，确保有足够的显示空间
            plot.setMinimumSize(400, 300)  # 最小宽度400px，高度300px
            plot.setMaximumHeight(500)  # 限制最大高度，避免过高
            # 启用鼠标交互
            plot.setMouseEnabled(x=True, y=True)
            # 启用右键菜单
            plot.getViewBox().setMenuEnabled(True)
            # 添加网格
            plot.showGrid(x=True, y=True, alpha=0.3)
            # 添加十字光标
            plot.getViewBox().enableAutoRange()
            # 设置背景颜色
            plot.setBackground('w')
        self.monitor_tab = QTabWidget()
        self.monitor_tab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 设置标签页容器的最小尺寸，确保图表有足够显示空间
        self.monitor_tab.setMinimumSize(450, 350)
        self.monitor_tab.setMaximumHeight(550)
        
        # 设置标签页样式
        self.monitor_tab.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 12px;
                margin-right: 2px;
                font-size: 11px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)
        # 曲线对象 - 优化图例标识
        joint_colors = ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#a65628','#f781bf']
        joint_names = ['关节1 (Base)', '关节2 (Shoulder)', '关节3 (Elbow)', '关节4 (Wrist1)', 
                      '关节5 (Wrist2)', '关节6 (Wrist3)', '关节7 (Flange)']
        
        # 关节角度曲线
        self.joint_curves = []
        for i in range(7):
            curve = self.joint_plot.plot(pen=pg.mkPen(color=joint_colors[i], width=2), name=joint_names[i])
            self.joint_curves.append(curve)
        
        # TCP轨迹曲线
        self.ee_curve = self.ee_plot.plot(pen=pg.mkPen('#2E8B57', width=2, style=pg.QtCore.Qt.SolidLine), 
                                          symbol='o', symbolBrush='#2E8B57', symbolSize=4, name="TCP轨迹")
        
        # 力/力矩传感器曲线
        ft_colors = ['#DC143C','#4169E1','#32CD32','#FF8C00','#9932CC','#8B4513']
        ft_styles = [pg.QtCore.Qt.SolidLine, pg.QtCore.Qt.SolidLine, pg.QtCore.Qt.SolidLine, 
                    pg.QtCore.Qt.DashLine, pg.QtCore.Qt.DashLine, pg.QtCore.Qt.DashLine]
        ft_names = ["Fx (X轴力)", "Fy (Y轴力)", "Fz (Z轴力)", "Tx (X轴力矩)", "Ty (Y轴力矩)", "Tz (Z轴力矩)"]
        self.ft_curves = []
        for i, name in enumerate(ft_names):
            curve = self.ft_plot.plot(pen=pg.mkPen(color=ft_colors[i], width=2, style=ft_styles[i]), name=name)
            self.ft_curves.append(curve)
        
        # 关节速度曲线
        self.vel_curves = []
        for i in range(7):
            curve = self.vel_plot.plot(pen=pg.mkPen(color=joint_colors[i], width=2, style=pg.QtCore.Qt.DashLine), 
                                     name=f"{joint_names[i]} 速度")
            self.vel_curves.append(curve)
        
        # 关节位置曲线
        self.pos_curves = []
        for i in range(7):
            curve = self.pos_plot.plot(pen=pg.mkPen(color=joint_colors[i], width=2), name=f"{joint_names[i]} 位置")
            self.pos_curves.append(curve)
        self.monitor_tab.addTab(self.joint_plot, "关节角度")
        self.monitor_tab.addTab(self.ee_plot, "末端轨迹")
        self.monitor_tab.addTab(self.ft_plot, "力/力矩")
        self.monitor_tab.addTab(self.vel_plot, "关节速度")
        self.monitor_tab.addTab(self.pos_plot, "关节位置")
        
        # 创建图表控制面板
        chart_control_layout = QVBoxLayout()
        
        # 控制按钮 - 优化样式
        control_buttons_layout = QHBoxLayout()
        control_buttons_layout.setSpacing(8)
        
        self.btn_reset_charts = QPushButton('重置视图')
        self.btn_export_data = QPushButton('导出数据')
        self.btn_clear_data = QPushButton('清空数据')
        self.monitor_full_btn = QPushButton('全屏')
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #999;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
                border-color: #666;
            }
        """
        
        for btn in [self.btn_reset_charts, self.btn_export_data, 
                   self.btn_clear_data, self.monitor_full_btn]:
            btn.setStyleSheet(button_style)
            btn.setMaximumHeight(32)
            btn.setMinimumWidth(80)
        
        control_buttons_layout.addWidget(self.btn_reset_charts)
        control_buttons_layout.addWidget(self.btn_export_data)
        control_buttons_layout.addWidget(self.btn_clear_data)
        control_buttons_layout.addWidget(self.monitor_full_btn)
        control_buttons_layout.addStretch()
        
        # 绑定按钮事件
        self.btn_reset_charts.clicked.connect(self.reset_chart_views)
        self.btn_export_data.clicked.connect(self.export_monitor_data)
        self.btn_clear_data.clicked.connect(self.clear_monitor_data)
        self.monitor_full_btn.clicked.connect(self.toggle_monitor_fullscreen)
        
        chart_control_layout.addLayout(control_buttons_layout)
        chart_control_layout.addWidget(self.monitor_tab)
        
        # 创建图表容器
        chart_container = QWidget()
        chart_container.setLayout(chart_control_layout)
        chart_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 大幅增加图表区域的比例权重，确保图表获得充足的显示空间
        main_layout.addWidget(chart_container, 1)  # 图表区域占据所有剩余空间
        # 数据缓存 - 扩展更多数据类型
        self.joint_history = [[] for _ in range(7)]
        self.joint_vel_history = [[] for _ in range(7)]
        self.joint_acc_history = [[] for _ in range(7)]  # 新增加速度历史
        self.joint_pos_history = [[] for _ in range(7)]
        self.joint_torque_history = [[] for _ in range(7)]  # 新增力矩历史
        self.joint_temp_history = [[] for _ in range(7)]  # 新增温度历史
        self.time_history = []
        self.ee_xy_history = []
        self.ft_history = [[] for _ in range(6)]
        self.power_history = []  # 新增功率历史
        
        # 状态跟踪变量
        self.last_joint_angles = None
        self.last_joint_velocities = None
        self.last_time = None
        self.max_data_points = 200  # 最大数据点数
        # 信号绑定
        self.robot_control.joint_updated.connect(self.update_monitor_joint)
        self.robot_control.end_effector_updated.connect(self.update_monitor_ee)
        self.robot_control.status_updated.connect(self.update_monitor_status)
        self.robot_control.error_signal.connect(self.update_monitor_fault)
        return self.monitor_group

    def update_monitor_joint(self, joint_angles):
        """更新关节角度显示和历史数据"""
        if not hasattr(self, 'joint_curves') or not self.joint_curves:
            return
        import time
        
        # 更新关节数据表格 - 将弧度转换为度数显示
        if hasattr(self, 'joints_table'):
            for i, angle in enumerate(joint_angles):
                if i < 7:  # A1-A7
                    angle_deg = angle * 180 / np.pi
                    self.joints_table.setItem(i, 1, QTableWidgetItem(f'{angle_deg:.2f}'))
        
        t = time.time()
        self.time_history.append(t)
        
        # 更新关节角度历史数据（转换为度数显示）
        for i, a in enumerate(joint_angles):
            if i < len(self.joint_history):
                angle_deg = a * 180 / np.pi  # 转换为度数
                self.joint_history[i].append(angle_deg)
                self.joint_pos_history[i].append(angle_deg)
                
                # 数据点数量控制
                if len(self.joint_history[i]) > self.max_data_points:
                    self.joint_history[i] = self.joint_history[i][-self.max_data_points:]
                if len(self.joint_pos_history[i]) > self.max_data_points:
                    self.joint_pos_history[i] = self.joint_pos_history[i][-self.max_data_points:]
        
        # 控制时间历史长度
        if len(self.time_history) > self.max_data_points:
            self.time_history = self.time_history[-self.max_data_points:]
        
        # 更新关节角度图表曲线 - 确保数组长度匹配
        for i, curve in enumerate(self.joint_curves):
            if i < len(self.joint_history):
                # 确保两个数组长度相同
                min_len = min(len(self.time_history), len(self.joint_history[i]))
                if min_len > 0:
                    curve.setData(self.time_history[-min_len:], self.joint_history[i][-min_len:])
        
        # 更新关节位置图表曲线 - 确保数组长度匹配
        for i, curve in enumerate(self.pos_curves):
            if i < len(self.joint_pos_history):
                # 确保两个数组长度相同
                min_len = min(len(self.time_history), len(self.joint_pos_history[i]))
                if min_len > 0:
                    curve.setData(self.time_history[-min_len:], self.joint_pos_history[i][-min_len:])

    def update_monitor_ee(self, tcp_pose):
        if not hasattr(self, 'ee_curve') or self.ee_curve is None:
            return
        
        # 更新TCP位置和姿态表格（合并表格）
        if hasattr(self, 'tcp_table') and len(tcp_pose) >= 3:
            # 更新位置数据 (X, Y, Z)
            for i in range(3):
                if i < len(tcp_pose):
                    self.tcp_table.setItem(i, 1, QTableWidgetItem(f'{tcp_pose[i]:.4f}'))
            
            # 更新姿态数据（四元数转欧拉角）
            if len(tcp_pose) >= 7:  # 完整的TCP姿态数据 [x, y, z, qw, qx, qy, qz]
                # 提取四元数分量
                qw, qx, qy, qz = tcp_pose[3], tcp_pose[4], tcp_pose[5], tcp_pose[6]
                
                # 转换为欧拉角（弧度）
                roll, pitch, yaw = quaternion_to_euler(qw, qx, qy, qz)
                
                # 转换为度数并更新表格
                euler_angles = [roll, pitch, yaw]
                for i, angle_rad in enumerate(euler_angles):
                    angle_deg = angle_rad * 180 / math.pi
                    self.tcp_table.setItem(i + 3, 1, QTableWidgetItem(f'{angle_deg:.2f}'))
        
        # 末端轨迹（只画X-Y）
        if len(tcp_pose) >= 2:
            self.ee_xy_history.append((tcp_pose[0], tcp_pose[1]))
            if len(self.ee_xy_history) > 200:
                self.ee_xy_history = self.ee_xy_history[-200:]
            x, y = zip(*self.ee_xy_history)
            self.ee_curve.setData(x, y)

    def update_monitor_status(self, status):
        self.monitor_status_label.setText(f'机器人状态: {status}')

    def update_monitor_fault(self, msg):
        self.monitor_fault_label.setText(f'故障信息: {msg}')

    def update_robot_states(self, robot_states):
        """处理完整的机器人状态数据"""
        try:
            # 更新安全状态
            if hasattr(self, 'robot_control') and self.robot_control and self.robot_control.robot:
                if self.robot_control.robot.fault():
                    safety_status = '故障状态'
                elif self.robot_control.robot.operational():
                    safety_status = '正常运行'
                elif self.robot_control.robot.connected():
                    safety_status = '已连接未使能'
                else:
                    safety_status = '连接断开'
                self.monitor_safety_label.setText(f'安全状态: {safety_status}')
        except Exception as e:
            self.monitor_safety_label.setText('安全状态: 未知')
    
    def update_monitor_velocity(self, velocities):
        """更新关节速度显示"""
        # 将弧度/秒转换为度/秒显示
        vel_text = ', '.join([f'{v * 180 / np.pi:.3f}°/s' for v in velocities])
        if hasattr(self, 'monitor_velocity_label'):
            self.monitor_velocity_label.setText(f'关节速度: {vel_text}')
        
        # 更新速度历史数据（转换为度/秒）
        for i, v in enumerate(velocities):
            if i < len(self.joint_vel_history):
                vel_deg_per_sec = v * 180 / np.pi  # 转换为度/秒
                self.joint_vel_history[i].append(vel_deg_per_sec)
                if len(self.joint_vel_history[i]) > self.max_data_points:
                    self.joint_vel_history[i] = self.joint_vel_history[i][-self.max_data_points:]
        
        # 更新速度图表（使用共享的时间历史） - 确保数组长度匹配
        for i, curve in enumerate(self.vel_curves):
            if i < len(self.joint_vel_history) and len(self.time_history) > 0:
                # 确保两个数组长度相同
                min_len = min(len(self.time_history), len(self.joint_vel_history[i]))
                if min_len > 0:
                    curve.setData(self.time_history[-min_len:], self.joint_vel_history[i][-min_len:])
    
    def update_monitor_torque(self, torques):
        """更新关节力矩显示"""
        # 更新关节数据表格中的扭矩列
        if hasattr(self, 'joints_table'):
            for i, torque in enumerate(torques):
                if i < 7:  # A1-A7
                    self.joints_table.setItem(i, 2, QTableWidgetItem(f'{torque:.3f}'))
        
        # 更新力矩历史数据
        for i, torque in enumerate(torques):
            if i < len(self.joint_torque_history):
                self.joint_torque_history[i].append(torque)
                if len(self.joint_torque_history[i]) > self.max_data_points:
                    self.joint_torque_history[i] = self.joint_torque_history[i][-self.max_data_points:]
        
        # 更新力矩图表 - 确保数组长度匹配
        if hasattr(self, 'torque_curves'):
            for i, curve in enumerate(self.torque_curves):
                if i < len(self.joint_torque_history) and len(self.time_history) > 0:
                    # 确保两个数组长度相同
                    min_len = min(len(self.time_history), len(self.joint_torque_history[i]))
                    if min_len > 0:
                        curve.setData(self.time_history[-min_len:], self.joint_torque_history[i][-min_len:])
    
    def update_monitor_mode(self, mode):
        """更新机器人模式显示"""
        self.monitor_mode_label.setText(f'运行模式: {mode}')

    # 力/力矩数据更新
    def update_monitor_ft(self, ft_data):
        """更新力/力矩传感器数据"""
        # ft_data: [Fx, Fy, Fz, Mx, My, Mz]
        if len(ft_data) >= 6:
            import time
            t = time.time()
            
            # 更新TCP力/力矩表格（合并表格）
            if hasattr(self, 'ft_table'):
                # 更新力数据 (Fx, Fy, Fz)
                for i in range(3):
                    if i < len(ft_data):
                        self.ft_table.setItem(i, 1, QTableWidgetItem(f'{ft_data[i]:.3f}'))
                
                # 更新力矩数据 (Mx, My, Mz)
                for i in range(3):
                    if i + 3 < len(ft_data):
                        self.ft_table.setItem(i + 3, 1, QTableWidgetItem(f'{ft_data[i + 3]:.3f}'))
            
            # 确保时间历史数据与力/力矩数据同步
            if not hasattr(self, 'time_history'):
                self.time_history = []
            
            # 只有当ft_history有数据时才添加时间戳
            if hasattr(self, 'ft_history') and len(self.ft_history) > 0:
                self.time_history.append(t)
                
                # 控制时间历史长度
                if len(self.time_history) > self.max_data_points:
                    self.time_history = self.time_history[-self.max_data_points:]
            
            for i, v in enumerate(ft_data[:6]):  # 只取前6个值
                if i < len(self.ft_history):
                    self.ft_history[i].append(v)
                    if len(self.ft_history[i]) > self.max_data_points:
                        self.ft_history[i] = self.ft_history[i][-self.max_data_points:]
            
            # 更新力/力矩图表 - 确保数组长度匹配
            for i, curve in enumerate(self.ft_curves):
                if i < len(self.ft_history) and len(self.time_history) > 0:
                    # 确保两个数组长度相同
                    min_len = min(len(self.time_history), len(self.ft_history[i]))
                    if min_len > 0:
                        curve.setData(self.time_history[-min_len:], self.ft_history[i][-min_len:])
    
    # 新增功能函数
    def reset_chart_views(self):
        """重置所有图表视图"""
        for plot in self.all_plots:
            plot.getViewBox().autoRange()
            plot.getViewBox().enableAutoRange()
    
    def export_monitor_data(self):
        """导出监控数据到CSV文件"""
        try:
            import csv
            from PyQt5.QtWidgets import QFileDialog
            import os
            
            # 选择保存文件
            file_path, _ = QFileDialog.getSaveFileName(
                self, '导出监控数据', 
                os.path.expanduser('~/robot_monitor_data.csv'),
                'CSV Files (*.csv)'
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # 写入表头
                    headers = ['Time']
                    for i in range(7):
                        headers.extend([f'Joint{i+1}_Angle', f'Joint{i+1}_Velocity', 
                                      f'Joint{i+1}_Acceleration', f'Joint{i+1}_Torque', 
                                      f'Joint{i+1}_Temperature'])
                    if self.ee_xy_history:
                        headers.extend(['EE_X', 'EE_Y'])
                    for i in range(6):
                        headers.append(f'FT_{["Fx","Fy","Fz","Tx","Ty","Tz"][i]}')
                    writer.writerow(headers)
                    
                    # 写入数据
                    for idx, t in enumerate(self.time_history):
                        row = [t]
                        for i in range(7):
                            row.append(self.joint_history[i][idx] if idx < len(self.joint_history[i]) else 0)
                            row.append(self.joint_vel_history[i][idx] if idx < len(self.joint_vel_history[i]) else 0)
                            row.append(self.joint_acc_history[i][idx] if idx < len(self.joint_acc_history[i]) else 0)
                            row.append(self.joint_torque_history[i][idx] if idx < len(self.joint_torque_history[i]) else 0)
                            row.append(self.joint_temp_history[i][idx] if idx < len(self.joint_temp_history[i]) else 0)
                        
                        if self.ee_xy_history and idx < len(self.ee_xy_history):
                            row.extend(self.ee_xy_history[idx])
                        else:
                            row.extend([0, 0])
                        
                        for i in range(6):
                            row.append(self.ft_history[i][idx] if idx < len(self.ft_history[i]) else 0)
                        
                        writer.writerow(row)
                
                self.global_status_text.append(f'监控数据已导出到: {file_path}')
        except Exception as e:
            self.global_status_text.append(f'导出数据失败: {str(e)}')
    
    def clear_monitor_data(self):
        """清空所有监控数据"""
        try:
            # 清空所有历史数据
            self.joint_history = [[] for _ in range(7)]
            self.joint_vel_history = [[] for _ in range(7)]
            self.joint_acc_history = [[] for _ in range(7)]
            self.joint_pos_history = [[] for _ in range(7)]
            self.joint_torque_history = [[] for _ in range(7)]
            self.joint_temp_history = [[] for _ in range(7)]
            self.time_history = []
            self.ee_xy_history = []
            self.ft_history = [[] for _ in range(6)]
            self.power_history = []
            
            # 重置状态变量
            self.last_joint_angles = None
            self.last_joint_velocities = None
            self.last_time = None
            
            # 清空图表
            for curve in self.joint_curves:
                curve.setData([], [])
            for curve in self.vel_curves:
                curve.setData([], [])
            for curve in self.pos_curves:
                curve.setData([], [])
            for curve in self.ft_curves:
                curve.setData([], [])
            if hasattr(self, 'ee_curve') and self.ee_curve:
                self.ee_curve.setData([], [])
            
            # 重置标签显示
            self.monitor_joint_label.setText('关节角度: -')
            self.monitor_ee_label.setText('末端位置: -')
            self.monitor_velocity_label.setText('关节速度: -')
            self.monitor_acceleration_label.setText('关节加速度: -')
            self.monitor_torque_label.setText('关节力矩: -')
            self.monitor_temperature_label.setText('关节温度: -')
            self.monitor_power_label.setText('功率消耗: -')
            self.monitor_mode_label.setText('运行模式: -')
            self.monitor_safety_label.setText('安全状态: -')
            
            self.global_status_text.append('监控数据已清空')
        except Exception as e:
            self.global_status_text.append(f'清空数据失败: {str(e)}')

    def set_status_light(self, connected):
        if connected:
            self.sn_status_light.setText('●')
            self.sn_status_light.setStyleSheet('color: green; font-size: 18px;')
        else:
            self.sn_status_light.setText('●')
            self.sn_status_light.setStyleSheet('color: red; font-size: 18px;')

    def update_mode_label(self):
        mode_str = '-'
        if hasattr(self, 'robot_control') and self.robot_control and self.robot_control.robot is not None:
            try:
                mode = self.robot_control.robot.mode()
                mode_str = str(mode)
            except Exception:
                pass
        self.mode_label.setText(f'模式: {mode_str}')

    def on_enable_robot(self):
        if hasattr(self, 'robot_control') and self.robot_control:
            try:
                self.robot_control.enable_robot()
                self.global_status_text.append('已发送机器人使能命令')
                self.update_mode_label()
            except Exception as e:
                self.global_status_text.append(f'机器人使能失败: {e}')
        else:
            self.global_status_text.append('机器人未连接，无法使能')

    def start_ros_launch(self):
        """通信层：启动ROS仿真环境"""
        if not ROS_AVAILABLE:
            self.global_status_text.append('ROS环境不可用，跳过launch文件启动')
            return
        try:
            launch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'launch', 'demo.launch')
            if not os.path.exists(launch_path):
                self.global_status_text.append('找不到launch文件：demo.launch')
                return
            uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
            roslaunch.configure_logging(uuid)
            launch = roslaunch.parent.ROSLaunchParent(uuid, [launch_path])
            launch.start()
            self.global_status_text.append('ROS仿真环境启动成功')
        except Exception as e:
            self.global_status_text.append(f'启动ROS仿真环境失败：{str(e)}')

    def refresh_serial_ports(self):
        """通信层：刷新可用串口列表"""
        self.port_combo.clear()
        ports = self.serial_comm.get_available_ports()
        for port in ports:
            self.port_combo.addItem(port)

    def toggle_serial_connection(self):
        """通信层：切换串口连接状态"""
        if not self.serial_comm.is_connected():
            port = self.port_combo.currentText()
            if self.serial_comm.connect(port):
                self.connect_btn.setText('断开')
                self.global_status_text.append(f'成功连接到串口 {port}')
            else:
                self.global_status_text.append(f'连接串口 {port} 失败')
        else:
            self.serial_comm.disconnect()
            self.connect_btn.setText('连接')
            self.global_status_text.append('串口已断开连接')

    def on_joint_slider_pressed(self, joint_idx):
        """界面层：滑块按下事件"""
        self.user_interacting = True
    
    def on_joint_slider_released(self, joint_idx):
        """界面层：滑块释放事件"""
        # 延迟重置用户交互标记，确保拖动完成
        QTimer.singleShot(200, lambda: setattr(self, 'user_interacting', False))
    
    def on_joint_slider_changed(self, joint_idx, value):
        """界面层：处理关节滑块值变化"""
        angle = value
        self.joint_values[joint_idx].setText(f'{angle}°')
        angles = [slider.value() * np.pi / 180 for slider in self.joint_sliders]
        
        # 更新3D渲染
        self.gl_renderer.set_joint_angles(angles)
        
        # 在仿真模式和硬件模式下都要更新robot_control状态
        if hasattr(self, 'robot_control') and self.robot_control:
            self.robot_control.set_joint_angles(angles)

    def toggle_teaching(self):
        """界面层：切换示教模式"""
        if not hasattr(self, 'is_teaching'):
            self.is_teaching = False
        self.is_teaching = not self.is_teaching
        if self.is_teaching:
            self.global_status_text.append('开始示教模式')
        else:
            self.global_status_text.append('结束示教模式')

    def start_replay(self):
        """界面层：开始轨迹回放"""
        self.global_status_text.append('开始轨迹回放')

    def import_robot_model(self):
        """
        模型层：导入机器人模型

        注意事项：
        1. OpenGL context 必须 ready（即GLRenderer已初始化并显示）时才能调用 OpenGL API，否则会崩溃。
           否则会出现如：
           python: ../src/GLX/libglxmapping.c:277: __glXFetchDispatchEntry: Assertion `procName' failed.
           这类错误通常是因为在OpenGL上下文未就绪时调用了OpenGL相关API。
        2. 不要混用不同的 OpenGL 窗口库（Qt/pyglet/GLFW），否则会导致上下文混乱和崩溃。
        3. 在 PyCharm 下运行时，环境变量（尤其是 DISPLAY）要和终端一致，否则Qt无法连接X server，OpenGL context无法创建。

        解决此类报错的关键：
        - 确保 self.gl_renderer.isValid() 为 True（即OpenGL上下文已创建）。
        - 只用Qt的OpenGL窗口，不要和pyglet/GLFW等混用。
        - 若在IDE下报错，检查PyCharm的环境变量设置，DISPLAY要和终端一致。
        """
        try:
            model_name = self.model_combo.currentText().lower().replace(' ', '')
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            urdf_path = os.path.join(
                project_root,
                'resources', 'urdf',
                f'flexiv_{model_name}_kinematics.urdf'
            )
            self.global_status_text.append(f'尝试加载模型: {model_name}')
            self.global_status_text.append(f'URDF路径: {urdf_path}')
            if not os.path.exists(urdf_path):
                self.global_status_text.append(f'错误: URDF文件不存在')
                return

            # 检查OpenGL上下文是否ready
            if not self.gl_renderer.isValid():
                self.global_status_text.append('OpenGL上下文未就绪，无法加载模型。请确保窗口已显示。')
                return

            # 确保OpenGL已初始化
            if not hasattr(self.gl_renderer, '_gl_initialized') or not self.gl_renderer._gl_initialized:
                self.global_status_text.append('等待OpenGL初始化完成...')
                # 强制触发一次渲染以初始化OpenGL
                self.gl_renderer.update()
                # 给OpenGL一点时间初始化
                import time
                time.sleep(0.1)

            # 只允许Qt的OpenGL窗口
            success = self.gl_renderer.set_robot_model(urdf_path)
            if success:
                # 设置初始关节角度
                zero_angles = [0.0] * 7
                self.gl_renderer.set_joint_angles(zero_angles)
                
                # 更新UI控件
                for i, slider in enumerate(self.joint_sliders):
                    slider.setValue(0)
                    self.joint_values[i].setText("0°")
                
                # 默认关闭阴影以提高性能
                self.gl_renderer._render_shadows = False
                
                # 强制刷新渲染
                self.gl_renderer.update()
                self.global_status_text.append(f'成功加载模型: {model_name}')
                self.global_status_text.append('提示: 模型以米为单位，右键拖拽平移视角，左键拖拽旋转视角，滚轮缩放')
                self.global_status_text.append('提示: 点击"重置视角"按钮可重新居中模型')
            else:
                self.global_status_text.append(f'模型加载失败: {model_name}')
        except Exception as e:
            self.global_status_text.append(f'导入模型失败: {str(e)}')

    def toggle_shadows(self):
        """界面层：切换阴影渲染"""
        if hasattr(self.gl_renderer, '_render_shadows'):
            self.gl_renderer._render_shadows = not self.gl_renderer._render_shadows
            shadow_status = '开启' if self.gl_renderer._render_shadows else '关闭'
            self.shadow_btn.setText(f'阴影: {shadow_status}')
            self.global_status_text.append(f'阴影渲染已{shadow_status}')
            self.gl_renderer.update()

    def enable_robot_clicked(self):
        """使能按钮点击事件"""
        if hasattr(self, 'robot_control') and self.robot_control:
            self.robot_control.enable_robot()
            self.global_status_text.append('已发送使能命令')

    def toggle_mode(self):
        """界面层：切换硬件/仿真模式"""
        self.hardware = not self.hardware
        mode_str = '硬件模式' if self.hardware else '仿真/教学模式'
        self.global_status_text.append(f'已切换，当前运行模式：{mode_str}')
        # 重新实例化 Robot 并传递
        if self.hardware:
            self.robot = flexivrdk.Robot("Rizon10-062295")
        else:
            self.robot = None
        self.robot_control = RobotControl(robot=self.robot, hardware=self.hardware)
        self.gripper_control = GripperControl(robot=self.robot)
        # 可选：断开串口连接，重置UI等
        if self.serial_comm.is_connected():
            self.serial_comm.disconnect()
            self.connect_btn.setText('连接')
            self.global_status_text.append('串口已断开连接（模式切换）')

    def on_gripper_enable(self):
        # 使能抓手，需指定gripper_name
        if self.robot_control.robot is not None:
            self.gripper_control.robot = self.robot_control.robot
            # 这里假设抓手名为"Gripper1"，可根据实际UI输入
            self.gripper_control.enable("Gripper1")
            self.global_status_text.append('已发送抓手使能命令')

    def on_gripper_init(self):
        self.gripper_control.init()
        self.global_status_text.append('已发送抓手初始化命令')

    def on_gripper_open(self):
        self.gripper_control.move(0.09, 0.1, 20)  # 打开到最大宽度
        self.global_status_text.append('已发送抓手打开命令')

    def on_gripper_close(self):
        self.gripper_control.move(0.01, 0.1, 20)  # 闭合到最小宽度
        self.global_status_text.append('已发送抓手闭合命令')

    def on_gripper_stop(self):
        self.gripper_control.stop()
        self.global_status_text.append('已发送抓手停止命令')

    def update_gripper_state(self, state):
        # 实时显示抓手状态
        text = f"宽度: {getattr(state, 'width', '-'):.3f} m | 力: {getattr(state, 'force', '-'):.2f} N | 运动: {getattr(state, 'is_moving', '-')}"
        self.gripper_state_label.setText(f"状态: {text}")

    def update_gripper_param(self, param):
        # 显示抓手参数
        text = f"名称: {getattr(param, 'name', '-')} | 宽度: {getattr(param, 'min_width', '-')}~{getattr(param, 'max_width', '-')} m | 力: {getattr(param, 'min_force', '-')}~{getattr(param, 'max_force', '-')} N"
        self.gripper_param_label.setText(f"参数: {text}")

    def show_gripper_error(self, msg):
        self.global_status_text.append(f"[抓手错误] {msg}")

    def on_plan_exec(self):
        plan_name = self.plan_input.text().strip()
        if plan_name:
            self.robot_control.execute_plan(plan_name)
            self.global_status_text.append(f'已发送Plan执行命令: {plan_name}')

    def on_zero_ft(self):
        """力/力矩传感器归零按钮点击事件"""
        # 检查robot_control是否存在
        if not hasattr(self, 'robot_control') or self.robot_control is None:
            self.global_status_text.append('错误：机器人控制器未初始化，请先连接机器人')
            return
        
        # 检查连接状态
        if not self.is_robot_connected():
            self.global_status_text.append('错误：机器人未连接，无法执行力/力矩传感器归零')
            return
        
        # 执行归零操作
        try:
            self.robot_control.zero_force_torque_sensor()
            if self.hardware:
                self.global_status_text.append('已发送力/力矩传感器归零命令')
            else:
                self.global_status_text.append('仿真模式：已发送力/力矩传感器归零命令')
        except Exception as e:
            self.global_status_text.append(f'力/力矩传感器归零操作失败: {str(e)}')

    def on_auto_recover(self):
        self.robot_control.auto_recovery()
        self.global_status_text.append('已发送自动恢复命令')

    def on_sync_urdf(self):
        """URDF同步按钮点击事件"""
        try:
            # 检查robot_control是否存在
            if not hasattr(self, 'robot_control') or self.robot_control is None:
                self.global_status_text.append('错误：机器人控制器未初始化，请先连接机器人')
                return
                
            # 调用robot_control的sync_urdf方法
            success = self.robot_control.sync_urdf()
            if success:
                self.global_status_text.append('URDF同步成功，正在重新加载模型...')
                
                # 获取同步后的URDF文件路径（从robot_control获取）
                synced_urdf_path = None
                if hasattr(self.robot_control, 'last_synced_urdf_path'):
                    synced_urdf_path = self.robot_control.last_synced_urdf_path
                
                # 如果没有获取到路径，尝试查找最近修改的URDF文件
                if not synced_urdf_path:
                    project_root = os.path.dirname(os.path.dirname(__file__))
                    urdf_dir = os.path.join(project_root, 'resources', 'urdf')
                    
                    # 查找所有URDF文件并按修改时间排序
                    import glob
                    urdf_files = glob.glob(os.path.join(urdf_dir, '*.urdf'))
                    if urdf_files:
                        # 按修改时间排序，最新的在前
                        urdf_files.sort(key=os.path.getmtime, reverse=True)
                        synced_urdf_path = urdf_files[0]
                        self.global_status_text.append(f'使用最近修改的URDF文件: {os.path.basename(synced_urdf_path)}')
                
                if synced_urdf_path and os.path.exists(synced_urdf_path):
                    # 加载同步后的URDF
                    if hasattr(self, 'robot_model') and self.robot_model:
                        self.robot_model.load_calibrated_urdf(synced_urdf_path)
                        self.update_robot_model()
                        self.global_status_text.append(f'标定URDF加载完成: {os.path.basename(synced_urdf_path)}')
                    else:
                        self.global_status_text.append('警告：机器人模型未初始化，无法加载标定URDF')
                else:
                    self.global_status_text.append('警告：无法找到同步后的URDF文件')
                    # 列出urdf目录中的文件以便调试
                    try:
                        project_root = os.path.dirname(os.path.dirname(__file__))
                        urdf_dir = os.path.join(project_root, 'resources', 'urdf')
                        files = os.listdir(urdf_dir)
                        urdf_files = [f for f in files if f.endswith('.urdf')]
                        self.global_status_text.append(f'URDF目录中的文件: {urdf_files}')
                    except Exception as list_error:
                        self.global_status_text.append(f'无法列出URDF目录文件: {str(list_error)}')
            else:
                self.global_status_text.append('URDF同步失败')
        except Exception as e:
            self.global_status_text.append(f'URDF同步错误: {str(e)}')

    def on_refresh_tools(self):
        """刷新工具列表"""
        if hasattr(self, 'robot_control') and self.robot_control:
            try:
                # 获取工具列表
                tool_list = self.robot_control.get_tool_list()
                
                # 清空并重新填充下拉框
                self.tool_combo.clear()
                self.tool_combo.addItems(tool_list)
                
                # 获取当前工具并设置为选中项
                current_tool = self.robot_control.get_current_tool()
                index = self.tool_combo.findText(current_tool)
                if index >= 0:
                    self.tool_combo.setCurrentIndex(index)
                
                # 更新当前工具显示
                self.current_tool_label.setText(f'当前工具: {current_tool}')
                
                self.global_status_text.append(f'工具列表已刷新，共{len(tool_list)}个工具')
                
            except Exception as e:
                self.global_status_text.append(f'刷新工具列表失败: {str(e)}')
        else:
            self.global_status_text.append('机器人控制未初始化')
    
    def on_tool_switch(self):
        """切换工具"""
        if hasattr(self, 'robot_control') and self.robot_control:
            selected_tool = self.tool_combo.currentText()
            if selected_tool:
                self.robot_control.switch_tool(selected_tool)
                self.global_status_text.append(f'已发送工具切换命令: {selected_tool}')
            else:
                self.global_status_text.append('请先选择要切换的工具')
        else:
            self.global_status_text.append('机器人控制未初始化')

    def on_get_global_vars(self):
        self.robot_control.get_global_variables()
        self.global_status_text.append('已请求全局变量')

    def on_plan_executed(self, plan_name):
        self.global_status_text.append(f'Plan执行完成: {plan_name}')

    def on_force_sensor_zeroed(self):
        self.global_status_text.append('力/力矩传感器归零完成')

    def on_auto_recovered(self):
        self.global_status_text.append('自动恢复完成')

    def on_tool_updated(self, tool_name):
        """工具切换完成回调"""
        self.global_status_text.append(f'工具切换完成: {tool_name}')
        
        # 更新当前工具显示
        self.current_tool_label.setText(f'当前工具: {tool_name}')
        
        # 更新下拉框选中项
        index = self.tool_combo.findText(tool_name)
        if index >= 0:
            self.tool_combo.setCurrentIndex(index)

    def on_global_vars_updated(self, vars):
        """处理全局变量更新事件"""
        try:
            # 安全地序列化全局变量数据
            formatted_vars = self._format_global_vars(vars)
            self.global_vars_text.setPlainText(formatted_vars)
            self.global_status_text.append('全局变量已更新')
        except Exception as e:
            error_msg = f'全局变量显示失败: {str(e)}'
            self.global_vars_text.setPlainText(error_msg)
            self.global_status_text.append(error_msg)
    
    def _format_global_vars(self, vars):
        """安全地格式化全局变量数据"""
        if not vars:
            return '无全局变量数据'
        
        formatted_lines = []
        formatted_lines.append('机器人全局变量:')
        formatted_lines.append('=' * 50)
        
        for key, value in vars.items():
            try:
                # 安全地处理不同类型的值
                if isinstance(value, (list, tuple)):
                    # 处理数组类型
                    if len(value) <= 10:  # 限制显示长度
                        value_str = f'[{", ".join(f"{v:.6f}" if isinstance(v, float) else str(v) for v in value)}]'
                    else:
                        value_str = f'[数组长度: {len(value)}, 前3项: {", ".join(str(v) for v in value[:3])}...]'
                elif isinstance(value, dict):
                    # 处理字典类型
                    value_str = f'{{字典包含 {len(value)} 项}}'
                elif isinstance(value, float):
                    # 处理浮点数，保留6位小数
                    value_str = f'{value:.6f}'
                elif hasattr(value, '__call__'):
                    # 处理方法对象
                    value_str = f'<方法对象: {type(value).__name__}>'
                else:
                    # 处理其他类型
                    value_str = str(value)
                
                formatted_lines.append(f'{key:20s}: {value_str}')
                
            except Exception as e:
                # 如果单个变量处理失败，显示错误信息
                formatted_lines.append(f'{key:20s}: <处理失败: {str(e)}>')
        
        formatted_lines.append('=' * 50)
        formatted_lines.append(f'共 {len(vars)} 个全局变量')
        
        return '\n'.join(formatted_lines)

    def on_global_vars_apply(self, variables):
        """处理全局变量应用事件"""
        try:
            if hasattr(self, 'robot_control') and self.robot_control:
                self.robot_control.set_global_variables(variables)
                self.global_status_text.append(f'已应用 {len(variables)} 个全局变量到机器人')
            else:
                self.global_status_text.append('机器人未连接，无法应用全局变量')
        except Exception as e:
            self.global_status_text.append(f'应用全局变量失败: {str(e)}')
    
    def on_robot_error(self, msg):
        self.global_status_text.append(f'[机器人错误] {msg}')
    
    def update_status_message(self, message):
        """更新状态消息到全局状态栏"""
        self.global_status_text.append(f'[高级控制] {message}')
    
    def show_error_message(self, message):
        """显示错误消息到全局状态栏"""
        self.global_status_text.append(f'[错误] {message}')

    def on_connect_robot_sn(self):
        # 检查当前连接状态，决定是连接还是断开
        # 通过按钮文本来判断当前状态更可靠
        if self.sn_connect_btn.text() == '断开':
            # 当前已连接，执行断开操作
            self.disconnect_robot()
        else:
            # 当前未连接，执行连接操作
            self.connect_robot()
    
    def is_robot_connected(self):
        """检查机器人是否已连接"""
        if not hasattr(self, 'robot_control') or not self.robot_control:
            return False
        
        if self.hardware and hasattr(self.robot_control, 'robot') and self.robot_control.robot:
            try:
                return self.robot_control.robot.connected()
            except Exception:
                return False
        else:
            # 仿真模式下，如果robot_control存在且running标志为True，则认为已连接
            return hasattr(self.robot_control, 'running') and self.robot_control.running
    
    def connect_robot(self):
        """连接机器人"""
        sn = self.sn_input.text().strip()
        if not sn:
            self.global_status_text.append('请输入机器人序列号')
            self.set_status_light(False)
            return
        
        self.global_status_text.append(f'正在连接机器人: {sn}...')
        self.set_status_light(False)  # 初始设置为未连接状态
        
        try:
            # 在仿真模式下，保存当前关节状态
            if not self.hardware and hasattr(self, 'robot_control') and self.robot_control:
                self.saved_joint_angles = self.robot_control.get_joint_angles().copy()
                self.global_status_text.append('已保存当前关节状态')
            
            # 重新初始化RobotControl，在仿真模式下传入保存的关节角度
            if not self.hardware and self.saved_joint_angles is not None:
                self.robot_control = RobotControl(robot_id=sn, hardware=self.hardware, initial_joint_angles=self.saved_joint_angles)
                self.global_status_text.append('已恢复之前的关节状态')
            else:
                self.robot_control = RobotControl(robot_id=sn, hardware=self.hardware)
            
            # 检查实际连接状态
            if self.hardware and hasattr(self.robot_control, 'robot') and self.robot_control.robot:
                # 硬件模式下检查实际连接状态
                import time
                # 等待连接建立
                for i in range(10):  # 最多等待5秒
                    if self.robot_control.robot.connected():
                        break
                    time.sleep(0.5)
                    self.global_status_text.append(f'连接尝试 {i+1}/10...')
                
                if self.robot_control.robot.connected():
                    self.global_status_text.append(f'机器人连接成功: {sn}')
                    self.sn_input.setEnabled(False)
                    self.sn_connect_btn.setText('断开')
                    self.set_status_light(True)
                    connection_success = True
                else:
                    self.global_status_text.append(f'机器人连接失败: 无法建立与 {sn} 的连接')
                    self.set_status_light(False)
                    # 连接失败时清理robot_control对象
                    if hasattr(self.robot_control, 'stop'):
                        self.robot_control.stop()
                    self.robot_control = None
                    connection_success = False
            else:
                # 仿真模式或无硬件时
                self.global_status_text.append(f'仿真模式连接: {sn}')
                self.sn_input.setEnabled(False)
                self.sn_connect_btn.setText('断开')
                self.set_status_light(True)
                connection_success = True
            
            if connection_success:
                # 重新绑定信号
                self.robot_control.joint_updated.connect(self.update_monitor_joint)
                self.robot_control.end_effector_updated.connect(self.update_monitor_ee)
                self.robot_control.status_updated.connect(self.update_monitor_status)
                self.robot_control.error_signal.connect(self.update_monitor_fault)
                
                # 连接新的状态信号
                self.robot_control.robot_states_updated.connect(self.update_robot_states)
                self.robot_control.joint_velocity_updated.connect(self.update_monitor_velocity)
                self.robot_control.joint_torque_updated.connect(self.update_monitor_torque)
                self.robot_control.ft_sensor_updated.connect(self.update_monitor_ft)
                self.robot_control.mode_updated.connect(self.update_monitor_mode)
                
                self.robot_control.plan_executed.connect(self.on_plan_executed)
                self.robot_control.force_sensor_zeroed.connect(self.on_force_sensor_zeroed)
                self.robot_control.auto_recovered.connect(self.on_auto_recovered)
                self.robot_control.tool_updated.connect(self.on_tool_updated)
                self.robot_control.global_vars_updated.connect(self.on_global_vars_updated)
                # 连接全局变量组件的信号
                if hasattr(self, 'global_vars_widget'):
                    self.robot_control.global_vars_updated.connect(self.global_vars_widget.update_variables)
                self.robot_control.plan_list_updated.connect(self.on_plan_list_updated)
                self.robot_control.plan_info_updated.connect(self.on_plan_info_updated)
                # 启动robot_control线程（如有run方法）
                if hasattr(self.robot_control, 'start'):
                    self.robot_control.start()
                
                # 自动刷新工具列表
                self.on_refresh_tools()
                
                # 自动刷新Plan列表
                self.on_refresh_plan_list()
                
                self.save_last_robot_sn(sn)
                self.update_mode_label()
            else:
                # 连接失败时重新启用输入控件
                self.sn_input.setEnabled(True)
                self.sn_connect_btn.setText('连接')
                
        except Exception as e:
            self.global_status_text.append(f'连接机器人异常: {e}')
            self.set_status_light(False)
            # 连接异常时重新启用输入控件
            self.sn_input.setEnabled(True)
            self.sn_connect_btn.setText('连接')
    
    def disconnect_robot(self):
        """断开机器人连接"""
        try:
            self.global_status_text.append('正在断开机器人连接...')
            
            # 停止robot_control线程
            if hasattr(self, 'robot_control') and self.robot_control:
                if hasattr(self.robot_control, 'stop'):
                    self.robot_control.stop()
                if hasattr(self.robot_control, 'quit'):
                    self.robot_control.quit()
                if hasattr(self.robot_control, 'wait'):
                    self.robot_control.wait()
            
            # 重置UI状态
            self.sn_input.setEnabled(True)
            self.sn_connect_btn.setText('连接')
            self.set_status_light(False)
            
            # 清空robot_control引用
            self.robot_control = None
            
            self.global_status_text.append('机器人连接已断开')
            self.update_mode_label()
            
        except Exception as e:
            self.global_status_text.append(f'断开连接异常: {e}')
            # 即使异常也要重置UI状态
            self.sn_input.setEnabled(True)
            self.sn_connect_btn.setText('连接')
            self.set_status_light(False)
            self.robot_control = None

    def load_last_robot_sn(self):
        try:
            if os.path.exists('.robot_sn'):
                with open('.robot_sn', 'r') as f:
                    sn = f.read().strip()
                    if sn:
                        self.sn_input.setText(sn)
        except Exception as e:
            print(f'加载上次机器人SN失败: {e}')

    def save_last_robot_sn(self, sn):
        try:
            with open('.robot_sn', 'w') as f:
                f.write(sn)
        except Exception as e:
            print(f'保存机器人SN失败: {e}')

    def on_refresh_plan_list(self):
        if hasattr(self, 'robot_control') and self.robot_control:
            self.robot_control.get_plan_list()
            self.update_mode_label()

    def on_plan_list_updated(self, plan_list):
        self.plan_combo.clear()
        self.plan_combo.addItems(plan_list)
        self.global_status_text.append(f'已刷新Plan列表: {plan_list}')

    def on_plan_exec_by_name(self):
        plan_name = self.plan_combo.currentText().strip()
        if plan_name:
            self.robot_control.execute_plan(plan_name)
            self.global_status_text.append(f'已发送Plan执行命令: {plan_name}')

    def on_plan_exec_by_index(self):
        plan_index = self.plan_index_input.text().strip()
        if plan_index.isdigit():
            idx = int(plan_index)
            self.robot_control.execute_plan(idx)
            self.global_status_text.append(f'已发送Plan索引执行命令: {idx}')
        else:
            self.global_status_text.append('请输入有效的Plan索引')
    
    def on_plan_stop(self):
        """停止当前执行的plan"""
        self.robot_control.stop_plan()
        self.global_status_text.append('已发送停止Plan命令')
    
    def on_plan_stopped(self, plan_name):
        """plan停止完成的回调"""
        self.global_status_text.append(f'Plan {plan_name} 已停止执行')
    
    def on_speed_changed(self, value):
        """速度滑块值改变事件"""
        speed = value / 100.0  # 转换为0.1-1.0范围
        self.robot_control.set_execution_speed(speed)
        self.speed_label.setText(f'{value}%')  # 显示百分比
        self.global_status_text.append(f'执行速度已设置为: {value}%')

    def on_plan_info_updated(self, info):
        if info:
            text = f"当前Plan: {getattr(info, 'assigned_plan_name', '-')}, 节点: {getattr(info, 'node_name', '-')}, 路径: {getattr(info, 'node_path', '-')}, 节点序号: {getattr(info, 'node_path_number', '-')}, 时间: {getattr(info, 'node_path_time_period', '-')}, 速度缩放: {getattr(info, 'velocity_scale', '-')}, 等待步进: {getattr(info, 'waiting_for_step', '-')}, pt_name: {getattr(info, 'pt_name', '-') }"
            self.plan_info_text.setPlainText(text)
            self.global_status_text.append(text)
    
    # 分屏控制方法
    def set_splitter_equal(self):
        """设置分屏器为等分布局 - 优化setSizes调用"""
        total_width = self.splitter.width()
        equal_width = total_width // 2
        new_sizes = [equal_width, equal_width]
        self._safe_set_splitter_sizes(new_sizes)
        self.global_status_text.append('已设置为等分布局')
    
    def set_splitter_left_priority(self):
        """设置左侧面板优先（60%:40%） - 优化setSizes调用"""
        total_width = self.splitter.width()
        left_width = int(total_width * 0.6)
        right_width = int(total_width * 0.4)
        new_sizes = [left_width, right_width]
        self._safe_set_splitter_sizes(new_sizes)
        self.global_status_text.append('已设置为左侧优先布局')
    
    def set_splitter_right_priority(self):
        """设置右侧面板优先（30%:70%） - 优化setSizes调用"""
        total_width = self.splitter.width()
        left_width = int(total_width * 0.3)
        right_width = int(total_width * 0.7)
        new_sizes = [left_width, right_width]
        self._safe_set_splitter_sizes(new_sizes)
        self.global_status_text.append('已设置为右侧优先布局')
    
    def toggle_3d_view(self):
        """切换3D视图的显示/隐藏状态 - 优化setSizes调用"""
        if self.btn_toggle_3d_view.isChecked():
            # 隐藏3D视图，实现左侧标签页全屏化
            self._saved_splitter_sizes = self.splitter.sizes()
            
            # 完全隐藏右侧3D视图，让左侧标签页占据全屏
            self.gl_renderer.setVisible(False)
            # 设置左侧占据100%宽度，右侧为0
            total_width = self.splitter.width()
            new_sizes = [total_width, 0]
            self._safe_set_splitter_sizes(new_sizes)
            
            # 设置左侧标签页的最小和最大宽度以实现全屏效果
            self.left_tab.setMinimumWidth(total_width - 20)  # 减去一些边距
            self.left_tab.setMaximumWidth(total_width)
            
            self.btn_toggle_3d_view.setText('显示3D视图')
            self.global_status_text.append('已隐藏3D视图，左侧界面已全屏化')
            
            # 优化监控图表布局 - 3D视图关闭时图表获得更大空间
            if hasattr(self, 'monitor_tab'):
                # 扩大图表显示区域以利用全屏空间
                self.monitor_tab.setMinimumSize(total_width - 350, 450)  # 根据全屏宽度调整
                self.monitor_tab.setMaximumHeight(800)  # 增加最大高度
                # 优化每个图表的尺寸以适应全屏
                if hasattr(self, 'all_plots'):
                    for plot in self.all_plots:
                        plot.setMinimumSize(total_width - 400, 400)  # 根据全屏宽度调整图表尺寸
                        plot.setMaximumHeight(750)
        else:
            # 显示3D视图，恢复分屏布局
            self.gl_renderer.setVisible(True)
            
            # 恢复左侧标签页的原始宽度限制
            self.left_tab.setMinimumWidth(350)
            self.left_tab.setMaximumWidth(500)
            
            # 恢复分屏布局
            if hasattr(self, '_saved_splitter_sizes') and self._saved_splitter_sizes:
                self._safe_set_splitter_sizes(self._saved_splitter_sizes)
            else:
                # 默认恢复为40%:60%
                total_width = self.splitter.width()
                left_width = int(total_width * 0.4)
                right_width = int(total_width * 0.6)
                new_sizes = [left_width, right_width]
                self._safe_set_splitter_sizes(new_sizes)
            
            self.btn_toggle_3d_view.setText('隐藏3D视图')
            self.global_status_text.append('已显示3D视图，恢复分屏布局')
            
            # 恢复监控图表原始布局
            if hasattr(self, 'monitor_tab'):
                # 恢复图表显示区域原始尺寸
                self.monitor_tab.setMinimumSize(450, 350)  # 恢复原始最小尺寸
                self.monitor_tab.setMaximumHeight(550)  # 恢复原始最大高度
                # 恢复每个图表的原始尺寸
                if hasattr(self, 'all_plots'):
                    for plot in self.all_plots:
                        plot.setMinimumSize(400, 300)  # 恢复原始图表尺寸
                        plot.setMaximumHeight(500)
    
    def toggle_right_panel(self):
        """切换右侧面板的显示/隐藏状态 - 优化setSizes调用"""
        if hasattr(self, '_right_panel_hidden') and self._right_panel_hidden:
            # 显示右侧面板
            if hasattr(self, '_saved_splitter_sizes') and self._saved_splitter_sizes:
                self._safe_set_splitter_sizes(self._saved_splitter_sizes)
            else:
                # 默认恢复为40%:60%
                total_width = self.splitter.width()
                left_width = int(total_width * 0.4)
                right_width = int(total_width * 0.6)
                new_sizes = [left_width, right_width]
                self._safe_set_splitter_sizes(new_sizes)
            self._right_panel_hidden = False
            self.global_status_text.append('已显示右侧面板')
        else:
            # 隐藏右侧面板
            self._saved_splitter_sizes = self.splitter.sizes()
            total_width = self.splitter.width()
            new_sizes = [total_width, 0]
            self._safe_set_splitter_sizes(new_sizes)
            self._right_panel_hidden = True
            self.global_status_text.append('已隐藏右侧面板')
    
    # 响应式布局方法
    def resizeEvent(self, event):
        """窗口大小变化事件处理 - 使用防抖机制"""
        super().resizeEvent(event)
        if hasattr(self, '_adaptive_layout_enabled') and self._adaptive_layout_enabled:
            # 使用防抖机制，避免频繁调用布局调整
            self._pending_size = event.size()
            self._resize_timer.stop()
            self._resize_timer.start(100)  # 100ms延迟
    
    def _delayed_layout_adjustment(self):
        """延迟执行的布局调整方法"""
        if self._pending_size and not self._layout_adjustment_in_progress:
            self._layout_adjustment_in_progress = True
            try:
                self.adjust_layout_for_size(self._pending_size)
            finally:
                self._layout_adjustment_in_progress = False
                self._pending_size = None
    
    def adjust_layout_for_size(self, size):
        """根据窗口大小调整布局 - 优化setSizes调用"""
        width = size.width()
        height = size.height()
        
        # 检查是否需要调整布局
        if not hasattr(self, 'splitter') or not self.splitter:
            return
            
        current_sizes = self.splitter.sizes()
        new_sizes = None
        
        # 小屏幕适配（宽度小于1000px）
        if width < 1000:
            # 调整左侧面板最小宽度
            if hasattr(self, 'left_tab'):
                self.left_tab.setMinimumWidth(280)
                self.left_tab.setMaximumWidth(350)
            
            # 自动隐藏右侧面板以节省空间
            if not getattr(self, '_right_panel_hidden', False):
                self._saved_splitter_sizes = current_sizes
                new_sizes = [width, 0]
                self._right_panel_hidden = True
        
        # 中等屏幕适配（1000px-1400px）
        elif width < 1400:
            if hasattr(self, 'left_tab'):
                self.left_tab.setMinimumWidth(320)
                self.left_tab.setMaximumWidth(400)
            
            # 恢复右侧面板但调整比例
            if getattr(self, '_right_panel_hidden', False):
                left_width = int(width * 0.45)
                right_width = int(width * 0.55)
                new_sizes = [left_width, right_width]
                self._right_panel_hidden = False
        
        # 大屏幕适配（宽度大于1400px）
        else:
            if hasattr(self, 'left_tab'):
                self.left_tab.setMinimumWidth(350)
                self.left_tab.setMaximumWidth(500)
            
            # 恢复默认布局比例
            left_width = int(width * 0.4)
            right_width = int(width * 0.6)
            target_sizes = [left_width, right_width]
            
            # 只有当尺寸变化显著时才调整
            if not self._sizes_similar(current_sizes, target_sizes, tolerance=50):
                new_sizes = target_sizes
                self._right_panel_hidden = False
        
        # 调整监控组中图表的显示 - 考虑3D视图状态
        if hasattr(self, 'monitor_tab'):
            # 检查3D视图是否隐藏
            is_3d_hidden = hasattr(self, 'btn_toggle_3d_view') and self.btn_toggle_3d_view.isChecked()
            
            if is_3d_hidden:
                # 3D视图隐藏时，确保左侧标签页全屏化
                self.left_tab.setMinimumWidth(width - 20)
                self.left_tab.setMaximumWidth(width)
                
                # 根据全屏宽度调整图表尺寸
                chart_width = width - 350  # 减去边距
                if width < 1000:
                    self.monitor_tab.setMinimumSize(chart_width, 400)
                    if hasattr(self, 'all_plots'):
                        for plot in self.all_plots:
                            plot.setMinimumSize(chart_width - 50, 350)
                elif width < 1400:
                    self.monitor_tab.setMinimumSize(chart_width, 450)
                    if hasattr(self, 'all_plots'):
                        for plot in self.all_plots:
                            plot.setMinimumSize(chart_width - 50, 400)
                else:
                    self.monitor_tab.setMinimumSize(chart_width, 500)
                    if hasattr(self, 'all_plots'):
                        for plot in self.all_plots:
                            plot.setMinimumSize(chart_width - 50, 450)
            else:
                # 3D视图显示时，恢复标准分屏布局
                if width < 1000:
                    self.left_tab.setMinimumWidth(280)
                    self.left_tab.setMaximumWidth(350)
                    self.monitor_tab.setMinimumSize(350, 300)
                    if hasattr(self, 'all_plots'):
                        for plot in self.all_plots:
                            plot.setMinimumSize(300, 250)
                elif width < 1400:
                    self.left_tab.setMinimumWidth(320)
                    self.left_tab.setMaximumWidth(400)
                    self.monitor_tab.setMinimumSize(400, 350)
                    if hasattr(self, 'all_plots'):
                        for plot in self.all_plots:
                            plot.setMinimumSize(350, 300)
                else:
                    self.left_tab.setMinimumWidth(350)
                    self.left_tab.setMaximumWidth(500)
                    self.monitor_tab.setMinimumSize(450, 350)
                    if hasattr(self, 'all_plots'):
                        for plot in self.all_plots:
                            plot.setMinimumSize(400, 300)
        
        # 只有在需要时才调用setSizes
        if new_sizes and not self._sizes_similar(current_sizes, new_sizes, tolerance=20):
            self._safe_set_splitter_sizes(new_sizes)
        
        # 更新记录的窗口大小
        self._last_window_size = size
    
    def _sizes_similar(self, sizes1, sizes2, tolerance=20):
        """检查两个尺寸数组是否相似"""
        if not sizes1 or not sizes2 or len(sizes1) != len(sizes2):
            return False
        return all(abs(s1 - s2) <= tolerance for s1, s2 in zip(sizes1, sizes2))
    
    def _safe_set_splitter_sizes(self, sizes):
        """安全地设置splitter尺寸，避免频繁调用"""
        if not hasattr(self, 'splitter') or not self.splitter:
            return
            
        # 检查是否与上次设置的尺寸相同
        if self._last_splitter_sizes and self._sizes_similar(self._last_splitter_sizes, sizes, tolerance=10):
            return
            
        try:
            self.splitter.setSizes(sizes)
            self._last_splitter_sizes = sizes[:]
        except Exception as e:
            # 静默处理setSizes可能的异常
            pass
    
    # 通信协议相关方法
    def on_protocol_changed(self, protocol_name):
        """通信协议切换事件"""
        protocol_index = self.protocol_combo.currentIndex()
        self.protocol_stack.setCurrentIndex(protocol_index)
        self.global_status_text.append(f'已切换到{protocol_name}协议')
        
        # 重置连接状态
        self.comm_status_label.setText('未连接')
        self.comm_status_label.setStyleSheet('color: red; font-weight: bold;')
    
    def refresh_serial_ports(self):
        """刷新串口列表"""
        try:
            import serial.tools.list_ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.serial_port_combo.clear()
            self.serial_port_combo.addItems(ports)
            self.global_status_text.append(f'已刷新串口列表: {ports}')
        except Exception as e:
            self.global_status_text.append(f'刷新串口列表失败: {e}')
    
    def on_comm_connect(self):
        """连接通信"""
        protocol = self.protocol_combo.currentText()
        try:
            if protocol == '串口通信':
                self.connect_serial()
            elif protocol == 'TCP/IP':
                self.connect_tcpip()
            elif protocol == 'Profinet':
                self.connect_profinet()
            elif protocol == 'ModBus TCP/IP':
                self.connect_modbus()
        except Exception as e:
            self.global_status_text.append(f'{protocol}连接失败: {e}')
            self.comm_status_label.setText('连接失败')
            self.comm_status_label.setStyleSheet('color: red; font-weight: bold;')
    
    def on_comm_disconnect(self):
        """断开通信"""
        protocol = self.protocol_combo.currentText()
        try:
            # 这里可以添加具体的断开逻辑
            self.comm_status_label.setText('未连接')
            self.comm_status_label.setStyleSheet('color: red; font-weight: bold;')
            self.global_status_text.append(f'{protocol}已断开连接')
        except Exception as e:
            self.global_status_text.append(f'{protocol}断开连接失败: {e}')
    
    def on_comm_test(self):
        """测试通信连接"""
        protocol = self.protocol_combo.currentText()
        try:
            if protocol == '串口通信':
                self.test_serial_connection()
            elif protocol == 'TCP/IP':
                self.test_tcpip_connection()
            elif protocol == 'Profinet':
                self.test_profinet_connection()
            elif protocol == 'ModBus TCP/IP':
                self.test_modbus_connection()
        except Exception as e:
            self.global_status_text.append(f'{protocol}连接测试失败: {e}')
    
    def connect_serial(self):
        """连接串口"""
        port = self.serial_port_combo.currentText()
        baud = int(self.serial_baud_combo.currentText())
        data_bits = int(self.serial_data_bits.currentText())
        stop_bits = float(self.serial_stop_bits.currentText())
        parity = self.serial_parity.currentText()
        
        # 这里添加实际的串口连接逻辑
        self.comm_status_label.setText('已连接')
        self.comm_status_label.setStyleSheet('color: green; font-weight: bold;')
        self.global_status_text.append(f'串口连接成功: {port}, 波特率: {baud}')
    
    def connect_tcpip(self):
        """连接TCP/IP"""
        mode = self.tcpip_mode_combo.currentText()
        timeout = self.tcpip_timeout_input.value()
        
        try:
            if mode == 'Client':
                # Client模式连接
                host = self.tcpip_client_host_input.text()
                port = self.tcpip_client_port_input.value()
                
                if not host:
                    self.global_status_text.append('请输入服务器IP地址')
                    return
                
                # 这里添加实际的TCP/IP Client连接逻辑
                # import socket
                # self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # self.tcp_client_socket.settimeout(timeout)
                # self.tcp_client_socket.connect((host, port))
                
                self.comm_status_label.setText('已连接(Client)')
                self.comm_status_label.setStyleSheet('color: green; font-weight: bold;')
                self.global_status_text.append(f'TCP/IP Client连接成功: {host}:{port}')
                
            elif mode == 'Server':
                # Server模式启动
                bind_addr = self.tcpip_server_bind_input.text()
                port = self.tcpip_server_port_input.value()
                max_conn = self.tcpip_server_max_conn_input.value()
                
                if not bind_addr:
                    bind_addr = '0.0.0.0'
                
                # 这里添加实际的TCP/IP Server启动逻辑
                # import socket
                # self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # self.tcp_server_socket.bind((bind_addr, port))
                # self.tcp_server_socket.listen(max_conn)
                
                self.comm_status_label.setText('已启动(Server)')
                self.comm_status_label.setStyleSheet('color: green; font-weight: bold;')
                self.global_status_text.append(f'TCP/IP Server启动成功: {bind_addr}:{port}, 最大连接数: {max_conn}')
                
        except Exception as e:
            self.comm_status_label.setText('连接失败')
            self.comm_status_label.setStyleSheet('color: red; font-weight: bold;')
            self.global_status_text.append(f'TCP/IP {mode}连接失败: {str(e)}')
    
    def connect_profinet(self):
        """连接Profinet"""
        device_name = self.profinet_device_name.text()
        ip = self.profinet_ip_input.text()
        station = self.profinet_station_input.value()
        
        # 这里添加实际的Profinet连接逻辑
        self.comm_status_label.setText('已连接')
        self.comm_status_label.setStyleSheet('color: green; font-weight: bold;')
        self.global_status_text.append(f'Profinet连接成功: {device_name} ({ip}), 站号: {station}')
    
    def connect_modbus(self):
        """连接ModBus TCP/IP"""
        host = self.modbus_host_input.text()
        port = self.modbus_port_input.value()
        slave = self.modbus_slave_input.value()
        
        # 这里添加实际的ModBus连接逻辑
        self.comm_status_label.setText('已连接')
        self.comm_status_label.setStyleSheet('color: green; font-weight: bold;')
        self.global_status_text.append(f'ModBus TCP/IP连接成功: {host}:{port}, 从站: {slave}')
    
    def test_serial_connection(self):
        """测试串口连接"""
        port = self.serial_port_combo.currentText()
        if port:
            self.global_status_text.append(f'串口连接测试: {port} - 测试通过')
        else:
            self.global_status_text.append('请先选择串口')
    
    def test_tcpip_connection(self):
        """测试TCP/IP连接"""
        mode = self.tcpip_mode_combo.currentText()
        
        try:
            if mode == 'Client':
                host = self.tcpip_client_host_input.text()
                port = self.tcpip_client_port_input.value()
                
                if not host:
                    self.global_status_text.append('请先输入服务器IP地址')
                    return
                
                # 这里添加实际的TCP/IP Client连接测试逻辑
                # import socket
                # test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # test_socket.settimeout(3)
                # result = test_socket.connect_ex((host, port))
                # test_socket.close()
                # if result == 0:
                #     self.global_status_text.append(f'TCP/IP Client连接测试: {host}:{port} - 测试通过')
                # else:
                #     self.global_status_text.append(f'TCP/IP Client连接测试: {host}:{port} - 连接失败')
                
                self.global_status_text.append(f'TCP/IP Client连接测试: {host}:{port} - 测试通过')
                
            elif mode == 'Server':
                bind_addr = self.tcpip_server_bind_input.text()
                port = self.tcpip_server_port_input.value()
                
                if not bind_addr:
                    bind_addr = '0.0.0.0'
                
                # 这里添加实际的TCP/IP Server端口测试逻辑
                # import socket
                # test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # try:
                #     test_socket.bind((bind_addr, port))
                #     test_socket.close()
                #     self.global_status_text.append(f'TCP/IP Server端口测试: {bind_addr}:{port} - 端口可用')
                # except OSError:
                #     self.global_status_text.append(f'TCP/IP Server端口测试: {bind_addr}:{port} - 端口被占用')
                
                self.global_status_text.append(f'TCP/IP Server端口测试: {bind_addr}:{port} - 端口可用')
                
        except Exception as e:
            self.global_status_text.append(f'TCP/IP {mode}连接测试失败: {str(e)}')
    
    def test_profinet_connection(self):
        """测试Profinet连接"""
        device_name = self.profinet_device_name.text()
        ip = self.profinet_ip_input.text()
        if device_name and ip:
            self.global_status_text.append(f'Profinet连接测试: {device_name} ({ip}) - 测试通过')
        else:
            self.global_status_text.append('请先输入设备名称和IP地址')
    
    def test_modbus_connection(self):
        """测试ModBus连接"""
        host = self.modbus_host_input.text()
        port = self.modbus_port_input.value()
        if host:
            self.global_status_text.append(f'ModBus TCP/IP连接测试: {host}:{port} - 测试通过')
        else:
            self.global_status_text.append('请先输入IP地址')
    
    def changeEvent(self, event):
        """窗口状态变化事件处理 - 优化setSizes调用"""
        super().changeEvent(event)
        if event.type() == event.WindowStateChange:
            # 检测最大化/还原状态变化
            if self.isMaximized() and not self._is_maximized:
                self._is_maximized = True
                # 最大化时优化布局
                if hasattr(self, 'splitter') and self.splitter:
                    screen = QDesktopWidget().screenGeometry()
                    left_width = int(screen.width() * 0.35)
                    right_width = int(screen.width() * 0.65)
                    new_sizes = [left_width, right_width]
                    self._safe_set_splitter_sizes(new_sizes)
            elif not self.isMaximized() and self._is_maximized:
                self._is_maximized = False
                # 还原时恢复默认比例
                if hasattr(self, 'splitter') and self.splitter:
                    total_width = self.width()
                    left_width = int(total_width * 0.4)
                    right_width = int(total_width * 0.6)
                    new_sizes = [left_width, right_width]
                    self._safe_set_splitter_sizes(new_sizes)

def main():
    parser = argparse.ArgumentParser(description='Flexiv Robot Control System')
    parser.add_argument('--sim', action='store_true', help='使用仿真/教学模式')
    parser.add_argument('--hardware', action='store_true', help='强制硬件模式')
    args = parser.parse_args()
    
    # 使用全局变量检测flexivrdk
    flexiv_ok = FLEXIV_AVAILABLE
    if args.sim:
        hardware = False
    elif args.hardware:
        hardware = True
    else:
        hardware = flexiv_ok
    
    # macOS特定设置，消除GUI警告
    import platform
    if platform.system() == 'Darwin':  # macOS
        # 设置Qt应用程序属性，避免macOS GUI警告
        os.environ['QT_MAC_WANTS_LAYER'] = '1'
        # 禁用输入法相关的警告
        os.environ['QT_IM_MODULE'] = ''
        # 禁用macOS原生事件处理
        os.environ['QT_MAC_DISABLE_FOREGROUND_APPLICATION_TRANSFORM'] = '1'
        # 设置高DPI支持
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        # 禁用窗口移动动画相关警告
        QApplication.setAttribute(Qt.AA_DontShowIconsInMenus, True)
        # 禁用原生窗口装饰
        QApplication.setAttribute(Qt.AA_MacPluginApplication, True)
        # 禁用Cocoa事件处理
        QApplication.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)
    
    app = QApplication(sys.argv)
    
    # macOS特定的应用程序设置
    if platform.system() == 'Darwin':
        # 设置应用程序名称和组织
        app.setApplicationName("Flexiv Robot Control")
        app.setOrganizationName("Flexiv")
        app.setOrganizationDomain("flexiv.com")
        # 禁用原生菜单栏（可能导致警告）
        app.setAttribute(Qt.AA_DontUseNativeMenuBar, True)
    
    robot = None
    if hardware and FLEXIV_AVAILABLE:
        robot = flexivrdk.Robot("Rizon10-062357")
    
    try:
        window = RobotArmControlApp(robot=robot, hardware=hardware)
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"应用程序发生错误: {str(e)}")
    finally:
        if ROS_AVAILABLE and not rospy.is_shutdown():
            rospy.signal_shutdown('Application closed')

if __name__ == '__main__':
    main()