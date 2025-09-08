'''
Author: LK
Date: 2025-01-XX XX:XX:XX
LastEditTime: 2025-01-XX XX:XX:XX
LastEditors: LK
FilePath: /Demo/app/ui/primitive_control_widget.py
'''

import json
from typing import Dict, Any, List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QLineEdit, QDoubleSpinBox, 
                             QSpinBox, QGroupBox, QScrollArea, QTextEdit,
                             QTabWidget, QTreeWidget, QTreeWidgetItem,
                             QSplitter, QCheckBox, QSlider, QFormLayout,
                             QMessageBox, QProgressBar, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
import qtawesome as qta

from app.control.primitive_manager import PrimitiveManager, PrimitiveParams, PrimitiveCategory

class CoordInputWidget(QWidget):
    """坐标输入控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 位置输入
        pos_group = QGroupBox("位置 (m)")
        pos_layout = QHBoxLayout(pos_group)
        
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(-10.0, 10.0)
        self.x_spin.setDecimals(3)
        self.x_spin.setSingleStep(0.001)
        
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(-10.0, 10.0)
        self.y_spin.setDecimals(3)
        self.y_spin.setSingleStep(0.001)
        
        self.z_spin = QDoubleSpinBox()
        self.z_spin.setRange(-10.0, 10.0)
        self.z_spin.setDecimals(3)
        self.z_spin.setSingleStep(0.001)
        
        pos_layout.addWidget(QLabel("X:"))
        pos_layout.addWidget(self.x_spin)
        pos_layout.addWidget(QLabel("Y:"))
        pos_layout.addWidget(self.y_spin)
        pos_layout.addWidget(QLabel("Z:"))
        pos_layout.addWidget(self.z_spin)
        
        # 姿态输入
        rot_group = QGroupBox("姿态 (deg)")
        rot_layout = QHBoxLayout(rot_group)
        
        self.rx_spin = QDoubleSpinBox()
        self.rx_spin.setRange(-360.0, 360.0)
        self.rx_spin.setDecimals(1)
        self.rx_spin.setSingleStep(1.0)
        
        self.ry_spin = QDoubleSpinBox()
        self.ry_spin.setRange(-360.0, 360.0)
        self.ry_spin.setDecimals(1)
        self.ry_spin.setSingleStep(1.0)
        
        self.rz_spin = QDoubleSpinBox()
        self.rz_spin.setRange(-360.0, 360.0)
        self.rz_spin.setDecimals(1)
        self.rz_spin.setSingleStep(1.0)
        
        rot_layout.addWidget(QLabel("Rx:"))
        rot_layout.addWidget(self.rx_spin)
        rot_layout.addWidget(QLabel("Ry:"))
        rot_layout.addWidget(self.ry_spin)
        rot_layout.addWidget(QLabel("Rz:"))
        rot_layout.addWidget(self.rz_spin)
        
        # 坐标系选择
        ref_group = QGroupBox("参考坐标系")
        ref_layout = QHBoxLayout(ref_group)
        
        self.ref_coord_combo = QComboBox()
        self.ref_coord_combo.addItems(["WORLD", "WORK", "TCP", "TCP_START", "TRAJ_START", "TRAJ_GOAL", "TRAJ_PREV"])
        
        self.ref_origin_edit = QLineEdit("WORLD_ORIGIN")
        
        ref_layout.addWidget(QLabel("坐标系:"))
        ref_layout.addWidget(self.ref_coord_combo)
        ref_layout.addWidget(QLabel("原点:"))
        ref_layout.addWidget(self.ref_origin_edit)
        
        layout.addWidget(pos_group)
        layout.addWidget(rot_group)
        layout.addWidget(ref_group)
    
    def get_value(self) -> Dict[str, Any]:
        """获取坐标值"""
        return {
            "pos": [self.x_spin.value(), self.y_spin.value(), self.z_spin.value()],
            "rot": [self.rx_spin.value(), self.ry_spin.value(), self.rz_spin.value()],
            "ref": [self.ref_coord_combo.currentText(), self.ref_origin_edit.text()]
        }
    
    def set_value(self, value: Dict[str, Any]):
        """设置坐标值"""
        if "pos" in value:
            pos = value["pos"]
            self.x_spin.setValue(pos[0])
            self.y_spin.setValue(pos[1])
            self.z_spin.setValue(pos[2])
        
        if "rot" in value:
            rot = value["rot"]
            self.rx_spin.setValue(rot[0])
            self.ry_spin.setValue(rot[1])
            self.rz_spin.setValue(rot[2])
        
        if "ref" in value:
            ref = value["ref"]
            self.ref_coord_combo.setCurrentText(ref[0])
            self.ref_origin_edit.setText(ref[1])

class JointInputWidget(QWidget):
    """关节位置输入控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 关节角度输入
        joints_group = QGroupBox("关节角度 (deg)")
        joints_layout = QHBoxLayout(joints_group)
        
        self.joint_spins = []
        for i in range(7):
            spin = QDoubleSpinBox()
            spin.setRange(-360.0, 360.0)
            spin.setDecimals(1)
            spin.setSingleStep(1.0)
            self.joint_spins.append(spin)
            
            joints_layout.addWidget(QLabel(f"J{i+1}:"))
            joints_layout.addWidget(spin)
        
        # 外部轴输入
        external_group = QGroupBox("外部轴 (可选)")
        external_layout = QHBoxLayout(external_group)
        
        self.external_spins = []
        for i in range(2):
            spin = QDoubleSpinBox()
            spin.setRange(-1000.0, 1000.0)
            spin.setDecimals(1)
            spin.setSingleStep(1.0)
            self.external_spins.append(spin)
            
            external_layout.addWidget(QLabel(f"E{i+1}:"))
            external_layout.addWidget(spin)
        
        layout.addWidget(joints_group)
        layout.addWidget(external_group)
    
    def get_value(self) -> Dict[str, Any]:
        """获取关节位置值"""
        joints = [spin.value() for spin in self.joint_spins]
        external = [spin.value() for spin in self.external_spins]
        
        return {
            "joints": joints,
            "external": external
        }
    
    def set_value(self, value: Dict[str, Any]):
        """设置关节位置值"""
        if "joints" in value:
            joints = value["joints"]
            for i, joint_value in enumerate(joints[:7]):
                if i < len(self.joint_spins):
                    self.joint_spins[i].setValue(joint_value)
        
        if "external" in value:
            external = value["external"]
            for i, ext_value in enumerate(external[:2]):
                if i < len(self.external_spins):
                    self.external_spins[i].setValue(ext_value)

class PrimitiveParamWidget(QWidget):
    """Primitive参数配置控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.param_widgets = {}
        self.current_primitive = None
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.param_container = QWidget()
        self.param_layout = QFormLayout(self.param_container)
        
        self.scroll_area.setWidget(self.param_container)
        self.layout.addWidget(self.scroll_area)
        
        # 提示标签
        self.hint_label = QLabel("请选择一个Primitive来配置参数")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet("color: gray; font-style: italic;")
        self.layout.addWidget(self.hint_label)
    
    def set_primitive(self, primitive_name: str):
        """设置当前Primitive并生成参数控件"""
        self.current_primitive = primitive_name
        self.clear_params()
        
        if not primitive_name:
            self.hint_label.show()
            return
        
        self.hint_label.hide()
        
        schema = PrimitiveParams.get_primitive_schema(primitive_name)
        if not schema:
            return
        
        params = schema.get("params", {})
        required_params = schema.get("required", [])
        
        for param_name, param_info in params.items():
            self.create_param_widget(param_name, param_info, param_name in required_params)
    
    def create_param_widget(self, param_name: str, param_info: Dict[str, Any], is_required: bool):
        """创建参数控件（使用UI工具函数）"""
        from app.utils.ui_utils import create_parameter_widget
        
        param_type = param_info.get("type", "string")
        default_value = param_info.get("default")
        param_range = param_info.get("range")
        options = param_info.get("options")
        unit = param_info.get("unit", "")
        
        # 使用工具函数创建标签和控件
        label, widget = create_parameter_widget(param_name, param_info, is_required)
        
        # 特殊处理COORD和JPOS类型（需要自定义控件）
        if param_type == "COORD":
            widget = CoordInputWidget()
            if default_value:
                widget.set_value(default_value)
            
        elif param_type == "JPOS":
            widget = JointInputWidget()
            if default_value:
                widget.set_value(default_value)
        
        elif param_type.startswith("VEC_"):
            # 向量类型（需要自定义处理）
            dim = int(param_type.split("_")[1][0])  # 提取维度
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            spins = []
            for i in range(dim):
                spin = QDoubleSpinBox()
                spin.setRange(-1000.0, 1000.0)
                spin.setDecimals(3)
                spin.setSingleStep(0.001)
                spins.append(spin)
                layout.addWidget(spin)
            
            widget.spins = spins  # 保存引用
            
            if default_value and isinstance(default_value, list):
                for i, val in enumerate(default_value[:dim]):
                    spins[i].setValue(val)
        
        # 对于其他类型，使用工具函数创建的widget
        if widget:
            self.param_widgets[param_name] = widget
            self.param_layout.addRow(label, widget)
    
    def get_params(self) -> Dict[str, Any]:
        """获取所有参数值"""
        params = {}
        
        for param_name, widget in self.param_widgets.items():
            if isinstance(widget, CoordInputWidget):
                params[param_name] = widget.get_value()
            elif isinstance(widget, JointInputWidget):
                params[param_name] = widget.get_value()
            elif isinstance(widget, QDoubleSpinBox):
                params[param_name] = widget.value()
            elif isinstance(widget, QSpinBox):
                params[param_name] = widget.value()
            elif isinstance(widget, QComboBox):
                params[param_name] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:
                    params[param_name] = text
            elif hasattr(widget, 'spins'):  # 向量类型
                params[param_name] = [spin.value() for spin in widget.spins]
        
        return params
    
    def clear_params(self):
        """清空参数控件"""
        for i in reversed(range(self.param_layout.count())):
            item = self.param_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        self.param_widgets.clear()

class PrimitiveControlWidget(QWidget):
    """Primitive控制主界面"""
    
    # 信号定义
    primitive_execute_requested = pyqtSignal(str, dict)  # primitive_name, params
    primitive_stop_requested = pyqtSignal()
    
    def __init__(self, primitive_manager: PrimitiveManager, parent=None):
        super().__init__(parent)
        self.primitive_manager = primitive_manager
        self.current_primitive = None
        self.execution_progress = 0
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("Primitive 控制面板")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：Primitive选择
        left_widget = self.create_primitive_selection_widget()
        main_splitter.addWidget(left_widget)
        
        # 右侧：参数配置和控制
        right_widget = self.create_control_widget()
        main_splitter.addWidget(right_widget)
        
        main_splitter.setSizes([300, 500])
        layout.addWidget(main_splitter)
        
        # 状态栏
        self.create_status_bar(layout)
    
    def create_primitive_selection_widget(self) -> QWidget:
        """创建Primitive选择控件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入Primitive名称...")
        self.search_edit.textChanged.connect(self.filter_primitives)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
        
        # Primitive树形列表
        self.primitive_tree = QTreeWidget()
        self.primitive_tree.setHeaderLabel("可用 Primitives")
        self.primitive_tree.itemClicked.connect(self.on_primitive_selected)
        
        self.populate_primitive_tree()
        
        layout.addWidget(self.primitive_tree)
        
        return widget
    
    def create_control_widget(self) -> QWidget:
        """创建控制控件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 当前选择的Primitive信息
        info_group = QGroupBox("Primitive 信息")
        info_layout = QVBoxLayout(info_group)
        
        self.primitive_name_label = QLabel("未选择")
        self.primitive_name_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.primitive_desc_label = QLabel("")
        self.primitive_desc_label.setWordWrap(True)
        self.primitive_desc_label.setStyleSheet("color: gray;")
        
        info_layout.addWidget(QLabel("名称:"))
        info_layout.addWidget(self.primitive_name_label)
        info_layout.addWidget(QLabel("描述:"))
        info_layout.addWidget(self.primitive_desc_label)
        
        layout.addWidget(info_group)
        
        # 参数配置
        param_group = QGroupBox("参数配置")
        param_layout = QVBoxLayout(param_group)
        
        self.param_widget = PrimitiveParamWidget()
        param_layout.addWidget(self.param_widget)
        
        layout.addWidget(param_group)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("执行 Primitive")
        self.execute_btn.setIcon(qta.icon('fa.play'))
        self.execute_btn.clicked.connect(self.execute_primitive)
        self.execute_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setIcon(qta.icon('fa.stop'))
        self.stop_btn.clicked.connect(self.stop_primitive)
        self.stop_btn.setEnabled(False)
        
        self.validate_btn = QPushButton("验证参数")
        self.validate_btn.setIcon(qta.icon('fa.check'))
        self.validate_btn.clicked.connect(self.validate_params)
        self.validate_btn.setEnabled(False)
        
        control_layout.addWidget(self.execute_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.validate_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        return widget
    
    def create_status_bar(self, parent_layout):
        """创建状态栏"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("就绪")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(QLabel("状态:"))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(status_frame)
    
    def populate_primitive_tree(self):
        """填充Primitive树形列表"""
        self.primitive_tree.clear()
        
        available_primitives = self.primitive_manager.get_available_primitives()
        
        for category, primitives in available_primitives.items():
            category_item = QTreeWidgetItem([category.value])
            category_item.setFont(0, QFont("Arial", 10, QFont.Bold))
            
            for primitive_name in primitives:
                primitive_item = QTreeWidgetItem([primitive_name])
                primitive_item.setData(0, Qt.UserRole, primitive_name)
                category_item.addChild(primitive_item)
            
            self.primitive_tree.addTopLevelItem(category_item)
            category_item.setExpanded(True)
    
    def filter_primitives(self, text: str):
        """过滤Primitive列表"""
        text = text.lower()
        
        for i in range(self.primitive_tree.topLevelItemCount()):
            category_item = self.primitive_tree.topLevelItem(i)
            category_visible = False
            
            for j in range(category_item.childCount()):
                primitive_item = category_item.child(j)
                primitive_name = primitive_item.text(0).lower()
                
                if text in primitive_name:
                    primitive_item.setHidden(False)
                    category_visible = True
                else:
                    primitive_item.setHidden(True)
            
            category_item.setHidden(not category_visible)
    
    def on_primitive_selected(self, item: QTreeWidgetItem, column: int):
        """Primitive选择事件"""
        primitive_name = item.data(0, Qt.UserRole)
        if not primitive_name:
            return
        
        self.current_primitive = primitive_name
        
        # 更新信息显示
        schema = PrimitiveParams.get_primitive_schema(primitive_name)
        self.primitive_name_label.setText(primitive_name)
        self.primitive_desc_label.setText(schema.get("description", "无描述"))
        
        # 更新参数配置
        self.param_widget.set_primitive(primitive_name)
        
        # 启用控制按钮
        self.execute_btn.setEnabled(True)
        self.validate_btn.setEnabled(True)
    
    def validate_params(self):
        """验证参数"""
        if not self.current_primitive:
            return
        
        params = self.param_widget.get_params()
        is_valid, message = PrimitiveParams.validate_params(self.current_primitive, params)
        
        if is_valid:
            QMessageBox.information(self, "参数验证", "参数验证通过！")
        else:
            QMessageBox.warning(self, "参数验证失败", message)
    
    def execute_primitive(self):
        """执行Primitive"""
        if not self.current_primitive:
            return
        
        params = self.param_widget.get_params()
        is_valid, message = PrimitiveParams.validate_params(self.current_primitive, params)
        
        if not is_valid:
            QMessageBox.warning(self, "参数错误", f"参数验证失败：{message}")
            return
        
        # 发送执行请求信号
        self.primitive_execute_requested.emit(self.current_primitive, params)
    
    def stop_primitive(self):
        """停止Primitive"""
        self.primitive_stop_requested.emit()
    
    def connect_signals(self):
        """连接信号"""
        self.primitive_manager.primitive_started.connect(self.on_primitive_started)
        self.primitive_manager.primitive_completed.connect(self.on_primitive_completed)
        self.primitive_manager.primitive_failed.connect(self.on_primitive_failed)
        self.primitive_manager.primitive_progress.connect(self.on_primitive_progress)
        self.primitive_manager.status_updated.connect(self.on_status_updated)
    
    def on_primitive_started(self, primitive_name: str):
        """Primitive开始执行"""
        self.execute_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"正在执行: {primitive_name}")
    
    def on_primitive_completed(self, primitive_name: str, result: dict):
        """Primitive执行完成"""
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"执行完成: {primitive_name}")
    
    def on_primitive_failed(self, primitive_name: str, error_msg: str):
        """Primitive执行失败"""
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"执行失败: {primitive_name}")
        
        QMessageBox.critical(self, "执行失败", f"Primitive '{primitive_name}' 执行失败：\n{error_msg}")
    
    def on_primitive_progress(self, primitive_name: str, state: dict):
        """Primitive执行进度更新"""
        if "progress" in state:
            progress = int(state["progress"] * 100)
            self.progress_bar.setValue(progress)
        
        if "reachedTarget" in state and state["reachedTarget"]:
            self.progress_bar.setValue(100)
    
    def on_status_updated(self, message: str):
        """状态更新"""
        if not self.primitive_manager.is_executing():
            self.status_label.setText(message)