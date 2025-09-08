# 监控中心面板组件
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QComboBox, QPushButton, QProgressBar,
                             QTextEdit, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QPalette
from typing import Dict, Any
import time

class MonitoringPanel(QWidget):
    """监控中心面板组件"""
    
    config_changed = pyqtSignal(str, dict)  # 配置变化信号
    diagnostic_command = pyqtSignal(str)   # 诊断命令信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection_status = "disconnected"
        self.last_update_time = time.time()
        self.setup_ui()
        self.setup_connections()
        self.setup_timers()
        
    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 状态监控组件
        status_group = QGroupBox("📊 实时状态监控")
        status_layout = QVBoxLayout(status_group)
        
        # 连接状态
        from app.utils.ui_utils import create_label, create_button, BUTTON_STYLE_SECONDARY
        connection_layout = QHBoxLayout()
        self.lbl_connection = create_label("🔴 未连接", bold=True, font_size=14)
        self.btn_reconnect = create_button("🔄 重连", style=BUTTON_STYLE_SECONDARY)
        
        connection_layout.addWidget(self.lbl_connection)
        connection_layout.addWidget(self.btn_reconnect)
        status_layout.addLayout(connection_layout)
        
        # 系统状态
        system_layout = QHBoxLayout()
        self.lbl_mode = create_label("模式: 未知", background_color="#f0f0f0", padding=4, border_radius=3)
        self.lbl_safety = create_label("安全状态: 正常", background_color="#f0f0f0", padding=4, border_radius=3)
        self.lbl_update_rate = create_label("更新率: 0 Hz", background_color="#f0f0f0", padding=4, border_radius=3)
        
        for widget in [self.lbl_mode, self.lbl_safety, self.lbl_update_rate]:
            system_layout.addWidget(widget)
        
        status_layout.addLayout(system_layout)
        
        # 性能指标
        performance_layout = QVBoxLayout()
        
        # CPU使用率
        cpu_layout = QHBoxLayout()
        self.lbl_cpu = create_label("CPU: 0%")
        self.progress_cpu = QProgressBar()
        self.progress_cpu.setRange(0, 100)
        self.progress_cpu.setValue(0)
        
        cpu_layout.addWidget(self.lbl_cpu)
        cpu_layout.addWidget(self.progress_cpu)
        performance_layout.addLayout(cpu_layout)
        
        # 内存使用率
        memory_layout = QHBoxLayout()
        self.lbl_memory = create_label("内存: 0%")
        self.progress_memory = QProgressBar()
        self.progress_memory.setRange(0, 100)
        self.progress_memory.setValue(0)
        
        memory_layout.addWidget(self.lbl_memory)
        memory_layout.addWidget(self.progress_memory)
        performance_layout.addLayout(memory_layout)
        
        status_layout.addLayout(performance_layout)
        layout.addWidget(status_group)
        
        # 详细状态显示
        detail_group = QGroupBox("🔍 详细状态信息")
        detail_layout = QVBoxLayout(detail_group)
        
        self.text_status = QTextEdit()
        self.text_status.setMaximumHeight(150)
        self.text_status.setReadOnly(True)
        detail_layout.addWidget(self.text_status)
        
        layout.addWidget(detail_group)
        
        # 通信配置组件
        comm_group = QGroupBox("📡 通信配置")
        comm_layout = QVBoxLayout(comm_group)
        
        # 通信接口选择
        interface_layout = QHBoxLayout()
        self.combo_interface = create_input_field("combo", options=["EtherCAT", "TCP/IP", "UDP", "RS232", "模拟接口"])
        
        interface_layout.addWidget(create_label("通信接口:"))
        interface_layout.addWidget(self.combo_interface)
        comm_layout.addLayout(interface_layout)
        
        # 通信参数
        param_layout = QHBoxLayout()
        self.spin_timeout = create_input_field("int", default_value=10, range_values=[1, 60])
        self.spin_timeout.setSuffix("s")
        
        self.spin_retries = create_input_field("int", default_value=3, range_values=[0, 10])
        
        param_layout.addWidget(create_label("超时时间:"))
        param_layout.addWidget(self.spin_timeout)
        param_layout.addWidget(create_label("重试次数:"))
        param_layout.addWidget(self.spin_retries)
        comm_layout.addLayout(param_layout)
        
        # 通信控制
        control_layout = QHBoxLayout()
        self.btn_test_connection = create_button("🧪 测试连接", style=BUTTON_STYLE_PRIMARY)
        self.btn_apply_config = create_button("💾 应用配置", style=BUTTON_STYLE_SECONDARY)
        
        control_layout.addWidget(self.btn_test_connection)
        control_layout.addWidget(self.btn_apply_config)
        comm_layout.addLayout(control_layout)
        
        layout.addWidget(comm_group)
        layout.addStretch()
        
    def setup_connections(self):
        """设置信号槽连接"""
        self.btn_reconnect.clicked.connect(self.on_reconnect)
        self.btn_test_connection.clicked.connect(self.on_test_connection)
        self.btn_apply_config.clicked.connect(self.on_apply_config)
        
        self.combo_interface.currentTextChanged.connect(self.on_interface_changed)
        
    def setup_timers(self):
        """设置定时器"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_performance)
        self.update_timer.start(1000)  # 1秒更新一次
        
    def on_reconnect(self):
        """重连按钮点击"""
        self.diagnostic_command.emit("reconnect")
        
    def on_test_connection(self):
        """测试连接"""
        self.diagnostic_command.emit("test_connection")
        
    def on_apply_config(self):
        """应用通信配置"""
        config = {
            'interface': self.combo_interface.currentText(),
            'timeout': self.spin_timeout.value(),
            'retries': self.spin_retries.value()
        }
        self.config_changed.emit("communication", config)
        
    def on_interface_changed(self, interface):
        """通信接口变化"""
        # 根据接口类型调整默认参数
        if interface == "EtherCAT":
            self.spin_timeout.setValue(5)
        elif interface == "TCP/IP":
            self.spin_timeout.setValue(10)
        elif interface == "UDP":
            self.spin_timeout.setValue(3)
        elif interface == "RS232":
            self.spin_timeout.setValue(15)
        
    def update_robot_state(self, state: Dict[str, Any]):
        """更新机器人状态显示"""
        current_time = time.time()
        update_interval = current_time - self.last_update_time
        update_rate = 1.0 / update_interval if update_interval > 0 else 0
        self.last_update_time = current_time
        
        # 更新连接状态
        connected = state.get('connected', False)
        if connected:
            self.connection_status = "connected"
            self.lbl_connection.setText("🟢 已连接")
            self.lbl_connection.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
        else:
            self.connection_status = "disconnected"
            self.lbl_connection.setText("🔴 未连接")
            self.lbl_connection.setStyleSheet("color: #f44336; font-weight: bold; font-size: 14px;")
        
        # 更新模式和安全状态
        mode = state.get('mode', 'unknown')
        self.lbl_mode.setText(f"模式: {mode}")
        
        safety_status = state.get('safety_status', 'normal')
        safety_texts = {
            'normal': '正常',
            'warning': '警告', 
            'error': '错误',
            'emergency': '紧急停止'
        }
        safety_color = {
            'normal': '#4CAF50',
            'warning': '#FF9800',
            'error': '#f44336', 
            'emergency': '#d32f2f'
        }
        self.lbl_safety.setText(f"安全状态: {safety_texts.get(safety_status, '未知')}")
        self.lbl_safety.setStyleSheet(f"background-color: {safety_color.get(safety_status, '#f0f0f0')}; color: white; padding: 4px; border-radius: 3px;")
        
        # 更新率
        self.lbl_update_rate.setText(f"更新率: {update_rate:.1f} Hz")
        
        # 更新详细状态信息
        status_text = f"更新时间: {time.strftime('%H:%M:%S')}\n"
        status_text += f"连接状态: {'已连接' if connected else '未连接'}\n"
        status_text += f"控制模式: {mode}\n"
        status_text += f"安全状态: {safety_status}\n"
        
        # 添加关节信息
        joints = state.get('joint_positions', [])
        if joints:
            status_text += f"关节角度: [{', '.join(f'{j:.2f}' for j in joints)}]\n"
        
        # 添加TCP信息
        tcp_pose = state.get('tcp_pose', [])
        if tcp_pose:
            status_text += f"TCP位姿: [{', '.join(f'{p:.3f}' for p in tcp_pose[:3])}]\n"
        
        self.text_status.setText(status_text)
        
    def update_performance(self):
        """更新性能指标（模拟数据）"""
        # 模拟CPU和内存使用率
        import random
        cpu_usage = random.randint(5, 40)
        memory_usage = random.randint(20, 60)
        
        self.lbl_cpu.setText(f"CPU: {cpu_usage}%")
        self.progress_cpu.setValue(cpu_usage)
        
        self.lbl_memory.setText(f"内存: {memory_usage}%")
        self.progress_memory.setValue(memory_usage)
        
        # 根据使用率设置颜色
        for progress, usage in [(self.progress_cpu, cpu_usage), (self.progress_memory, memory_usage)]:
            if usage > 80:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #f44336; }")
            elif usage > 60:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #FF9800; }")
            else:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
    
    def set_connection_status(self, status: str, message: str = ""):
        """设置连接状态"""
        self.connection_status = status
        status_info = {
            "connected": ("🟢 已连接", "#4CAF50"),
            "connecting": ("🟡 连接中...", "#FF9800"),
            "disconnected": ("🔴 未连接", "#f44336"),
            "error": ("⚫ 连接错误", "#9e9e9e")
        }
        
        text, color = status_info.get(status, ("❓ 未知状态", "#9e9e9e"))
        if message:
            text = f"{text} - {message}"
            
        self.lbl_connection.setText(text)
        self.lbl_connection.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
    
    def cleanup(self):
        """清理资源"""
        self.update_timer.stop()
        print("清理监控中心面板资源")