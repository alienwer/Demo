# 智能任务面板组件
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QPushButton, QLabel, QComboBox, QTextEdit, 
                             QListWidget, QListWidgetItem, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Dict, Any, List

class IntelligentTaskPanel(QWidget):
    """智能任务面板组件"""
    
    primitive_command = pyqtSignal(str, dict)  # 原语控制信号
    task_command = pyqtSignal(str, dict)  # 任务管理信号
    advanced_command = pyqtSignal(str, dict)  # 高级功能信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tasks = []
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 原语控制组件
        primitive_group = QGroupBox("🎯 运动原语")
        primitive_layout = QVBoxLayout(primitive_group)
        
        # 原语选择
        from app.utils.ui_utils import create_label, create_input_field
        self.combo_primitive = create_input_field("combo", options=[
            "点到点运动 (PTP)",
            "直线运动 (Linear)", 
            "圆弧运动 (Circular)",
            "力控运动 (Force Control)",
            "轨迹跟踪 (Trajectory)"
        ])
        primitive_layout.addWidget(create_label("选择运动原语:"))
        primitive_layout.addWidget(self.combo_primitive)
        
        # 原语参数配置
        param_layout = QHBoxLayout()
        self.spin_velocity = create_input_field("int", default_value=50, range_values=[1, 100])
        self.spin_velocity.setSuffix("%")
        
        self.spin_acceleration = create_input_field("int", default_value=30, range_values=[1, 100])
        self.spin_acceleration.setSuffix("%")
        
        param_layout.addWidget(create_label("速度:"))
        param_layout.addWidget(self.spin_velocity)
        param_layout.addWidget(create_label("加速度:"))
        param_layout.addWidget(self.spin_acceleration)
        primitive_layout.addLayout(param_layout)
        
        # 执行按钮
        from app.utils.ui_utils import create_button, BUTTON_STYLE_PRIMARY
        self.btn_execute_primitive = create_button("🚀 执行原语", style=BUTTON_STYLE_PRIMARY)
        primitive_layout.addWidget(self.btn_execute_primitive)
        
        layout.addWidget(primitive_group)
        
        # 任务管理组件
        task_group = QGroupBox("📋 任务管理")
        task_layout = QVBoxLayout(task_group)
        
        # 任务列表
        self.task_list = QListWidget()
        self.task_list.setMaximumHeight(120)
        task_layout.addWidget(create_label("当前任务队列:"))
        task_layout.addWidget(self.task_list)
        
        # 任务控制按钮
        task_control_layout = QHBoxLayout()
        self.btn_add_task = create_button("➕ 添加任务", style=BUTTON_STYLE_PRIMARY)
        self.btn_remove_task = create_button("➖ 移除任务", style=BUTTON_STYLE_SECONDARY)
        self.btn_clear_tasks = create_button("🗑️ 清空队列", style=BUTTON_STYLE_DANGER)
        self.btn_start_tasks = create_button("▶️ 开始执行", style=BUTTON_STYLE_PRIMARY)
        self.btn_pause_tasks = create_button("⏸️ 暂停", style=BUTTON_STYLE_SECONDARY)
        self.btn_stop_tasks = create_button("⏹️ 停止", style=BUTTON_STYLE_DANGER)
        
        for btn in [self.btn_add_task, self.btn_remove_task, self.btn_clear_tasks,
                   self.btn_start_tasks, self.btn_pause_tasks, self.btn_stop_tasks]:
            btn.setMaximumWidth(100)
            task_control_layout.addWidget(btn)
        
        task_layout.addLayout(task_control_layout)
        layout.addWidget(task_group)
        
        # 高级功能组件
        advanced_group = QGroupBox("🌟 高级功能")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # 力控设置
        force_control_layout = QHBoxLayout()
        self.check_force_control = QCheckBox("启用力控")
        self.combo_force_direction = create_input_field("combo", options=["X方向", "Y方向", "Z方向", "自定义方向"])
        
        force_control_layout.addWidget(self.check_force_control)
        force_control_layout.addWidget(create_label("力控方向:"))
        force_control_layout.addWidget(self.combo_force_direction)
        advanced_layout.addLayout(force_control_layout)
        
        # 安全设置
        safety_layout = QHBoxLayout()
        self.check_collision_avoidance = QCheckBox("碰撞检测")
        self.check_workspace_limits = QCheckBox("工作空间限制")
        self.check_force_limits = QCheckBox("力限制")
        
        safety_layout.addWidget(self.check_collision_avoidance)
        safety_layout.addWidget(self.check_workspace_limits)
        safety_layout.addWidget(self.check_force_limits)
        advanced_layout.addLayout(safety_layout)
        
        # 高级功能按钮
        advanced_btn_layout = QHBoxLayout()
        self.btn_calibration = create_button("📏 标定", style=BUTTON_STYLE_PRIMARY)
        self.btn_teach_mode = create_button("👆 示教模式", style=BUTTON_STYLE_PRIMARY)
        self.btn_optimize = create_button("⚡ 优化轨迹", style=BUTTON_STYLE_PRIMARY)
        
        for btn in [self.btn_calibration, self.btn_teach_mode, self.btn_optimize]:
            btn.setMaximumWidth(120)
            advanced_btn_layout.addWidget(btn)
        
        advanced_layout.addLayout(advanced_btn_layout)
        layout.addWidget(advanced_group)
        layout.addStretch()
        
    def setup_connections(self):
        """设置信号槽连接"""
        self.btn_execute_primitive.clicked.connect(self.on_execute_primitive)
        
        self.btn_add_task.clicked.connect(self.on_add_task)
        self.btn_remove_task.clicked.connect(self.on_remove_task)
        self.btn_clear_tasks.clicked.connect(self.on_clear_tasks)
        self.btn_start_tasks.clicked.connect(self.on_start_tasks)
        self.btn_pause_tasks.clicked.connect(self.on_pause_tasks)
        self.btn_stop_tasks.clicked.connect(self.on_stop_tasks)
        
        self.btn_calibration.clicked.connect(lambda: self.advanced_command.emit("calibration", {}))
        self.btn_teach_mode.clicked.connect(lambda: self.advanced_command.emit("teach_mode", {}))
        self.btn_optimize.clicked.connect(lambda: self.advanced_command.emit("optimize", {}))
        
    def on_execute_primitive(self):
        """执行运动原语"""
        primitive_type = self.combo_primitive.currentText()
        params = {
            'velocity': self.spin_velocity.value() / 100.0,
            'acceleration': self.spin_acceleration.value() / 100.0,
            'force_control': self.check_force_control.isChecked(),
            'force_direction': self.combo_force_direction.currentText()
        }
        self.primitive_command.emit(primitive_type, params)
        
    def on_add_task(self):
        """添加任务到队列"""
        primitive_type = self.combo_primitive.currentText()
        task_name = f"{primitive_type} - 任务{len(self.current_tasks) + 1}"
        
        item = QListWidgetItem(task_name)
        self.task_list.addItem(item)
        self.current_tasks.append({
            'name': task_name,
            'type': primitive_type,
            'params': self.get_current_params()
        })
        
    def on_remove_task(self):
        """移除选中任务"""
        current_row = self.task_list.currentRow()
        if current_row >= 0:
            self.task_list.takeItem(current_row)
            self.current_tasks.pop(current_row)
        
    def on_clear_tasks(self):
        """清空任务队列"""
        self.task_list.clear()
        self.current_tasks.clear()
        
    def on_start_tasks(self):
        """开始执行任务队列"""
        if self.current_tasks:
            self.task_command.emit("start", {'tasks': self.current_tasks})
        
    def on_pause_tasks(self):
        """暂停任务执行"""
        self.task_command.emit("pause", {})
        
    def on_stop_tasks(self):
        """停止任务执行"""
        self.task_command.emit("stop", {})
        
    def get_current_params(self) -> Dict[str, Any]:
        """获取当前参数设置"""
        return {
            'velocity': self.spin_velocity.value() / 100.0,
            'acceleration': self.spin_acceleration.value() / 100.0,
            'force_control': self.check_force_control.isChecked(),
            'force_direction': self.combo_force_direction.currentText(),
            'safety': {
                'collision_avoidance': self.check_collision_avoidance.isChecked(),
                'workspace_limits': self.check_workspace_limits.isChecked(),
                'force_limits': self.check_force_limits.isChecked()
            }
        }
    
    def update_task_status(self, status: Dict[str, Any]):
        """更新任务状态显示"""
        current_task = status.get('current_task', -1)
        task_state = status.get('state', 'idle')
        
        # 更新任务列表显示
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if i == current_task:
                prefix = "▶️" if task_state == 'running' else "⏸️"
                item.setText(f"{prefix} {item.text().split(' ', 1)[-1]}")
            else:
                item.setText(item.text().replace("▶️ ", "").replace("⏸️ ", ""))
        
    def cleanup(self):
        """清理资源"""
        print("清理智能任务面板资源")