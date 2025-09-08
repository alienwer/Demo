# 机器人控制面板组件
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QPushButton, QLabel, QSlider, QComboBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Dict, Any

class RobotControlPanel(QWidget):
    """机器人控制面板组件"""
    
    control_command = pyqtSignal(str, dict)  # 控制命令信号
    gripper_command = pyqtSignal(float, str)  # 夹爪控制信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 机器人操作组件
        operation_group = QGroupBox("🤖 机器人操作")
        operation_layout = QVBoxLayout(operation_group)
        
        # 使能/禁用按钮
        from app.utils.ui_utils import create_button, BUTTON_STYLE_PRIMARY, BUTTON_STYLE_DANGER
        btn_layout = QHBoxLayout()
        self.btn_enable = create_button("🟢 使能机器人", style=BUTTON_STYLE_PRIMARY)
        self.btn_disable = create_button("🔴 禁用机器人", style=BUTTON_STYLE_DANGER)
        
        btn_layout.addWidget(self.btn_enable)
        btn_layout.addWidget(self.btn_disable)
        operation_layout.addLayout(btn_layout)
        
        # 急停按钮
        self.btn_emergency = create_button("🛑 紧急停止", style=BUTTON_STYLE_DANGER)
        operation_layout.addWidget(self.btn_emergency)
        
        layout.addWidget(operation_group)
        
        # 夹爪控制组件
        gripper_group = QGroupBox("🔧 夹爪控制")
        gripper_layout = QVBoxLayout(gripper_group)
        
        # 夹爪开合控制
        from app.utils.ui_utils import create_label
        grip_control_layout = QHBoxLayout()
        self.slider_gripper = QSlider(Qt.Horizontal)
        self.slider_gripper.setRange(0, 100)
        self.slider_gripper.setValue(50)
        self.slider_gripper.setTickPosition(QSlider.TicksBelow)
        self.slider_gripper.setTickInterval(10)
        
        self.btn_grip = create_button("🤏 抓取", style=BUTTON_STYLE_PRIMARY)
        self.btn_release = create_button("👆 释放", style=BUTTON_STYLE_SECONDARY)
        
        grip_control_layout.addWidget(create_label("开合度:"))
        grip_control_layout.addWidget(self.slider_gripper)
        grip_control_layout.addWidget(self.btn_grip)
        grip_control_layout.addWidget(self.btn_release)
        gripper_layout.addLayout(grip_control_layout)
        
        # 夹爪状态显示
        self.lbl_gripper_status = create_label("状态: 就绪", background_color="#e8f5e8", padding=4, border_radius=3)
        gripper_layout.addWidget(self.lbl_gripper_status)
        
        layout.addWidget(gripper_group)
        
        # 运动模式选择
        mode_group = QGroupBox("🚀 运动模式")
        mode_layout = QVBoxLayout(mode_group)
        
        from app.utils.ui_utils import create_input_field
        self.combo_motion_mode = create_input_field("combo", options=[
            "位置控制模式", 
            "速度控制模式", 
            "力控模式", 
            "阻抗控制模式"
        ])
        mode_layout.addWidget(create_label("选择控制模式:"))
        mode_layout.addWidget(self.combo_motion_mode)
        
        # 柔顺性控制
        compliance_layout = QHBoxLayout()
        self.check_compliance = QCheckBox("启用柔顺控制")
        self.slider_stiffness = QSlider(Qt.Horizontal)
        self.slider_stiffness.setRange(1, 100)
        self.slider_stiffness.setValue(50)
        
        compliance_layout.addWidget(self.check_compliance)
        compliance_layout.addWidget(create_label("刚度:"))
        compliance_layout.addWidget(self.slider_stiffness)
        mode_layout.addLayout(compliance_layout)
        
        layout.addWidget(mode_group)
        layout.addStretch()
        
    def setup_connections(self):
        """设置信号槽连接"""
        self.btn_enable.clicked.connect(lambda: self.control_command.emit("enable", {}))
        self.btn_disable.clicked.connect(lambda: self.control_command.emit("disable", {}))
        self.btn_emergency.clicked.connect(lambda: self.control_command.emit("emergency_stop", {}))
        
        self.btn_grip.clicked.connect(lambda: self.gripper_command.emit(
            self.slider_gripper.value() / 100.0, "grip"
        ))
        self.btn_release.clicked.connect(lambda: self.gripper_command.emit(0.0, "release"))
        
        self.slider_gripper.valueChanged.connect(self.on_gripper_slider_changed)
        
    def on_gripper_slider_changed(self, value):
        """夹爪滑块值变化处理"""
        self.lbl_gripper_status.setText(f"开合度: {value}%")
        
    def update_robot_state(self, state: Dict[str, Any]):
        """更新机器人状态显示"""
        # 更新使能状态
        enabled = state.get('enabled', False)
        if enabled:
            self.btn_enable.setEnabled(False)
            self.btn_disable.setEnabled(True)
        else:
            self.btn_enable.setEnabled(True)
            self.btn_disable.setEnabled(False)
        
        # 更新急停状态
        emergency_stop = state.get('emergency_stop', False)
        if emergency_stop:
            self.btn_emergency.setStyleSheet("background-color: #ff0000; color: white; font-weight: bold;")
        else:
            self.btn_emergency.setStyleSheet("background-color: #ff4444; color: white; font-weight: bold;")
        
        # 更新夹爪状态
        gripper_state = state.get('gripper_state', {})
        if gripper_state:
            position = gripper_state.get('position', 0)
            self.slider_gripper.setValue(int(position * 100))
            
            status = gripper_state.get('status', 'unknown')
            status_texts = {
                'gripping': '抓取中',
                'releasing': '释放中', 
                'ready': '就绪',
                'error': '错误'
            }
            self.lbl_gripper_status.setText(f"状态: {status_texts.get(status, '未知')}")
    
    def set_control_mode(self, mode: str):
        """设置控制模式"""
        mode_mapping = {
            'position': '位置控制模式',
            'velocity': '速度控制模式', 
            'force': '力控模式',
            'impedance': '阻抗控制模式'
        }
        
        if mode in mode_mapping:
            index = self.combo_motion_mode.findText(mode_mapping[mode])
            if index >= 0:
                self.combo_motion_mode.setCurrentIndex(index)
    
    def get_control_settings(self) -> Dict[str, Any]:
        """获取当前控制设置"""
        return {
            'motion_mode': self.combo_motion_mode.currentText(),
            'compliance_enabled': self.check_compliance.isChecked(),
            'stiffness': self.slider_stiffness.value() / 100.0
        }
    
    def cleanup(self):
        """清理资源"""
        print("清理机器人控制面板资源")