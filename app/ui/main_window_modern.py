# Flexiv机器人控制系统 - 现代化主窗口实现
from PyQt5.QtWidgets import (QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QFrame, QLabel, QPushButton, QScrollArea, QGroupBox,
                             QComboBox, QSlider, QDoubleSpinBox, QCheckBox, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import os
from typing import Dict, List, Any

# 导入可视化面板组件
from .widgets.visualization_panel import VisualizationPanel

class ModernMainWindow(QMainWindow):
    """现代化Flexiv机器人控制系统主窗口"""
    
    robot_status_changed = pyqtSignal(dict)  # 机器人状态变化信号
    control_command = pyqtSignal(str, dict)  # 控制命令信号
    
    def __init__(self, hardware_mode: bool = True, debug_mode: bool = False):
        super().__init__()
        self.hardware_mode = hardware_mode
        self.debug_mode = debug_mode
        self.current_robot_state = {}
        
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()
        
    def setup_ui(self):
        """设置现代化UI布局"""
        self.setWindowTitle("Flexiv机器人控制系统 - 现代化界面")
        self.setGeometry(100, 100, 1600, 900)
        
        # 主分割器 - 左右分屏布局
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧控制面板区域
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 控制面板选项卡
        control_tabs = QTabWidget()
        control_tabs.addTab(self.create_robot_control_panel(), "机器人控制")
        control_tabs.addTab(self.create_intelligent_task_panel(), "智能任务")
        control_tabs.addTab(self.create_monitoring_panel(), "监控中心")
        control_tabs.addTab(self.create_system_settings_panel(), "系统设置")
        
        left_layout.addWidget(control_tabs)
        
        # 右侧3D可视化区域
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 3D可视化面板
        self.visualization_panel = VisualizationPanel()
        right_layout.addWidget(self.visualization_panel)
        
        # 设置分割器比例
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([400, 1200])
        
        self.setCentralWidget(main_splitter)
        
    def create_robot_control_panel(self) -> QWidget:
        """创建机器人控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 机器人操作组件
        operation_group = QGroupBox("机器人操作")
        operation_layout = QVBoxLayout(operation_group)
        
        # 模型加载按钮
        model_layout = QHBoxLayout()
        self.btn_load_model = QPushButton("📁 加载机器人模型")
        self.btn_load_model.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold;")
        model_layout.addWidget(self.btn_load_model)
        
        # 模型选择下拉框
        self.combo_model = QComboBox()
        self.combo_model.addItems([
            "flexiv_rizon10_kinematics.urdf",
            "flexiv_rizon10s_kinematics.urdf", 
            "flexiv_rizon4_kinematics.urdf",
            "flexiv_rizon4s_kinematics.urdf"
        ])
        self.combo_model.setMaximumWidth(150)
        model_layout.addWidget(self.combo_model)
        operation_layout.addLayout(model_layout)
        
        # 使能/禁用按钮
        btn_layout = QHBoxLayout()
        self.btn_enable = QPushButton("🟢 使能机器人")
        self.btn_disable = QPushButton("🔴 禁用机器人")
        btn_layout.addWidget(self.btn_enable)
        btn_layout.addWidget(self.btn_disable)
        operation_layout.addLayout(btn_layout)
        
        # 急停按钮
        self.btn_emergency = QPushButton("🛑 紧急停止")
        self.btn_emergency.setStyleSheet("background-color: #ff4444; color: white; font-weight: bold;")
        operation_layout.addWidget(self.btn_emergency)
        
        layout.addWidget(operation_group)
        
        # 夹爪控制组件
        gripper_group = QGroupBox("夹爪控制")
        gripper_layout = QVBoxLayout(gripper_group)
        
        # 夹爪开合控制
        grip_layout = QHBoxLayout()
        self.slider_gripper = QSlider(Qt.Horizontal)
        self.slider_gripper.setRange(0, 100)
        self.slider_gripper.setValue(50)
        self.btn_grip = QPushButton("抓取")
        self.btn_release = QPushButton("释放")
        
        grip_layout.addWidget(QLabel("开合度:"))
        grip_layout.addWidget(self.slider_gripper)
        grip_layout.addWidget(self.btn_grip)
        grip_layout.addWidget(self.btn_release)
        gripper_layout.addLayout(grip_layout)
        
        layout.addWidget(gripper_group)
        layout.addStretch()
        
        return panel
        
    def create_intelligent_task_panel(self) -> QWidget:
        """创建智能任务面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 原语控制组件
        primitive_group = QGroupBox("运动原语")
        primitive_layout = QVBoxLayout(primitive_group)
        
        # 原语选择
        self.combo_primitive = QComboBox()
        self.combo_primitive.addItems(["点到点运动", "直线运动", "圆弧运动", "力控运动"])
        primitive_layout.addWidget(QLabel("选择运动原语:"))
        primitive_layout.addWidget(self.combo_primitive)
        
        # 任务管理组件
        task_group = QGroupBox("任务管理")
        task_layout = QVBoxLayout(task_group)
        
        self.task_list = QTextEdit()
        self.task_list.setMaximumHeight(100)
        task_layout.addWidget(QLabel("当前任务:"))
        task_layout.addWidget(self.task_list)
        
        layout.addWidget(primitive_group)
        layout.addWidget(task_group)
        layout.addStretch()
        
        return panel
        
    def create_monitoring_panel(self) -> QWidget:
        """创建监控中心面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 状态监控组件
        status_group = QGroupBox("实时状态")
        status_layout = QVBoxLayout(status_group)
        
        self.lbl_connection = QLabel("🔴 未连接")
        self.lbl_mode = QLabel("模式: 未知")
        self.lbl_joints = QLabel("关节角度: 等待数据...")
        self.lbl_tcp = QLabel("TCP位姿: 等待数据...")
        
        for widget in [self.lbl_connection, self.lbl_mode, self.lbl_joints, self.lbl_tcp]:
            widget.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 4px;")
            status_layout.addWidget(widget)
        
        layout.addWidget(status_group)
        
        # 通信配置组件
        comm_group = QGroupBox("通信配置")
        comm_layout = QVBoxLayout(comm_group)
        
        self.combo_interface = QComboBox()
        self.combo_interface.addItems(["EtherCAT", "TCP/IP", "UDP", "RS232"])
        comm_layout.addWidget(QLabel("通信接口:"))
        comm_layout.addWidget(self.combo_interface)
        
        layout.addWidget(comm_group)
        layout.addStretch()
        
        return panel
        
    def create_system_settings_panel(self) -> QWidget:
        """创建系统设置面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 全局变量组件
        global_group = QGroupBox("全局配置")
        global_layout = QVBoxLayout(global_group)
        
        self.check_debug = QCheckBox("调试模式")
        self.check_logging = QCheckBox("启用日志记录")
        self.check_auto_reconnect = QCheckBox("自动重连")
        
        global_layout.addWidget(self.check_debug)
        global_layout.addWidget(self.check_logging)
        global_layout.addWidget(self.check_auto_reconnect)
        
        layout.addWidget(global_group)
        layout.addStretch()
        
        return panel
        
    def create_hud_widget(self) -> QWidget:
        """创建HUD显示组件"""
        # 现在HUD功能已集成到VisualizationPanel中
        return QWidget()
        
    def create_view_control_widget(self) -> QWidget:
        """创建视角控制组件"""
        # 现在视角控制功能已集成到VisualizationPanel中
        return QWidget()
        
    def setup_connections(self):
        """设置信号槽连接"""
        self.btn_load_model.clicked.connect(self._load_robot_model)
        self.btn_enable.clicked.connect(lambda: self.control_command.emit("enable", {}))
        self.btn_disable.clicked.connect(lambda: self.control_command.emit("disable", {}))
        self.btn_emergency.clicked.connect(lambda: self.control_command.emit("emergency_stop", {}))
        
        self.robot_status_changed.connect(self.update_ui)
        self.robot_status_changed.connect(self.visualization_panel.update_robot_state)
        
    def apply_styles(self):
        """应用现代化样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #3c3c3c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #3c3c3c;
            }
            QTabBar::tab {
                background-color: #4a4a4a;
                border: 1px solid #444;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #6a6a6a;
            }
        """)
        
    def _load_robot_model(self):
        """加载选定的机器人模型"""
        model_name = self.combo_model.currentText()
        
        # 构建模型文件路径
        import os
        resources_dir = os.path.join(os.path.dirname(__file__), 'resources')
        model_path = os.path.join(resources_dir, 'urdf', model_name)
        
        if os.path.exists(model_path):
            try:
                success = self.visualization_panel.load_robot_model(model_path)
                if success:
                    print(f"成功加载模型: {model_name}")
                    # 更新状态显示
                    self.lbl_connection.setText("🟡 模型已加载")
                else:
                    print(f"加载模型失败: {model_name}")
            except Exception as e:
                print(f"加载模型时出错: {e}")
        else:
            print(f"模型文件不存在: {model_path}")
    
    def update_ui(self, state: Dict[str, Any]):
        """更新UI显示"""
        self.current_robot_state = state
        
        # 更新状态显示
        if state.get('connected', False):
            self.lbl_connection.setText("🟢 已连接")
        else:
            self.lbl_connection.setText("🔴 未连接")
        
        # 更新模式显示
        mode = state.get('mode', 'unknown')
        self.lbl_mode.setText(f"模式: {mode}")
        
        # 更新关节角度
        joints = state.get('joint_positions', [])
        if joints:
            joints_str = ", ".join(f"{j:.2f}" for j in joints)
            self.lbl_joints.setText(f"关节角度: [{joints_str}]")
        
        # 更新TCP位姿
        tcp_pose = state.get('tcp_pose', [])
        if tcp_pose:
            tcp_str = ", ".join(f"{p:.3f}" for p in tcp_pose[:3])  # 只显示位置
            self.lbl_tcp.setText(f"TCP位姿: [{tcp_str}]")
        
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'visualization_panel'):
            self.visualization_panel.cleanup()
        print("清理现代化主窗口资源")

# 组件工厂函数
def create_modern_main_window(hardware_mode=True, debug_mode=False) -> ModernMainWindow:
    """创建现代化主窗口实例"""
    return ModernMainWindow(hardware_mode, debug_mode)