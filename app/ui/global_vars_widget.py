#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局变量管理组件
功能：显示、编辑和导出机器人全局变量
"""

import sys
import os
from typing import Dict, Any, List, Union
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QFileDialog, QLabel,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QGroupBox, QSplitter, QTextEdit, QProgressBar, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("警告: pandas未安装，Excel导出功能将不可用")

class GlobalVariablesWidget(QWidget):
    """
    全局变量管理组件
    提供表格显示、编辑和Excel导出功能
    """
    
    # 信号定义
    variables_updated = pyqtSignal(dict)  # 全局变量更新信号
    variable_changed = pyqtSignal(str, object)  # 单个变量修改信号
    export_completed = pyqtSignal(str)  # 导出完成信号
    error_occurred = pyqtSignal(str)  # 错误信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_variables = {}  # 当前全局变量数据
        self.modified_variables = {}  # 修改后的变量数据
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 标题和控制按钮区域
        header_layout = QHBoxLayout()
        
        # 标题
        title_label = QLabel("机器人全局变量管理")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 控制按钮
        self.btn_refresh = QPushButton("刷新数据")
        self.btn_export_excel = QPushButton("导出Excel")
        self.btn_import_excel = QPushButton("导入Excel")
        self.btn_apply_changes = QPushButton("应用修改")
        self.btn_reset_changes = QPushButton("重置修改")
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                font-size: 12px;
                border-radius: 4px;
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
        
        for btn in [self.btn_refresh, self.btn_export_excel, self.btn_import_excel, 
                   self.btn_apply_changes, self.btn_reset_changes]:
            btn.setStyleSheet(button_style)
            header_layout.addWidget(btn)
        
        # 特殊样式设置
        self.btn_apply_changes.setStyleSheet(button_style.replace("#4CAF50", "#2196F3").replace("#45a049", "#1976D2").replace("#3d8b40", "#1565C0"))
        self.btn_reset_changes.setStyleSheet(button_style.replace("#4CAF50", "#FF9800").replace("#45a049", "#F57C00").replace("#3d8b40", "#E65100"))
        
        layout.addLayout(header_layout)
        
        # 状态信息区域
        status_layout = QHBoxLayout()
        self.status_label = QLabel("状态: 等待数据...")
        self.variable_count_label = QLabel("变量数量: 0")
        self.modified_count_label = QLabel("已修改: 0")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.variable_count_label)
        status_layout.addWidget(self.modified_count_label)
        
        layout.addLayout(status_layout)
        
        # 主要内容区域 - 使用分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：变量表格
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # 表格标题
        table_title = QLabel("全局变量列表")
        table_title.setFont(QFont("Arial", 12, QFont.Bold))
        table_layout.addWidget(table_title)
        
        # 创建表格
        self.variables_table = QTableWidget()
        self.variables_table.setColumnCount(4)
        self.variables_table.setHorizontalHeaderLabels(["变量名", "当前值", "新值", "类型"])
        
        # 设置表格样式
        self.variables_table.setAlternatingRowColors(True)
        self.variables_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.variables_table.horizontalHeader().setStretchLastSection(True)
        self.variables_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # 设置列宽
        self.variables_table.setColumnWidth(0, 200)  # 变量名
        self.variables_table.setColumnWidth(1, 250)  # 当前值
        self.variables_table.setColumnWidth(2, 250)  # 新值
        self.variables_table.setColumnWidth(3, 100)  # 类型
        
        table_layout.addWidget(self.variables_table)
        splitter.addWidget(table_widget)
        
        # 右侧：详细信息和编辑区域
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        
        # 详细信息标题
        detail_title = QLabel("变量详细信息")
        detail_title.setFont(QFont("Arial", 12, QFont.Bold))
        detail_layout.addWidget(detail_title)
        
        # 详细信息显示区域
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(200)
        detail_layout.addWidget(self.detail_text)
        
        # 编辑区域
        edit_group = QGroupBox("编辑变量")
        edit_layout = QVBoxLayout(edit_group)
        
        # 变量名显示
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("变量名:"))
        self.edit_var_name = QLabel("未选择")
        self.edit_var_name.setStyleSheet("font-weight: bold; color: #2196F3;")
        name_layout.addWidget(self.edit_var_name)
        name_layout.addStretch()
        edit_layout.addLayout(name_layout)
        
        # 类型显示
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("类型:"))
        self.edit_var_type = QLabel("未知")
        type_layout.addWidget(self.edit_var_type)
        type_layout.addStretch()
        edit_layout.addLayout(type_layout)
        
        # 值编辑区域
        self.edit_value_widget = QWidget()
        self.edit_value_layout = QVBoxLayout(self.edit_value_widget)
        edit_layout.addWidget(self.edit_value_widget)
        
        # 编辑按钮
        edit_btn_layout = QHBoxLayout()
        self.btn_save_edit = QPushButton("保存修改")
        self.btn_cancel_edit = QPushButton("取消")
        
        self.btn_save_edit.setStyleSheet(button_style.replace("#4CAF50", "#2196F3").replace("#45a049", "#1976D2").replace("#3d8b40", "#1565C0"))
        self.btn_cancel_edit.setStyleSheet(button_style.replace("#4CAF50", "#9E9E9E").replace("#45a049", "#757575").replace("#3d8b40", "#616161"))
        
        edit_btn_layout.addWidget(self.btn_save_edit)
        edit_btn_layout.addWidget(self.btn_cancel_edit)
        edit_btn_layout.addStretch()
        edit_layout.addLayout(edit_btn_layout)
        
        detail_layout.addWidget(edit_group)
        detail_layout.addStretch()
        
        splitter.addWidget(detail_widget)
        
        # 设置分割器比例
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)
        
        # 进度条（用于导入/导出操作）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 初始状态设置
        self.btn_apply_changes.setEnabled(False)
        self.btn_reset_changes.setEnabled(False)
        self.btn_export_excel.setEnabled(PANDAS_AVAILABLE)
        self.btn_import_excel.setEnabled(PANDAS_AVAILABLE)
        
        if not PANDAS_AVAILABLE:
            self.btn_export_excel.setToolTip("需要安装pandas库才能使用Excel功能")
            self.btn_import_excel.setToolTip("需要安装pandas库才能使用Excel功能")
    
    def setup_connections(self):
        """设置信号连接"""
        self.btn_refresh.clicked.connect(self.refresh_variables)
        self.btn_export_excel.clicked.connect(self.export_to_excel)
        self.btn_import_excel.clicked.connect(self.import_from_excel)
        self.btn_apply_changes.clicked.connect(self.apply_changes)
        self.btn_reset_changes.clicked.connect(self.reset_changes)
        
        self.btn_save_edit.clicked.connect(self.save_current_edit)
        self.btn_cancel_edit.clicked.connect(self.cancel_current_edit)
        
        self.variables_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.variables_table.cellDoubleClicked.connect(self.on_cell_double_clicked)
    
    def update_variables(self, variables: Dict[str, Any]):
        """更新全局变量数据"""
        try:
            self.current_variables = variables.copy()
            self.populate_table()
            self.update_status(f"已加载 {len(variables)} 个全局变量")
            self.variable_count_label.setText(f"变量数量: {len(variables)}")
        except Exception as e:
            self.error_occurred.emit(f"更新变量数据失败: {str(e)}")
    
    def populate_table(self):
        """填充表格数据"""
        try:
            self.variables_table.setRowCount(len(self.current_variables))
            
            for row, (name, value) in enumerate(self.current_variables.items()):
                # 变量名
                name_item = QTableWidgetItem(str(name))
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # 不可编辑
                self.variables_table.setItem(row, 0, name_item)
                
                # 当前值
                current_value_str = self.format_value_for_display(value)
                current_item = QTableWidgetItem(current_value_str)
                current_item.setFlags(current_item.flags() & ~Qt.ItemIsEditable)  # 不可编辑
                self.variables_table.setItem(row, 1, current_item)
                
                # 新值（如果有修改）
                if name in self.modified_variables:
                    new_value_str = self.format_value_for_display(self.modified_variables[name])
                    new_item = QTableWidgetItem(new_value_str)
                    new_item.setBackground(QColor(255, 255, 0, 100))  # 黄色背景表示已修改
                else:
                    new_item = QTableWidgetItem("")
                new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)  # 不可编辑
                self.variables_table.setItem(row, 2, new_item)
                
                # 类型
                var_type = self.get_variable_type(value)
                type_item = QTableWidgetItem(var_type)
                type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)  # 不可编辑
                self.variables_table.setItem(row, 3, type_item)
            
            self.update_modified_count()
            
        except Exception as e:
            self.error_occurred.emit(f"填充表格失败: {str(e)}")
    
    def format_value_for_display(self, value: Any) -> str:
        """格式化值用于显示"""
        try:
            if isinstance(value, (list, tuple)):
                if len(value) <= 6:
                    return f"[{', '.join(f'{v:.3f}' if isinstance(v, float) else str(v) for v in value)}]"
                else:
                    return f"[数组长度: {len(value)}, 前3项: {', '.join(str(v) for v in value[:3])}...]"
            elif isinstance(value, float):
                return f"{value:.6f}"
            elif isinstance(value, bool):
                return "True" if value else "False"
            elif isinstance(value, int):
                return str(value)
            elif isinstance(value, str):
                return value
            else:
                return str(value)
        except Exception:
            return "<显示错误>"
    
    def get_variable_type(self, value: Any) -> str:
        """获取变量类型字符串"""
        if isinstance(value, bool):
            return "布尔"
        elif isinstance(value, int):
            return "整数"
        elif isinstance(value, float):
            return "浮点"
        elif isinstance(value, str):
            return "字符串"
        elif isinstance(value, (list, tuple)):
            if len(value) > 0:
                element_type = type(value[0]).__name__
                return f"数组[{element_type}]"
            else:
                return "数组[空]"
        elif isinstance(value, dict):
            return "字典"
        else:
            return "其他"
    
    def on_selection_changed(self):
        """处理表格选择变化"""
        try:
            current_row = self.variables_table.currentRow()
            if current_row >= 0:
                var_name = self.variables_table.item(current_row, 0).text()
                self.show_variable_details(var_name)
        except Exception as e:
            self.error_occurred.emit(f"选择变化处理失败: {str(e)}")
    
    def show_variable_details(self, var_name: str):
        """显示变量详细信息"""
        try:
            if var_name in self.current_variables:
                value = self.current_variables[var_name]
                
                # 更新详细信息显示
                details = []
                details.append(f"变量名: {var_name}")
                details.append(f"类型: {self.get_variable_type(value)}")
                details.append(f"当前值: {self.format_value_for_display(value)}")
                
                if var_name in self.modified_variables:
                    details.append(f"修改后值: {self.format_value_for_display(self.modified_variables[var_name])}")
                    details.append("状态: 已修改")
                else:
                    details.append("状态: 未修改")
                
                # 如果是数组，显示详细信息
                if isinstance(value, (list, tuple)) and len(value) > 0:
                    details.append(f"数组长度: {len(value)}")
                    details.append("数组内容:")
                    for i, item in enumerate(value[:10]):  # 最多显示前10个元素
                        details.append(f"  [{i}]: {item}")
                    if len(value) > 10:
                        details.append(f"  ... 还有 {len(value) - 10} 个元素")
                
                self.detail_text.setPlainText("\n".join(details))
                
                # 更新编辑区域
                self.setup_edit_area(var_name, value)
                
        except Exception as e:
            self.error_occurred.emit(f"显示变量详情失败: {str(e)}")
    
    def setup_edit_area(self, var_name: str, value: Any):
        """设置编辑区域"""
        try:
            # 清除现有编辑控件
            for i in reversed(range(self.edit_value_layout.count())):
                child = self.edit_value_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
            
            # 更新变量名和类型显示
            self.edit_var_name.setText(var_name)
            self.edit_var_type.setText(self.get_variable_type(value))
            
            # 根据变量类型创建相应的编辑控件
            current_value = self.modified_variables.get(var_name, value)
            
            if isinstance(value, bool) or (isinstance(value, int) and value in [0, 1]):
                # 布尔值编辑
                self.current_edit_widget = QCheckBox("启用")
                self.current_edit_widget.setChecked(bool(current_value))
                self.edit_value_layout.addWidget(self.current_edit_widget)
                
            elif isinstance(value, int):
                # 整数编辑
                self.current_edit_widget = QSpinBox()
                self.current_edit_widget.setRange(-999999, 999999)
                self.current_edit_widget.setValue(int(current_value))
                self.edit_value_layout.addWidget(self.current_edit_widget)
                
            elif isinstance(value, float):
                # 浮点数编辑
                self.current_edit_widget = QDoubleSpinBox()
                self.current_edit_widget.setRange(-999999.999999, 999999.999999)
                self.current_edit_widget.setDecimals(6)
                self.current_edit_widget.setValue(float(current_value))
                self.edit_value_layout.addWidget(self.current_edit_widget)
                
            elif isinstance(value, str):
                # 字符串编辑
                self.current_edit_widget = QLineEdit()
                self.current_edit_widget.setText(str(current_value))
                self.edit_value_layout.addWidget(self.current_edit_widget)
                
            elif isinstance(value, (list, tuple)):
                # 数组编辑
                self.current_edit_widget = QTextEdit()
                self.current_edit_widget.setMaximumHeight(100)
                # 将数组转换为每行一个元素的格式
                array_text = "\n".join(str(item) for item in current_value)
                self.current_edit_widget.setPlainText(array_text)
                self.edit_value_layout.addWidget(self.current_edit_widget)
                
                # 添加说明标签
                help_label = QLabel("每行输入一个数组元素")
                help_label.setStyleSheet("color: #666; font-size: 10px;")
                self.edit_value_layout.addWidget(help_label)
                
            else:
                # 其他类型，使用文本编辑
                self.current_edit_widget = QLineEdit()
                self.current_edit_widget.setText(str(current_value))
                self.edit_value_layout.addWidget(self.current_edit_widget)
            
            self.current_edit_var_name = var_name
            
        except Exception as e:
            self.error_occurred.emit(f"设置编辑区域失败: {str(e)}")
    
    def save_current_edit(self):
        """保存当前编辑"""
        try:
            if not hasattr(self, 'current_edit_var_name') or not hasattr(self, 'current_edit_widget'):
                return
            
            var_name = self.current_edit_var_name
            original_value = self.current_variables[var_name]
            
            # 根据控件类型获取新值
            if isinstance(self.current_edit_widget, QCheckBox):
                new_value = 1 if self.current_edit_widget.isChecked() else 0
            elif isinstance(self.current_edit_widget, QSpinBox):
                new_value = self.current_edit_widget.value()
            elif isinstance(self.current_edit_widget, QDoubleSpinBox):
                new_value = self.current_edit_widget.value()
            elif isinstance(self.current_edit_widget, QLineEdit):
                text = self.current_edit_widget.text().strip()
                # 尝试转换为原始类型
                if isinstance(original_value, int):
                    new_value = int(text)
                elif isinstance(original_value, float):
                    new_value = float(text)
                else:
                    new_value = text
            elif isinstance(self.current_edit_widget, QTextEdit):
                # 处理数组编辑
                text = self.current_edit_widget.toPlainText().strip()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                # 尝试转换为原始数组的元素类型
                if isinstance(original_value, (list, tuple)) and len(original_value) > 0:
                    element_type = type(original_value[0])
                    try:
                        if element_type == int:
                            new_value = [int(line) for line in lines]
                        elif element_type == float:
                            new_value = [float(line) for line in lines]
                        else:
                            new_value = lines
                    except ValueError:
                        raise ValueError(f"无法将输入转换为 {element_type.__name__} 类型")
                else:
                    new_value = lines
            else:
                new_value = str(self.current_edit_widget.text() if hasattr(self.current_edit_widget, 'text') else self.current_edit_widget)
            
            # 保存修改
            self.modified_variables[var_name] = new_value
            self.populate_table()  # 刷新表格显示
            self.update_status(f"已修改变量: {var_name}")
            
            # 发送变量修改信号
            self.variable_changed.emit(var_name, new_value)
            
        except Exception as e:
            QMessageBox.warning(self, "编辑错误", f"保存编辑失败: {str(e)}")
    
    def cancel_current_edit(self):
        """取消当前编辑"""
        try:
            if hasattr(self, 'current_edit_var_name'):
                var_name = self.current_edit_var_name
                if var_name in self.current_variables:
                    # 重新设置编辑区域为原始值
                    self.setup_edit_area(var_name, self.current_variables[var_name])
        except Exception as e:
            self.error_occurred.emit(f"取消编辑失败: {str(e)}")
    
    def update_modified_count(self):
        """更新修改计数显示"""
        count = len(self.modified_variables)
        self.modified_count_label.setText(f"已修改: {count}")
        self.btn_apply_changes.setEnabled(count > 0)
        self.btn_reset_changes.setEnabled(count > 0)
    
    def apply_changes(self):
        """应用所有修改"""
        try:
            if not self.modified_variables:
                QMessageBox.information(self, "提示", "没有需要应用的修改")
                return
            
            # 确认对话框
            reply = QMessageBox.question(
                self, "确认应用", 
                f"确定要应用 {len(self.modified_variables)} 个变量的修改吗？\n\n这将把修改发送到机器人。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 发送更新信号
                self.variables_updated.emit(self.modified_variables.copy())
                self.update_status(f"已应用 {len(self.modified_variables)} 个变量的修改")
                
                # 清空修改记录
                self.modified_variables.clear()
                self.populate_table()
                
        except Exception as e:
            QMessageBox.critical(self, "应用失败", f"应用修改失败: {str(e)}")
    
    def reset_changes(self):
        """重置所有修改"""
        try:
            if not self.modified_variables:
                QMessageBox.information(self, "提示", "没有需要重置的修改")
                return
            
            # 确认对话框
            reply = QMessageBox.question(
                self, "确认重置", 
                f"确定要重置 {len(self.modified_variables)} 个变量的修改吗？\n\n这将丢失所有未应用的修改。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.modified_variables.clear()
                self.populate_table()
                self.update_status("已重置所有修改")
                
        except Exception as e:
            QMessageBox.critical(self, "重置失败", f"重置修改失败: {str(e)}")
    
    def refresh_variables(self):
        """刷新变量数据"""
        self.update_status("正在刷新变量数据...")
        # 这个信号应该被父组件接收并触发数据刷新
        self.variables_updated.emit({})
    
    def export_to_excel(self):
        """导出到Excel文件"""
        if not PANDAS_AVAILABLE:
            QMessageBox.warning(self, "功能不可用", "需要安装pandas库才能使用Excel导出功能")
            return
        
        try:
            if not self.current_variables:
                QMessageBox.information(self, "提示", "没有可导出的变量数据")
                return
            
            # 选择保存文件
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出全局变量", "robot_global_variables.xlsx", 
                "Excel文件 (*.xlsx);;所有文件 (*)"
            )
            
            if not file_path:
                return
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # 准备数据
            data = []
            for name, value in self.current_variables.items():
                row = {
                    '变量名': name,
                    '当前值': self.format_value_for_display(value),
                    '类型': self.get_variable_type(value),
                    '原始值': str(value)
                }
                
                # 如果有修改，添加修改后的值
                if name in self.modified_variables:
                    row['修改后值'] = self.format_value_for_display(self.modified_variables[name])
                    row['修改后原始值'] = str(self.modified_variables[name])
                    row['状态'] = '已修改'
                else:
                    row['修改后值'] = ''
                    row['修改后原始值'] = ''
                    row['状态'] = '未修改'
                
                data.append(row)
            
            self.progress_bar.setValue(50)
            
            # 创建DataFrame并导出
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False, sheet_name='全局变量')
            
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
            
            self.update_status(f"已导出到: {file_path}")
            self.export_completed.emit(file_path)
            
            QMessageBox.information(self, "导出成功", f"全局变量已成功导出到:\n{file_path}")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            error_msg = f"导出Excel失败: {str(e)}"
            QMessageBox.critical(self, "导出失败", error_msg)
            self.error_occurred.emit(error_msg)
    
    def import_from_excel(self):
        """从Excel文件导入"""
        if not PANDAS_AVAILABLE:
            QMessageBox.warning(self, "功能不可用", "需要安装pandas库才能使用Excel导入功能")
            return
        
        try:
            # 选择文件
            file_path, _ = QFileDialog.getOpenFileName(
                self, "导入全局变量", "", 
                "Excel文件 (*.xlsx *.xls);;所有文件 (*)"
            )
            
            if not file_path:
                return
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            self.progress_bar.setValue(30)
            
            # 验证文件格式
            required_columns = ['变量名', '修改后原始值']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"Excel文件格式不正确，需要包含列: {required_columns}")
            
            # 处理导入的数据
            imported_count = 0
            for _, row in df.iterrows():
                var_name = row['变量名']
                if var_name in self.current_variables and pd.notna(row['修改后原始值']) and str(row['修改后原始值']).strip():
                    try:
                        # 尝试解析修改后的值
                        new_value_str = str(row['修改后原始值']).strip()
                        original_value = self.current_variables[var_name]
                        
                        # 根据原始类型转换新值
                        if isinstance(original_value, bool) or (isinstance(original_value, int) and original_value in [0, 1]):
                            new_value = 1 if new_value_str.lower() in ['true', '1', 'yes', 'on'] else 0
                        elif isinstance(original_value, int):
                            new_value = int(float(new_value_str))  # 先转float再转int，处理"1.0"这种情况
                        elif isinstance(original_value, float):
                            new_value = float(new_value_str)
                        elif isinstance(original_value, str):
                            new_value = new_value_str
                        elif isinstance(original_value, (list, tuple)):
                            # 尝试解析数组
                            if new_value_str.startswith('[') and new_value_str.endswith(']'):
                                # 移除方括号并分割
                                array_str = new_value_str[1:-1]
                                elements = [s.strip() for s in array_str.split(',') if s.strip()]
                                
                                # 转换元素类型
                                if len(original_value) > 0:
                                    element_type = type(original_value[0])
                                    if element_type == int:
                                        new_value = [int(float(e)) for e in elements]
                                    elif element_type == float:
                                        new_value = [float(e) for e in elements]
                                    else:
                                        new_value = elements
                                else:
                                    new_value = elements
                            else:
                                # 按行分割
                                elements = [s.strip() for s in new_value_str.split('\n') if s.strip()]
                                new_value = elements
                        else:
                            new_value = new_value_str
                        
                        self.modified_variables[var_name] = new_value
                        imported_count += 1
                        
                    except Exception as e:
                        print(f"导入变量 {var_name} 失败: {e}")
                        continue
            
            self.progress_bar.setValue(80)
            
            # 刷新显示
            self.populate_table()
            
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
            
            self.update_status(f"从Excel导入了 {imported_count} 个变量修改")
            
            if imported_count > 0:
                QMessageBox.information(self, "导入成功", f"成功导入 {imported_count} 个变量的修改")
            else:
                QMessageBox.warning(self, "导入结果", "没有找到可导入的有效数据")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            error_msg = f"导入Excel失败: {str(e)}"
            QMessageBox.critical(self, "导入失败", error_msg)
            self.error_occurred.emit(error_msg)
    
    def on_cell_double_clicked(self, row: int, column: int):
        """处理单元格双击事件"""
        try:
            if column == 0:  # 变量名列
                var_name = self.variables_table.item(row, 0).text()
                self.show_variable_details(var_name)
        except Exception as e:
            self.error_occurred.emit(f"处理双击事件失败: {str(e)}")
    
    def update_status(self, message: str):
        """更新状态显示"""
        self.status_label.setText(f"状态: {message}")
        
        # 自动清除状态消息
        QTimer.singleShot(5000, lambda: self.status_label.setText("状态: 就绪"))