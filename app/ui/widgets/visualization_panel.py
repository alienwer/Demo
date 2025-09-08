# 3D可视化面板组件
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QGroupBox, QScrollArea, QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QOpenGLContext
from typing import Dict, Any, List
import numpy as np

# 导入高性能GL渲染器
from .gl_renderer import GLRenderer
# 导入运动学计算
from ...utils.kinematics import KinematicsSolver, create_kinematics_solver

class VisualizationPanel(QWidget):
    """3D可视化面板组件"""
    
    view_changed = pyqtSignal(str)  # 视角变化信号
    render_initialized = pyqtSignal()  # 渲染器初始化完成信号
    joint_angle_changed = pyqtSignal(str, float)  # 关节角度变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._joint_sliders = {}  # 关节滑块字典
        self._joint_labels = {}   # 关节标签字典
        self._kinematics_solver = None  # 运动学求解器
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # HUD显示区域
        self.hud_widget = self.create_hud_widget()
        layout.addWidget(self.hud_widget)
        
        # OpenGL渲染区域
        self.gl_renderer = GLRenderer()
        self.gl_renderer.setMinimumSize(800, 600)
        layout.addWidget(self.gl_renderer)
        
        # 连接渲染器信号
        self.gl_renderer.fps_updated.connect(self.update_fps)
        self.gl_renderer.render_initialized.connect(self.render_initialized.emit)
        
        # 关节控制面板
        self.joint_control_widget = self.create_joint_control_widget()
        layout.addWidget(self.joint_control_widget)
        
        # 运动学控制面板
        self.kinematics_widget = self.create_kinematics_widget()
        layout.addWidget(self.kinematics_widget)
        
        # 视角控制工具栏
        self.view_control_widget = self.create_view_control_widget()
        layout.addWidget(self.view_control_widget)
        
    def create_hud_widget(self) -> QWidget:
        """创建HUD显示组件（使用UI工具函数）"""
        from app.utils.ui_utils import create_label
        
        hud = QWidget()
        hud_layout = QHBoxLayout(hud)
        hud_layout.setContentsMargins(10, 5, 10, 5)
        
        # 状态指示器
        self.lbl_status = create_label("🔴 离线", color="#00ff00", font_size=12)
        self.lbl_joints = create_label("关节: ---", color="#00ff00", font_size=12)
        self.lbl_tcp = create_label("TCP: ---", color="#00ff00", font_size=12)
        self.lbl_fps = create_label("FPS: 0", color="#00ff00", font_size=12)
        
        # 设置HUD样式
        hud_style = """
            background-color: rgba(0, 0, 0, 0.7); 
            padding: 4px 8px; 
            border-radius: 3px;
            font-family: 'Monospace';
        """
        
        for widget in [self.lbl_status, self.lbl_joints, self.lbl_tcp, self.lbl_fps]:
            widget.setStyleSheet(hud_style)
            hud_layout.addWidget(widget)
        
        hud_layout.addStretch()
        return hud
    
    def create_joint_control_widget(self) -> QWidget:
        """创建关节控制组件"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        
        control_widget = QWidget()
        self.joint_layout = QVBoxLayout(control_widget)
        self.joint_layout.setContentsMargins(10, 10, 10, 10)
        
        # 初始提示
        from app.utils.ui_utils import create_label
        hint_label = create_label("请先加载机器人模型以显示关节控制", color="#888", font_style="italic")
        hint_label.setAlignment(Qt.AlignCenter)
        self.joint_layout.addWidget(hint_label)
        
        scroll_area.setWidget(control_widget)
        return scroll_area
    
    def create_kinematics_widget(self) -> QWidget:
        """创建运动学控制组件"""
        widget = QGroupBox("运动学控制")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 15, 10, 10)
        
        # TCP位姿显示
        from app.utils.ui_utils import create_label
        tcp_layout = QHBoxLayout()
        tcp_layout.addWidget(create_label("TCP位姿:"))
        self.tcp_display = QLineEdit()
        self.tcp_display.setReadOnly(True)
        self.tcp_display.setPlaceholderText("请先加载机器人模型")
        tcp_layout.addWidget(self.tcp_display)
        layout.addLayout(tcp_layout)
        
        # 正向运动学按钮
        from app.utils.ui_utils import create_button, BUTTON_STYLE_PRIMARY
        btn_fk = create_button("计算正向运动学", style=BUTTON_STYLE_PRIMARY)
        btn_fk.clicked.connect(self._calculate_forward_kinematics)
        layout.addWidget(btn_fk)
        
        # 逆向运动学输入
        ik_layout = QHBoxLayout()
        ik_layout.addWidget(create_label("目标位姿:"))
        self.target_pose_input = QLineEdit()
        self.target_pose_input.setPlaceholderText("x,y,z,rx,ry,rz")
        ik_layout.addWidget(self.target_pose_input)
        
        btn_ik = create_button("逆向运动学", style=BUTTON_STYLE_PRIMARY)
        btn_ik.clicked.connect(self._calculate_inverse_kinematics)
        ik_layout.addWidget(btn_ik)
        layout.addLayout(ik_layout)
        
        return widget
    
    def create_view_control_widget(self) -> QWidget:
        """创建视角控制组件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 预设视角按钮
        views = [
            ("正面", "front"),
            ("侧面", "side"), 
            ("顶部", "top"),
            ("等轴测", "isometric"),
            ("自定义", "custom")
        ]
        
        for text, view_type in views:
            from app.utils.ui_utils import create_button
            btn = create_button(text, minimum_width=80)
            btn.setProperty("view_type", view_type)
            btn.clicked.connect(lambda checked, vt=view_type: self.view_changed.emit(vt))
            layout.addWidget(btn)
        
        layout.addStretch()
        return widget
    
    def update_robot_state(self, state: Dict[str, Any]):
        """更新机器人状态显示"""
        # 更新连接状态
        if state.get('connected', False):
            self.lbl_status.setText("🟢 在线")
        else:
            self.lbl_status.setText("🔴 离线")
        
        # 更新关节角度
        joints = state.get('joint_positions', [])
        if joints:
            joints_str = ", ".join(f"{j:.2f}" for j in joints[:3])  # 显示前3个关节
            self.lbl_joints.setText(f"关节: [{joints_str}...]")
        
        # 更新TCP位姿
        tcp_pose = state.get('tcp_pose', [])
        if tcp_pose and len(tcp_pose) >= 3:
            tcp_str = ", ".join(f"{p:.3f}" for p in tcp_pose[:3])
            self.lbl_tcp.setText(f"TCP: [{tcp_str}]")
    
    def update_fps(self, fps: float):
        """更新FPS显示"""
        self.lbl_fps.setText(f"FPS: {fps:.1f}")
    
    def initialize_gl_renderer(self):
        """初始化OpenGL渲染器"""
        # 渲染器会在首次显示时自动初始化
        print("OpenGL渲染器准备就绪")
    
    def load_robot_model(self, urdf_path: str):
        """加载URDF机器人模型"""
        if hasattr(self, 'gl_renderer'):
            success = self.gl_renderer.load_robot_model(urdf_path)
            if success:
                self._setup_joint_controls()
                # 初始化运动学求解器
                self._initialize_kinematics_solver()
            return success
        return False
    
    def _setup_joint_controls(self):
        """设置关节控制界面"""
        # 清空现有控件
        self._clear_joint_controls()
        
        # 获取关节信息
        joint_angles = self.gl_renderer.get_joint_angles()
        if not joint_angles:
            return
        
        # 移除初始提示
        for i in reversed(range(self.joint_layout.count())):
            widget = self.joint_layout.itemAt(i).widget()
            if widget and isinstance(widget, QLabel) and "请先加载" in widget.text():
                widget.deleteLater()
        
        # 为每个关节创建控制组
        for joint_name, current_angle in joint_angles.items():
            self._create_joint_control_group(joint_name, current_angle)
    
    def _initialize_kinematics_solver(self):
        """初始化运动学求解器"""
        if hasattr(self, 'gl_renderer') and hasattr(self.gl_renderer, '_robot_model'):
            self._kinematics_solver = create_kinematics_solver(self.gl_renderer._robot_model)
            self.tcp_display.setPlaceholderText("等待计算...")
            print("运动学求解器初始化完成")
        else:
            print("警告: 无法初始化运动学求解器")
    
    def _clear_joint_controls(self):
        """清空关节控制控件"""
        self._joint_sliders.clear()
        self._joint_labels.clear()
        
        # 移除所有控件（保留布局）
        for i in reversed(range(self.joint_layout.count())):
            widget = self.joint_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
    
    def _create_joint_control_group(self, joint_name: str, initial_angle: float):
        """为单个关节创建控制组"""
        group = QGroupBox(joint_name)
        layout = QHBoxLayout(group)
        
        # 角度标签
        from app.utils.ui_utils import create_label
        angle_label = create_label(f"{initial_angle:.2f}°", background_color="#f0f0f0", padding=4, border_radius=3)
        angle_label.setMinimumWidth(60)
        angle_label.setAlignment(Qt.AlignCenter)
        
        # 滑块控件
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(-1800)  # -180.0° * 10 用于精确控制
        slider.setMaximum(1800)   # 180.0° * 10
        slider.setValue(int(initial_angle * 10))
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(900)  # 90°间隔
        
        # 连接信号
        slider.valueChanged.connect(
            lambda value, jn=joint_name, al=angle_label: self._on_joint_slider_changed(jn, value, al)
        )
        
        layout.addWidget(create_label("角度:"))
        layout.addWidget(slider)
        layout.addWidget(angle_label)
        
        # 存储引用
        self._joint_sliders[joint_name] = slider
        self._joint_labels[joint_name] = angle_label
        
        self.joint_layout.addWidget(group)
    
    def _on_joint_slider_changed(self, joint_name: str, slider_value: int, angle_label: QLabel):
        """处理关节滑块变化"""
        angle = slider_value / 10.0  # 转换为实际角度
        angle_label.setText(f"{angle:.2f}°")
        
        # 更新渲染器
        if hasattr(self, 'gl_renderer'):
            self.gl_renderer.set_joint_angle(joint_name, angle)
        
        # 发射信号
        self.joint_angle_changed.emit(joint_name, angle)
        
        # 自动更新正向运动学显示
        self._update_forward_kinematics_display()
    
    def set_joint_angle(self, joint_name: str, angle: float):
        """设置单个关节角度"""
        if hasattr(self, 'gl_renderer') and joint_name in self._joint_sliders:
            # 更新滑块位置
            self._joint_sliders[joint_name].setValue(int(angle * 10))
            # 更新渲染器
            self.gl_renderer.set_joint_angle(joint_name, angle)
    
    def set_joint_angles(self, angles: Dict[str, float]):
        """批量设置关节角度"""
        if hasattr(self, 'gl_renderer'):
            for joint_name, angle in angles.items():
                if joint_name in self._joint_sliders:
                    self._joint_sliders[joint_name].setValue(int(angle * 10))
            # 批量更新渲染器
            self.gl_renderer.set_joint_angles(angles)
    
    def get_joint_angles(self) -> Dict[str, float]:
        """获取当前关节角度"""
        if hasattr(self, 'gl_renderer'):
            return self.gl_renderer.get_joint_angles()
        return {}
    
    def _calculate_forward_kinematics(self):
        """计算正向运动学"""
        if not self._kinematics_solver:
            print("警告: 运动学求解器未初始化")
            return
        
        joint_angles = self.get_joint_angles()
        if not joint_angles:
            print("警告: 没有关节角度数据")
            return
        
        # 转换为弧度
        joint_angles_rad = {name: np.deg2rad(angle) for name, angle in joint_angles.items()}
        
        # 计算正向运动学
        try:
            tcp_pose = self._kinematics_solver.forward_kinematics(joint_angles_rad)
            self._display_tcp_pose(tcp_pose)
            print(f"正向运动学计算完成: {tcp_pose[:3, 3]}")
        except Exception as e:
            print(f"正向运动学计算失败: {e}")
    
    def _update_forward_kinematics_display(self):
        """更新正向运动学显示"""
        if not self._kinematics_solver:
            return
        
        joint_angles = self.get_joint_angles()
        if not joint_angles:
            return
        
        # 转换为弧度
        joint_angles_rad = {name: np.deg2rad(angle) for name, angle in joint_angles.items()}
        
        # 计算正向运动学
        try:
            tcp_pose = self._kinematics_solver.forward_kinematics(joint_angles_rad)
            self._display_tcp_pose(tcp_pose)
        except Exception as e:
            print(f"正向运动学更新失败: {e}")
    
    def _calculate_inverse_kinematics(self):
        """计算逆向运动学"""
        if not self._kinematics_solver:
            print("警告: 运动学求解器未初始化")
            return
        
        # 解析目标位姿输入
        target_text = self.target_pose_input.text().strip()
        if not target_text:
            print("警告: 请输入目标位姿")
            return
        
        try:
            values = [float(x.strip()) for x in target_text.split(',')]
            if len(values) != 6:
                print("错误: 需要6个值 (x,y,z,rx,ry,rz)")
                return
            
            # 构建目标位姿矩阵
            target_pose = self._build_target_pose(values)
            
            # 获取当前关节角度作为初始值
            current_angles = self.get_joint_angles()
            current_angles_rad = {name: np.deg2rad(angle) for name, angle in current_angles.items()}
            
            # 计算逆向运动学
            result_angles, converged = self._kinematics_solver.inverse_kinematics(
                target_pose, current_angles_rad
            )
            
            if converged:
                # 转换为角度并设置
                result_angles_deg = {name: np.rad2deg(angle) for name, angle in result_angles.items()}
                self.set_joint_angles(result_angles_deg)
                print("逆向运动学计算成功")
            else:
                print("警告: 逆向运动学未收敛")
                
        except ValueError:
            print("错误: 请输入有效的数字")
        except Exception as e:
            print(f"逆向运动学计算失败: {e}")
    
    def _build_target_pose(self, values: List[float]) -> np.ndarray:
        """从输入值构建目标位姿矩阵"""
        x, y, z, rx, ry, rz = values
        
        # 创建齐次变换矩阵
        T = np.eye(4)
        T[:3, 3] = [x, y, z]  # 位置
        
        # 从欧拉角创建旋转矩阵 (RPY顺序)
        from scipy.spatial.transform import Rotation
        R = Rotation.from_euler('xyz', [rx, ry, rz], degrees=True).as_matrix()
        T[:3, :3] = R
        
        return T
    
    def _display_tcp_pose(self, tcp_pose: np.ndarray):
        """显示TCP位姿"""
        # 提取位置
        position = tcp_pose[:3, 3]
        
        # 从旋转矩阵提取欧拉角
        from scipy.spatial.transform import Rotation
        rotation = Rotation.from_matrix(tcp_pose[:3, :3])
        euler_angles = rotation.as_euler('xyz', degrees=True)
        
        # 格式化显示
        pos_str = ", ".join(f"{p:.3f}" for p in position)
        rot_str = ", ".join(f"{r:.1f}" for r in euler_angles)
        display_text = f"位置: [{pos_str}], 姿态: [{rot_str}]°"
        
        self.tcp_display.setText(display_text)
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'gl_renderer'):
            self.gl_renderer.cleanup()
        print("清理3D可视化面板资源")