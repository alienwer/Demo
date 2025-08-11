"""
OpenGL渲染器 - 统一架构版本

基于Demo_1的GLRenderer重构：
1. 添加关节角度数据存储与更新方法
2. 在渲染时应用关节变换实现姿态同步
3. 修复OpenGL上下文问题，使用纯OpenGL渲染
4. 优化渲染性能，添加网格缓存和显示列表
"""
import numpy as np
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QThread
from PyQt5.QtGui import QMouseEvent, QWheelEvent
from OpenGL.GL import *
from OpenGL.GLU import *
from .urdf_parser import URDFParser
from .mesh_loader import MeshLoader
import trimesh
from typing import Optional, List, Dict

class GLRenderer(QGLWidget, QObject):
    """
    机器人3D可视化渲染器。
    支持URDF模型加载、关节角度更新、视角交互、阴影、环境贴图等。
    """
    render_updated = pyqtSignal()
    
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.model: Optional[dict] = None
        self.mesh_loader = MeshLoader()
        # 调整相机距离以适应米单位的模型
        self.camera_distance: float = 3.0  # 从300.0改为3.0
        self.camera_rotation: List[float] = [0, 0, 0]
        self.camera_center: List[float] = [0, 0, 0]
        self.last_pos: Optional[QMouseEvent] = None
        self.joint_angles: dict = {}
        self._mouse_btn: Optional[int] = None
        self._last_mouse_pos: Optional[QMouseEvent] = None
        self._pan_offset: List[float] = [0, 0]
        self._gl_initialized = False
        
        # 性能优化：网格缓存和显示列表
        self._mesh_display_lists: Dict[str, int] = {}
        self._mesh_cache: Dict[str, trimesh.Trimesh] = {}
        self._display_lists_created = False
        
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.ClickFocus)
    
    def initializeGL(self):
        """初始化OpenGL上下文 - 只在主线程调用"""
        if self._gl_initialized:
            return
            
        try:
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_MULTISAMPLE)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
            glEnable(GL_LINE_SMOOTH)
            # 环境光
            glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
            glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.7, 0.7, 0.7, 0.7])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 80.0)
            # 环境贴图/背景色渐变
            glClearColor(0.85, 0.92, 1.0, 1.0)
            self._gl_initialized = True
        except Exception as e:
            print(f"OpenGL初始化失败: {e}")
    
    def resizeGL(self, w, h):
        if not self._gl_initialized:
            return
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # 调整近远平面以适应米单位的模型
        gluPerspective(45, w/h if h else 1, 0.01, 20.0)  # 从0.1,2000.0改为0.01,20.0
    
    def paintGL(self):
        if not self._gl_initialized:
            return
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # 相机
        gluLookAt(self.camera_center[0]+self._pan_offset[0],
                  self.camera_center[1]+self._pan_offset[1],
                  self.camera_distance,
                  self.camera_center[0], self.camera_center[1], self.camera_center[2],
                  0, 1, 0)
        glRotatef(self.camera_rotation[0], 1, 0, 0)
        glRotatef(self.camera_rotation[1], 0, 1, 0)
        glRotatef(self.camera_rotation[2], 0, 0, 1)
        self.draw_ground_grid()
        self.draw_coordinate_system()
        if self.model:
            self.render_model()
            # 只在需要时渲染阴影（性能优化）
            if hasattr(self, '_render_shadows') and self._render_shadows:
                self.render_shadow()
    
    def draw_ground_grid(self, size=2, step=0.2):
        if not self._gl_initialized:
            return
        glDisable(GL_LIGHTING)
        glColor4f(0.7, 0.7, 0.7, 0.3)
        glBegin(GL_LINES)
        for i in range(-int(size/step), int(size/step)+1):
            pos = i * step
            glVertex3f(pos, 0, -size)
            glVertex3f(pos, 0, size)
            glVertex3f(-size, 0, pos)
            glVertex3f(size, 0, pos)
        glEnd()
        glEnable(GL_LIGHTING)
    
    def draw_coordinate_system(self):
        if not self._gl_initialized:
            return
        glDisable(GL_LIGHTING)
        glLineWidth(2)
        glBegin(GL_LINES)
        # 调整坐标轴长度以适应米单位的模型
        axis_length = 0.5  # 从50改为0.5米
        glColor3f(1.0, 0.0, 0.0)  # 红色X轴
        glVertex3f(0, 0, 0)
        glVertex3f(axis_length, 0, 0)
        glColor3f(0.0, 1.0, 0.0)  # 绿色Y轴
        glVertex3f(0, 0, 0)
        glVertex3f(0, axis_length, 0)
        glColor3f(0.0, 0.0, 1.0)  # 蓝色Z轴
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, axis_length)
        glEnd()
        glLineWidth(1)
        glEnable(GL_LIGHTING)
    
    def load_model(self, urdf_path):
        """加载URDF模型 - 不涉及OpenGL调用"""
        try:
            parser = URDFParser()
            self.model = parser.parse(urdf_path)
            # 清除旧的显示列表
            self.clear_display_lists()
            # 预加载所有网格
            self.preload_meshes()
            return True
        except Exception as e:
            print(f"模型加载错误: {e}")
            return False
    
    def clear_display_lists(self):
        """清除显示列表"""
        if self._display_lists_created:
            for display_list in self._mesh_display_lists.values():
                glDeleteLists(display_list, 1)
            self._mesh_display_lists.clear()
            self._display_lists_created = False
    
    def preload_meshes(self):
        """预加载所有网格并创建显示列表"""
        if not self.model:
            return
            
        print("预加载网格数据...")
        model_bounds = {'min': [float('inf')]*3, 'max': [float('-inf')]*3}
        
        for link in self.model['links']:
            for visual in link['visual']:
                if visual['type'] == 'mesh':
                    mesh_path = visual['filename']
                    if mesh_path not in self._mesh_cache:
                        mesh = self.mesh_loader.load_mesh(mesh_path)
                        if mesh:
                            self._mesh_cache[mesh_path] = mesh
                            # 计算模型边界
                            if len(mesh.vertices) > 0:
                                min_coords = mesh.vertices.min(axis=0)
                                max_coords = mesh.vertices.max(axis=0)
                                for i in range(3):
                                    model_bounds['min'][i] = min(model_bounds['min'][i], min_coords[i])
                                    model_bounds['max'][i] = max(model_bounds['max'][i], max_coords[i])
        
        # 创建显示列表
        self.create_display_lists()
        print(f"预加载完成，共缓存 {len(self._mesh_cache)} 个网格")
        
        # 自动调整相机距离以适应模型大小
        self.auto_adjust_camera(model_bounds)
    
    def auto_adjust_camera(self, model_bounds):
        """根据模型边界自动调整相机距离"""
        if model_bounds['min'][0] == float('inf'):
            return  # 没有有效的边界数据
            
        # 计算模型尺寸
        model_size = [model_bounds['max'][i] - model_bounds['min'][i] for i in range(3)]
        max_size = max(model_size)
        
        if max_size > 0:
            # 根据模型大小调整相机距离
            # 让模型在视野中占据合适的大小
            target_distance = max_size * 2.0  # 模型大小 * 2
            self.camera_distance = max(0.5, min(target_distance, 10.0))  # 限制在0.5-10米之间
            
            # 调整相机中心到模型中心
            model_center = [(model_bounds['min'][i] + model_bounds['max'][i]) / 2 for i in range(3)]
            self.camera_center = model_center
            
            print(f"模型尺寸: {model_size}")
            print(f"模型中心: {model_center}")
            print(f"调整相机距离到: {self.camera_distance:.2f}米")
    
    def create_display_lists(self):
        """为所有网格创建显示列表"""
        if not self._gl_initialized:
            return
            
        try:
            for mesh_path, mesh in self._mesh_cache.items():
                if mesh_path not in self._mesh_display_lists:
                    display_list = glGenLists(1)
                    glNewList(display_list, GL_COMPILE)
                    self.render_mesh_opengl(mesh)
                    glEndList()
                    self._mesh_display_lists[mesh_path] = display_list
            self._display_lists_created = True
        except Exception as e:
            print(f"创建显示列表失败: {e}")
    
    def update_joint_positions(self, joint_angles):
        """更新关节位置 - 线程安全"""
        if not self.model:
            return
        self.joint_angles = {}
        for i, joint in enumerate(self.model['joints']):
            if i < len(joint_angles):
                self.joint_angles[joint['name']] = joint_angles[i]
        # 确保在主线程中更新UI
        if QThread.currentThread() == self.thread():
            self.update()
        else:
            self.update()
    
    def render_mesh_opengl(self, mesh):
        """使用纯OpenGL渲染网格 - 替代trimesh.show()"""
        if not self._gl_initialized or mesh is None:
            return
            
        try:
            vertices = mesh.vertices
            faces = mesh.faces
            
            glBegin(GL_TRIANGLES)
            for face in faces:
                # 计算面法向量
                v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
                normal = np.cross(v2 - v1, v3 - v1)
                
                # 检查法向量是否为零向量（三点共线的情况）
                norm_length = np.linalg.norm(normal)
                if norm_length > 1e-10:  # 避免除零错误
                    normal = normal / norm_length
                    glNormal3f(*normal)
                else:
                    # 如果三点共线，使用默认法向量
                    glNormal3f(0.0, 0.0, 1.0)
                
                glVertex3f(*v1)
                glVertex3f(*v2)
                glVertex3f(*v3)
            glEnd()
        except Exception as e:
            print(f"OpenGL网格渲染错误: {e}")
    
    def render_mesh_from_cache(self, mesh_path):
        """从缓存渲染网格（使用显示列表）"""
        if mesh_path in self._mesh_display_lists:
            glCallList(self._mesh_display_lists[mesh_path])
        else:
            # 如果显示列表不存在，回退到即时渲染
            if mesh_path in self._mesh_cache:
                self.render_mesh_opengl(self._mesh_cache[mesh_path])
    
    def render_model(self):
        """递归渲染机器人模型 - 使用纯OpenGL"""
        if not self._gl_initialized or not self.model:
            return
        # 构建关节变换字典
        joint_angles = self.joint_angles if hasattr(self, 'joint_angles') else {}
        # 构建link和joint的索引
        link_map = {link['name']: link for link in self.model['links']}
        joint_map = {joint['name']: joint for joint in self.model['joints']}
        # 构建child->joint映射
        child_joint_map = {joint['child']: joint for joint in self.model['joints']}
        # 构建parent->children映射
        parent_children_map = {}
        for joint in self.model['joints']:
            parent = joint['parent']
            if parent not in parent_children_map:
                parent_children_map[parent] = []
            parent_children_map[parent].append(joint['child'])
        # 找到base_link（没有parent_joint的link）
        base_links = [link['name'] for link in self.model['links'] if link['parent_joint'] is None]
        for base_link in base_links:
            self.render_link_recursive(base_link, link_map, child_joint_map, parent_children_map, joint_angles)

    def render_link_recursive(self, link_name, link_map, child_joint_map, parent_children_map, joint_angles):
        link = link_map[link_name]
        # 如果有父关节，应用joint的origin和关节运动变换
        joint = child_joint_map.get(link_name, None)
        if joint:
            glPushMatrix()
            # 1. joint origin (xyz/rpy)
            origin = joint.get('origin', {'xyz': [0,0,0], 'rpy': [0,0,0]})
            glTranslatef(*origin['xyz'])
            rpy = origin['rpy']
            glRotatef(rpy[2]*180/np.pi, 0, 0, 1)
            glRotatef(rpy[1]*180/np.pi, 0, 1, 0)
            glRotatef(rpy[0]*180/np.pi, 1, 0, 0)
            # 2. joint运动（旋转/平移）
            if joint['type'] in ['revolute', 'continuous', 'prismatic']:
                angle = joint_angles.get(joint['name'], 0.0)
                axis = joint.get('axis', [0,0,1])
                if joint['type'] in ['revolute', 'continuous']:
                    glRotatef(angle*180/np.pi, *axis)
                elif joint['type'] == 'prismatic':
                    glTranslatef(*(np.array(axis)*angle))
        # 渲染visual
        mat = [0.7, 0.7, 0.7, 0.7]
        if link.get('material') and link['material'] in self.model['materials']:
            mat = self.model['materials'][link['material']]
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, mat)
        for visual in link['visual']:
            glPushMatrix()
            if 'origin' in visual:
                if 'xyz' in visual['origin']:
                    glTranslatef(*visual['origin']['xyz'])
                if 'rpy' in visual['origin']:
                    rpy = visual['origin']['rpy']
                    glRotatef(rpy[2]*180/np.pi, 0, 0, 1)
                    glRotatef(rpy[1]*180/np.pi, 0, 1, 0)
                    glRotatef(rpy[0]*180/np.pi, 1, 0, 0)
            mesh_path = visual['filename']
            if mesh_path in self._mesh_cache:
                glEnable(GL_BLEND)
                glColor4f(1, 1, 1, mat[3] if len(mat)==4 else 1)
                self.render_mesh_from_cache(mesh_path)
                glDisable(GL_BLEND)
            glPopMatrix()
        # 递归渲染所有子link
        children = parent_children_map.get(link_name, [])
        for child_link in children:
            self.render_link_recursive(child_link, link_map, child_joint_map, parent_children_map, joint_angles)
        if joint:
            glPopMatrix()
    
    def get_parent_joint(self, link_name):
        """获取链接的父关节名称"""
        for joint in self.model['joints']:
            if joint['child'] == link_name:
                return joint['name']
        return None
    
    def build_joint_transforms(self):
        """构建关节变换矩阵"""
        transforms = {}
        
        # 从base_link开始，按层次结构构建变换
        for joint in self.model['joints']:
            if joint['parent'] == 'base_link':
                transforms[joint['name']] = self.compute_joint_transform(joint)
            else:
                # 找到父关节
                parent_joint = None
                for j in self.model['joints']:
                    if j['child'] == joint['parent']:
                        parent_joint = j['name']
                        break
                
                if parent_joint and parent_joint in transforms:
                    # 计算累积变换
                    parent_transform = transforms[parent_joint]
                    joint_transform = self.compute_joint_transform(joint)
                    transforms[joint['name']] = self.multiply_matrices(parent_transform, joint_transform)
        
        return transforms
    
    def compute_joint_transform(self, joint):
        """计算单个关节的变换矩阵"""
        # 获取关节原点
        origin = joint.get('origin', {'xyz': [0,0,0], 'rpy': [0,0,0]})
        xyz = origin['xyz']
        rpy = origin['rpy']
        
        # 创建变换矩阵
        transform = np.eye(4)
        
        # 应用平移
        transform[0:3, 3] = xyz
        
        # 应用旋转 (RPY顺序: roll, pitch, yaw)
        if rpy != [0,0,0]:
            # 转换为弧度
            roll, pitch, yaw = rpy
            
            # 创建旋转矩阵
            cos_r, sin_r = np.cos(roll), np.sin(roll)
            cos_p, sin_p = np.cos(pitch), np.sin(pitch)
            cos_y, sin_y = np.cos(yaw), np.sin(yaw)
            
            # RPY旋转矩阵 (ZYX顺序)
            rot_matrix = np.array([
                [cos_y*cos_p, cos_y*sin_p*sin_r - sin_y*cos_r, cos_y*sin_p*cos_r + sin_y*sin_r, 0],
                [sin_y*cos_p, sin_y*sin_p*sin_r + cos_y*cos_r, sin_y*sin_p*cos_r - cos_y*sin_r, 0],
                [-sin_p, cos_p*sin_r, cos_p*cos_r, 0],
                [0, 0, 0, 1]
            ])
            
            # 应用旋转
            transform = np.dot(rot_matrix, transform)
        
        # 应用关节角度（如果是旋转关节）
        if joint['type'] == 'revolute' and joint['name'] in self.joint_angles:
            angle = self.joint_angles[joint['name']]
            axis = joint.get('axis', [0, 0, 1])
            
            # 创建关节旋转矩阵
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            ux, uy, uz = axis
            
            joint_rot = np.array([
                [cos_a + ux*ux*(1-cos_a), ux*uy*(1-cos_a) - uz*sin_a, ux*uz*(1-cos_a) + uy*sin_a, 0],
                [uy*ux*(1-cos_a) + uz*sin_a, cos_a + uy*uy*(1-cos_a), uy*uz*(1-cos_a) - ux*sin_a, 0],
                [uz*ux*(1-cos_a) - uy*sin_a, uz*uy*(1-cos_a) + ux*sin_a, cos_a + uz*uz*(1-cos_a), 0],
                [0, 0, 0, 1]
            ])
            
            transform = np.dot(joint_rot, transform)
        
        return transform.flatten().tolist()
    
    def multiply_matrices(self, mat1, mat2):
        """矩阵乘法"""
        m1 = np.array(mat1).reshape(4, 4)
        m2 = np.array(mat2).reshape(4, 4)
        result = np.dot(m1, m2)
        return result.flatten().tolist()
    
    def render_shadow(self):
        """渲染阴影 - 使用纯OpenGL（优化版本）"""
        if not self._gl_initialized or not self.model:
            return
            
        glPushAttrib(GL_ENABLE_BIT)
        glDisable(GL_LIGHTING)
        glColor4f(0, 0, 0, 0.15)
        glPushMatrix()
        # 投影到y=0平面
        shadow_mat = [1,0,0,0, 0,0,0,0, 0,0,1,0, 0,0,0,1]
        glMultMatrixf(shadow_mat)
        
        for link in self.model['links']:
            for visual in link['visual']:
                if visual['type'] == 'mesh':
                    mesh_path = visual['filename']
                    if mesh_path in self._mesh_cache:
                        # 使用缓存的显示列表渲染
                        self.render_mesh_from_cache(mesh_path)
        
        glPopMatrix()
        glPopAttrib()
    
    # 视角交互
    def mousePressEvent(self, event: QMouseEvent):
        self._mouse_btn = event.button()
        self._last_mouse_pos = event.pos()
        self.setFocus()  # 确保获得焦点
        
    def mouseMoveEvent(self, event: QMouseEvent):
        if self._mouse_btn == Qt.LeftButton:
            dx = event.x() - self._last_mouse_pos.x()
            dy = event.y() - self._last_mouse_pos.y()
            self.camera_rotation[1] += dx * 0.5
            self.camera_rotation[0] += dy * 0.5
            # 限制旋转角度
            self.camera_rotation[0] = max(-90, min(90, self.camera_rotation[0]))
            self.update()
        elif self._mouse_btn == Qt.RightButton:
            dx = event.x() - self._last_mouse_pos.x()
            dy = event.y() - self._last_mouse_pos.y()
            self._pan_offset[0] += dx * 0.5
            self._pan_offset[1] -= dy * 0.5
            self.update()
        self._last_mouse_pos = event.pos()
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        self._mouse_btn = None
        
    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        self.camera_distance -= delta * 0.01  # 从0.1改为0.01，适应米单位
        self.camera_distance = max(0.5, min(self.camera_distance, 20.0))  # 从50,2000改为0.5,20.0
        self.update()
    
    # 视角交互扩展
    def reset_view(self):
        self.camera_distance = 3.0  # 从300.0改为3.0
        self.camera_rotation = [0, 0, 0]
        self.camera_center = [0, 0, 0]
        self._pan_offset = [0, 0]
        self.update()
    def set_preset_view(self, preset):
        # preset: str, e.g. 'front', 'top', 'side'
        if preset == 'front':
            self.camera_rotation = [0, 0, 0]
        elif preset == 'top':
            self.camera_rotation = [90, 0, 0]
        elif preset == 'side':
            self.camera_rotation = [0, 90, 0]
        self.update()
    def set_robot_model(self, urdf_path: str) -> bool:
        """加载机器人URDF模型"""
        return self.load_model(urdf_path)
    def set_joint_angles(self, joint_angles: List[float]) -> None:
        """设置关节角度（弧度制）"""
        self.update_joint_positions(joint_angles)