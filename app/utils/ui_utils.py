"""
UI工具函数模块 - 提取通用UI组件创建函数
用于消除代码重复，提供一致的UI创建模式
"""

from typing import Dict, Any, List, Optional, Union
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
                             QPushButton, QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox,
                             QCheckBox, QSplitter, QTreeWidget, QScrollArea, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import qtawesome as qta


def create_group_box(title: str, layout_type: str = "vertical", 
                     checkable: bool = False, checked: bool = False) -> QGroupBox:
    """
    创建标准化的分组框
    
    Args:
        title: 分组框标题
        layout_type: 布局类型，"vertical" 或 "horizontal"
        checkable: 是否可勾选
        checked: 初始勾选状态
        
    Returns:
        QGroupBox: 配置好的分组框
    """
    group = QGroupBox(title)
    if checkable:
        group.setCheckable(True)
        group.setChecked(checked)
    
    if layout_type.lower() == "vertical":
        group.setLayout(QVBoxLayout())
    else:
        group.setLayout(QHBoxLayout())
        
    return group


def create_label(text: str, bold: bool = False, color: str = None, 
                font_size: int = None) -> QLabel:
    """
    创建标准化的标签
    
    Args:
        text: 标签文本
        bold: 是否加粗
        color: 文本颜色（CSS格式）
        font_size: 字体大小
        
    Returns:
        QLabel: 配置好的标签
    """
    label = QLabel(text)
    
    style_parts = []
    if bold:
        style_parts.append("font-weight: bold;")
    if color:
        style_parts.append(f"color: {color};")
    if font_size:
        style_parts.append(f"font-size: {font_size}px;")
        
    if style_parts:
        label.setStyleSheet(" ".join(style_parts))
        
    return label


def create_button(text: str, icon: str = None, tooltip: str = None, 
                  style: str = None, minimum_width: int = None) -> QPushButton:
    """
    创建标准化的按钮
    
    Args:
        text: 按钮文本
        icon: 图标名称（qtawesome格式）
        tooltip: 工具提示文本
        style: CSS样式
        minimum_width: 最小宽度
        
    Returns:
        QPushButton: 配置好的按钮
    """
    if icon:
        btn = QPushButton(qta.icon(icon), text)
    else:
        btn = QPushButton(text)
        
    if tooltip:
        btn.setToolTip(tooltip)
        
    if style:
        btn.setStyleSheet(style)
        
    if minimum_width:
        btn.setMinimumWidth(minimum_width)
        
    return btn


def create_input_field(field_type: str, default_value: Any = None, 
                      options: List[str] = None, range_values: List[float] = None,
                      placeholder: str = None, read_only: bool = False) -> QWidget:
    """
    创建标准化的输入字段
    
    Args:
        field_type: 字段类型（"text", "number", "float", "combo", "checkbox"）
        default_value: 默认值
        options: 下拉选项列表（仅对combo类型有效）
        range_values: 数值范围 [min, max]（仅对number/float类型有效）
        placeholder: 占位文本
        read_only: 是否只读
        
    Returns:
        QWidget: 输入控件
    """
    widget = None
    
    if field_type == "text":
        widget = QLineEdit()
        if default_value is not None:
            widget.setText(str(default_value))
        if placeholder:
            widget.setPlaceholderText(placeholder)
        widget.setReadOnly(read_only)
        
    elif field_type == "number":
        widget = QSpinBox()
        if range_values and len(range_values) >= 2:
            widget.setRange(int(range_values[0]), int(range_values[1]))
        else:
            widget.setRange(-1000000, 1000000)
        if default_value is not None:
            widget.setValue(int(default_value))
        
    elif field_type == "float":
        widget = QDoubleSpinBox()
        if range_values and len(range_values) >= 2:
            widget.setRange(float(range_values[0]), float(range_values[1]))
        else:
            widget.setRange(-1000000.0, 1000000.0)
        widget.setDecimals(3)
        widget.setSingleStep(0.001)
        if default_value is not None:
            widget.setValue(float(default_value))
        
    elif field_type == "combo":
        widget = QComboBox()
        if options:
            widget.addItems(options)
        if default_value is not None:
            widget.setCurrentText(str(default_value))
        
    elif field_type == "checkbox":
        widget = QCheckBox()
        if default_value is not None:
            widget.setChecked(bool(default_value))
    
    else:
        # 默认为文本输入
        widget = QLineEdit()
        if default_value is not None:
            widget.setText(str(default_value))
    
    return widget


def create_form_row(label_text: str, widget: QWidget, required: bool = False, 
                    unit: str = None) -> tuple:
    """
    创建表单行（标签 + 控件）
    
    Args:
        label_text: 标签文本
        widget: 输入控件
        required: 是否为必填项
        unit: 单位文本
        
    Returns:
        tuple: (QLabel, QWidget) 标签和控件
    """
    # 构建标签文本
    full_label = label_text
    if required:
        full_label += " *"
    if unit:
        full_label += f" ({unit})"
    
    # 创建标签
    label = create_label(full_label, bold=required, color="red" if required else None)
    
    return label, widget


def create_protocol_config_widget(protocol_type: str) -> QWidget:
    """
    创建协议配置界面（通用模板）
    
    Args:
        protocol_type: 协议类型（"serial", "tcpip", "profinet", "modbus"）
        
    Returns:
        QWidget: 配置好的协议界面
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    if protocol_type == "serial":
        # 串口配置
        port_layout = QHBoxLayout()
        port_layout.addWidget(create_label("串口:"))
        port_combo = create_input_field("combo")
        port_layout.addWidget(port_combo)
        refresh_btn = create_button("", "fa5s.sync", "刷新串口列表")
        refresh_btn.setMaximumWidth(30)
        port_layout.addWidget(refresh_btn)
        port_layout.addStretch()
        layout.addLayout(port_layout)
        
        # 波特率设置
        baud_layout = QHBoxLayout()
        baud_layout.addWidget(create_label("波特率:"))
        baud_combo = create_input_field("combo", "115200", 
                                      ["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        baud_layout.addWidget(baud_combo)
        baud_layout.addStretch()
        layout.addLayout(baud_layout)
        
    elif protocol_type == "tcpip":
        # TCP/IP配置
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(create_label("工作模式:"))
        mode_combo = create_input_field("combo", "Client", ["Client", "Server"])
        mode_layout.addWidget(mode_combo)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # IP地址设置
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(create_label("IP地址:"))
        ip_input = create_input_field("text", "192.168.1.100", placeholder="服务器IP地址")
        ip_layout.addWidget(ip_input)
        ip_layout.addStretch()
        layout.addLayout(ip_layout)
        
    elif protocol_type == "profinet":
        # Profinet配置
        name_layout = QHBoxLayout()
        name_layout.addWidget(create_label("设备名称:"))
        name_input = create_input_field("text", "robot-controller", placeholder="设备名称")
        name_layout.addWidget(name_input)
        name_layout.addStretch()
        layout.addLayout(name_layout)
        
    elif protocol_type == "modbus":
        # ModBus配置
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(create_label("IP地址:"))
        ip_input = create_input_field("text", "192.168.1.100", placeholder="ModBus服务器IP")
        ip_layout.addWidget(ip_input)
        ip_layout.addStretch()
        layout.addLayout(ip_layout)
    
    return widget


def create_parameter_widget(param_name: str, param_info: Dict[str, Any], 
                           is_required: bool = False) -> tuple:
    """
    创建参数控件（通用版本）
    
    Args:
        param_name: 参数名称
        param_info: 参数信息字典
        is_required: 是否为必填参数
        
    Returns:
        tuple: (QLabel, QWidget) 标签和控件
    """
    param_type = param_info.get("type", "string")
    default_value = param_info.get("default")
    param_range = param_info.get("range")
    options = param_info.get("options")
    unit = param_info.get("unit", "")
    
    # 创建输入控件
    widget = create_input_field(
        field_type=param_type,
        default_value=default_value,
        options=options,
        range_values=param_range,
        placeholder=f"请输入{param_name}"
    )
    
    # 创建标签
    label, widget = create_form_row(param_name, widget, is_required, unit)
    
    return label, widget


def create_collapsible_section(widget: QWidget, title: str, 
                              initially_expanded: bool = False) -> QGroupBox:
    """
    创建可折叠的分组区域
    
    Args:
        widget: 要包含的控件
        title: 分组标题
        initially_expanded: 初始是否展开
        
    Returns:
        QGroupBox: 可折叠的分组框
    """
    group = create_group_box(title, "vertical", True, initially_expanded)
    group.layout().addWidget(widget)
    
    if not initially_expanded:
        widget.setVisible(False)
    
    group.toggled.connect(widget.setVisible)
    return group


# 样式常量
BUTTON_STYLE_PRIMARY = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QPushButton:pressed {
        background-color: #3d8b40;
    }
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
"""

BUTTON_STYLE_SECONDARY = """
    QPushButton {
        background-color: #2196F3;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1976D2;
    }
    QPushButton:pressed {
        background-color: #1565C0;
    }
"""

BUTTON_STYLE_DANGER = """
    QPushButton {
        background-color: #f44336;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #d32f2f;
    }
    QPushButton:pressed {
        background-color: #b71c1c;
    }
"""

# 导出常用函数
__all__ = [
    'create_group_box',
    'create_label', 
    'create_button',
    'create_input_field',
    'create_form_row',
    'create_protocol_config_widget',
    'create_parameter_widget',
    'create_collapsible_section',
    'BUTTON_STYLE_PRIMARY',
    'BUTTON_STYLE_SECONDARY', 
    'BUTTON_STYLE_DANGER'
]