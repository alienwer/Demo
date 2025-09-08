# OpenGL渲染器实现 - 高性能3D可视化
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader, QOpenGLBuffer, QOpenGLVertexArrayObject
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import time
import os
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from OpenGL import GL
from OpenGL.GL import glPushMatrix, glPopMatrix, glTranslatef, glRotatef, glScalef, glColor3f, glColor4f
from OpenGL.GLU import gluCylinder

# 导入URDF解析器
try:
    from ...utils.urdf_parser import URDFParser
except ImportError:
    print("警告: URDF解析器未找到，机器人模型加载功能将不可用")
    URDFParser = None

# 导入网格处理库
try:
    import trimesh
except ImportError:
    print("警告: trimesh库未安装，网格文件加载功能将不可用")
    trimesh = None

# 导入正确的MeshLoader
from ...model.mesh_loader import MeshLoader



class GLRenderer(QOpenGLWidget):
    """高性能OpenGL渲染器，支持机器人模型可视化"""
    
    fps_updated = pyqtSignal(float)  # FPS更新信号
    render_initialized = pyqtSignal()  # 渲染器初始化完成信号
    mesh_loaded = pyqtSignal(str, object)  # filename, mesh_object
    mesh_load_failed = pyqtSignal(str, str)  # filename, error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 渲染状态
        self._fps = 0.0
        self._frame_count = 0
        self._last_time = time.time()
        self._initialized = False
        
        # 视角控制
        self._camera_distance = 5.0
        self._camera_azimuth = 45.0
        self._camera_elevation = 30.0
        self._last_mouse_pos = None
        
        # 模型数据
        self._robot_model = None  # URDF机器人模型数据
        self._joint_angles: Dict[str, float] = {}  # 关节角度
        self._display_lists = {}
        self._mesh_cache = {}
        self.mesh_loader = MeshLoader()  # 网格加载器
        
        # 异步加载相关
        self._mesh_loading_queue = queue.Queue()
        self._mesh_loading_thread = None
        self._mesh_loading_executor = ThreadPoolExecutor(max_workers=4)
        self._pending_meshes: Dict[str, bool] = {}  # 正在加载的网格
        self._mesh_placeholder_cache: Dict[str, int] = {}  # 占位符显示列表缓存
        
        # 连接信号槽
        self.mesh_loaded.connect(self._on_mesh_loaded)
        self.mesh_load_failed.connect(self._on_mesh_load_failed)
        
        # 着色器程序
        self._shader_program = None
        
        # URDF解析器
        self._urdf_parser = None
        if URDFParser:
            cache_dir = os.path.join(os.path.expanduser('~'), '.flexiv_demo', 'urdf_cache')
            self._urdf_parser = URDFParser(cache_dir)
        
        # 性能优化
        self.setUpdateBehavior(QOpenGLWidget.PartialUpdate)
        
        # 启动FPS计时器
        self._fps_timer = QTimer(self)
        self._fps_timer.timeout.connect(self._update_fps)
        self._fps_timer.start(1000)  # 每秒更新一次FPS
    
    def initializeGL(self):
        """初始化OpenGL上下文"""
        try:
            # 设置OpenGL状态
            GL.glEnable(GL.GL_DEPTH_TEST)
            GL.glEnable(GL.GL_CULL_FACE)
            GL.glEnable(GL.GL_LIGHTING)
            GL.glEnable(GL.GL_LIGHT0)
            GL.glEnable(GL.GL_COLOR_MATERIAL)
            
            # 设置光照
            GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, [1.0, 1.0, 1.0, 0.0])
            GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
            GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
            GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
            
            # 初始化着色器
            self._init_shaders()
            
            # 创建显示列表
            self._create_display_lists()
            
            self._initialized = True
            self.render_initialized.emit()
            print("OpenGL渲染器初始化完成")
            
        except Exception as e:
            print(f"OpenGL初始化失败: {e}")
    
    def _init_shaders(self):
        """初始化着色器程序"""
        try:
            self._shader_program = QOpenGLShaderProgram(self)
            
            # 顶点着色器
            vertex_shader = """
                #version 120
                attribute vec3 position;
                attribute vec3 normal;
                attribute vec2 texCoord;
                
                varying vec3 Normal;
                varying vec3 FragPos;
                varying vec2 TexCoord;
                
                uniform mat4 model;
                uniform mat4 view;
                uniform mat4 projection;
                
                void main() {
                    gl_Position = projection * view * model * vec4(position, 1.0);
                    FragPos = vec3(model * vec4(position, 1.0));
                    Normal = normal; // 简化法线计算，GLSL 120不支持inverse函数
                    TexCoord = texCoord;
                }
            """
            
            # 片段着色器
            fragment_shader = """
                #version 120
                varying vec3 Normal;
                varying vec3 FragPos;
                varying vec2 TexCoord;
                

                
                uniform vec3 lightPos;
                uniform vec3 viewPos;
                uniform vec3 objectColor;
                uniform bool useTexture;
                
                void main() {
                    // 环境光
                    float ambientStrength = 0.1;
                    vec3 ambient = ambientStrength * vec3(1.0);
                    
                    // 漫反射
                    vec3 norm = normalize(Normal);
                    vec3 lightDir = normalize(lightPos - FragPos);
                    float diff = max(dot(norm, lightDir), 0.0);
                    vec3 diffuse = diff * vec3(1.0);
                    
                    // 镜面反射
                    float specularStrength = 0.5;
                    vec3 viewDir = normalize(viewPos - FragPos);
                    vec3 reflectDir = reflect(-lightDir, norm);
                    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
                    vec3 specular = specularStrength * spec * vec3(1.0);
                    
                    vec3 result = (ambient + diffuse + specular) * objectColor;
                    gl_FragColor = vec4(result, 1.0);
                }
            """
            
            # 编译着色器
            if not self._shader_program.addShaderFromSourceCode(QOpenGLShader.Vertex, vertex_shader):
                raise Exception("顶点着色器编译失败")
            if not self._shader_program.addShaderFromSourceCode(QOpenGLShader.Fragment, fragment_shader):
                raise Exception("片段着色器编译失败")
            if not self._shader_program.link():
                raise Exception("着色器程序链接失败")
                
        except Exception as e:
            print(f"着色器初始化失败: {e}")
            self._shader_program = None
    
    def _create_display_lists(self):
        """创建显示列表（性能优化）"""
        # 创建坐标系显示列表
        self._display_lists['coordinate_system'] = GL.glGenLists(1)
        GL.glNewList(self._display_lists['coordinate_system'], GL.GL_COMPILE)
        
        # 绘制坐标系
        GL.glBegin(GL.GL_LINES)
        # X轴 - 红色
        GL.glColor3f(1.0, 0.0, 0.0)
        GL.glVertex3f(0.0, 0.0, 0.0)
        GL.glVertex3f(1.0, 0.0, 0.0)
        # Y轴 - 绿色
        GL.glColor3f(0.0, 1.0, 0.0)
        GL.glVertex3f(0.0, 0.0, 0.0)
        GL.glVertex3f(0.0, 1.0, 0.0)
        # Z轴 - 蓝色
        GL.glColor3f(0.0, 0.0, 1.0)
        GL.glVertex3f(0.0, 0.0, 0.0)
        GL.glVertex3f(0.0, 0.0, 1.0)
        GL.glEnd()
        
        GL.glEndList()
    
    def _load_mesh(self, filename: str) -> Optional[int]:
        """加载网格文件并创建显示列表（同步版本）
        
        Args:
            filename: 网格文件路径
            
        Returns:
            显示列表ID，如果加载失败返回None
        """
        # 检查缓存
        if filename in self._mesh_cache:
            return self._mesh_cache[filename]
        
        # 使用MeshLoader加载网格
        mesh = self.mesh_loader.load_mesh(filename)
        if mesh is None:
            return None
        
        try:
            # 创建显示列表
            display_list = GL.glGenLists(1)
            GL.glNewList(display_list, GL.GL_COMPILE)
            
            # 使用纯OpenGL渲染网格
            self._render_mesh_opengl(mesh)
            
            GL.glEndList()
            
            # 缓存显示列表
            self._mesh_cache[filename] = display_list
            return display_list
            
        except Exception as e:
            print(f"显示列表创建失败 {filename}: {e}")
            return None
    
    def _render_mesh_opengl(self, mesh):
        """使用纯OpenGL渲染网格"""
        if mesh is None:
            return
            
        try:
            vertices = mesh.vertices
            faces = mesh.faces
            
            GL.glBegin(GL.GL_TRIANGLES)
            for face in faces:
                # 计算面法向量
                v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
                normal = np.cross(v2 - v1, v3 - v1)
                
                # 检查法向量是否为零向量（三点共线的情况）
                norm_length = np.linalg.norm(normal)
                if norm_length > 1e-10:  # 避免除零错误
                    normal = normal / norm_length
                    GL.glNormal3f(*normal)
                else:
                    # 如果三点共线，使用默认法向量
                    GL.glNormal3f(0.0, 0.0, 1.0)
                
                GL.glVertex3f(*v1)
                GL.glVertex3f(*v2)
                GL.glVertex3f(*v3)
            GL.glEnd()
        except Exception as e:
            print(f"OpenGL网格渲染错误: {e}")
    
    def _render_model_recursive(self):
        """递归渲染机器人模型"""
        if not self._robot_model:
            return
            
        # 构建link和joint的索引
        link_map = {link_name: link_data for link_name, link_data in self._robot_model['links'].items()}
        joint_map = {joint_name: joint_data for joint_name, joint_data in self._robot_model['joints'].items()}
        
        # 构建child->joint映射
        child_joint_map = {}
        for joint_name, joint_data in self._robot_model['joints'].items():
            child_joint_map[joint_data['child']] = joint_data
        
        # 构建parent->children映射
        parent_children_map = {}
        for joint_name, joint_data in self._robot_model['joints'].items():
            parent = joint_data['parent']
            if parent not in parent_children_map:
                parent_children_map[parent] = []
            parent_children_map[parent].append(joint_data['child'])
        
        # 找到base_link（没有parent_joint的link）
        base_links = [link_name for link_name, link_data in self._robot_model['links'].items() if link_data.get('parent_joint') is None]
        for base_link in base_links:
            self._render_link_recursive(base_link, link_map, child_joint_map, parent_children_map)
    
    def _render_link_recursive(self, link_name, link_map, child_joint_map, parent_children_map):
        """递归渲染链接"""
        link = link_map[link_name]
        
        # 如果有父关节，应用joint的origin和关节运动变换
        joint = child_joint_map.get(link_name)
        if joint:
            GL.glPushMatrix()
            
            # 1. joint origin (xyz/rpy)
            origin = joint.get('origin', {'xyz': [0,0,0], 'rpy': [0,0,0]})
            GL.glTranslatef(*origin['xyz'])
            rpy = origin['rpy']
            GL.glRotatef(rpy[2]*180/np.pi, 0, 0, 1)
            GL.glRotatef(rpy[1]*180/np.pi, 0, 1, 0)
            GL.glRotatef(rpy[0]*180/np.pi, 1, 0, 0)
            
            # 2. joint运动（旋转/平移）
            if joint['type'] in ['revolute', 'continuous', 'prismatic']:
                angle = self._joint_angles.get(joint['name'], 0.0)
                axis = joint.get('axis', [0,0,1])
                if joint['type'] in ['revolute', 'continuous']:
                    GL.glRotatef(angle*180/np.pi, *axis)
                elif joint['type'] == 'prismatic':
                    GL.glTranslatef(*(np.array(axis)*angle))
        
        # 渲染visual几何体
        for visual in link.get('visual', []):
            self._render_geometry(visual)
        
        # 递归渲染所有子链接
        children = parent_children_map.get(link_name, [])
        for child_link in children:
            self._render_link_recursive(child_link, link_map, child_joint_map, parent_children_map)
        
        if joint:
            GL.glPopMatrix()
    
    def _build_joint_transforms(self):
        """构建关节变换矩阵"""
        transforms = {}
        
        # 从base_link开始，按层次结构构建变换
        for joint_name, joint_data in self._robot_model['joints'].items():
            if joint_data['parent'] == 'base_link':
                transforms[joint_name] = self._compute_joint_transform(joint_data)
            else:
                # 找到父关节
                parent_joint = None
                for j_name, j_data in self._robot_model['joints'].items():
                    if j_data['child'] == joint_data['parent']:
                        parent_joint = j_name
                        break
                
                if parent_joint and parent_joint in transforms:
                    # 计算累积变换
                    parent_transform = transforms[parent_joint]
                    joint_transform = self._compute_joint_transform(joint_data)
                    transforms[joint_name] = self._multiply_matrices(parent_transform, joint_transform)
        
        return transforms
    
    def _compute_joint_transform(self, joint):
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
        if joint['type'] == 'revolute' and joint['name'] in self._joint_angles:
            angle = self._joint_angles[joint['name']]
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
    
    def _multiply_matrices(self, mat1, mat2):
        """矩阵乘法"""
        m1 = np.array(mat1).reshape(4, 4)
        m2 = np.array(mat2).reshape(4, 4)
        result = np.dot(m1, m2)
        return result.flatten().tolist()
    
    def resizeGL(self, w: int, h: int):
        """处理窗口大小变化"""
        GL.glViewport(0, 0, w, h)
        
        # 设置投影矩阵
        aspect = w / h if h > 0 else 1.0
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glFrustum(-aspect * 0.5, aspect * 0.5, -0.5, 0.5, 1.0, 100.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)
    
    def paintGL(self):
        """执行渲染"""
        # 清除缓冲区
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)
        
        # 设置模型视图矩阵
        GL.glLoadIdentity()
        
        # 设置摄像机
        self._setup_camera()
        
        # 渲染坐标系
        GL.glCallList(self._display_lists['coordinate_system'])
        
        # 渲染机器人模型（如果有）
        if self._robot_model:
            self._render_model_recursive()
        
        # 更新帧计数
        self._frame_count += 1
    
    def _setup_camera(self):
        """设置摄像机视角"""
        GL.glTranslatef(0.0, 0.0, -self._camera_distance)
        GL.glRotatef(self._camera_elevation, 1.0, 0.0, 0.0)
        GL.glRotatef(self._camera_azimuth, 0.0, 1.0, 0.0)
    
    def _render_robot_model(self):
        """渲染URDF机器人模型"""
        if not self._robot_model:
            return
        
        glPushMatrix()
        
        try:
            # 应用关节变换
            self._apply_joint_transforms()
            
            # 递归渲染机器人模型
            self._render_model_recursive()
                    
        except Exception as e:
            print(f"机器人模型渲染错误: {e}")
        
        glPopMatrix()
    
    def _apply_joint_transforms(self):
        """应用关节变换"""
        if not self._robot_model:
            return
        
        # 构建关节变换矩阵
        joint_transforms = self._build_joint_transforms()
        
        # 应用变换矩阵
        for joint_name, transform in joint_transforms.items():
            if joint_name in self._joint_angles:
                # 这里应该应用变换矩阵到OpenGL
                # 简化实现：直接应用关节角度
                angle = self._joint_angles[joint_name]
                joint = self._robot_model['joints'].get(joint_name, {})
                if joint.get('type') == 'revolute':
                    axis = joint.get('axis', [0, 0, 1])
                    glRotatef(angle * 180/np.pi, *axis)
    
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._last_mouse_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if self._last_mouse_pos and event.buttons() & Qt.LeftButton:
            dx = event.x() - self._last_mouse_pos.x()
            dy = event.y() - self._last_mouse_pos.y()
            
            self._camera_azimuth += dx * 0.5
            self._camera_elevation += dy * 0.5
            self._camera_elevation = max(-90.0, min(90.0, self._camera_elevation))
            
            self._last_mouse_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        self._last_mouse_pos = None
    
    def wheelEvent(self, event):
        """处理鼠标滚轮事件"""
        delta = event.angleDelta().y() / 120.0
        self._camera_distance = max(1.0, min(20.0, self._camera_distance - delta * 0.5))
        self.update()
    
    def _update_fps(self):
        """更新FPS显示"""
        current_time = time.time()
        elapsed = current_time - self._last_time
        
        if elapsed > 0:
            self._fps = self._frame_count / elapsed
            self.fps_updated.emit(self._fps)
        
        self._frame_count = 0
        self._last_time = current_time
    
    def update_robot_state(self, joint_angles: List[float], tcp_pose: List[float]):
        """更新机器人状态"""
        # 这里应该根据关节角度更新机器人模型姿态
        # 目前只是触发重绘
        self.update()
    
    def load_robot_model(self, urdf_path: str, use_cache: bool = True):
        """加载URDF机器人模型"""
        if not self._urdf_parser:
            print("错误: URDF解析器未初始化")
            return False
        
        try:
            urdf_path = os.path.abspath(urdf_path)
            if not os.path.exists(urdf_path):
                print(f"错误: URDF文件不存在: {urdf_path}")
                return False
            
            print(f"加载机器人模型: {urdf_path}")
            self._robot_model = self._urdf_parser.load_urdf(urdf_path, use_cache)
            
            # 为所有几何体创建显示列表（异步方式）
            self._create_robot_display_lists_async()
            
            # 初始化关节角度
            self._initialize_joint_angles()
            
            self.update()
            return True
            
        except Exception as e:
            print(f"机器人模型加载失败: {e}")
            return False
    
    def _create_robot_display_lists(self):
        """为机器人模型创建显示列表（同步版本）"""
        if not self._robot_model:
            return
        
        # 清理旧的显示列表
        for key in list(self._display_lists.keys()):
            if key.startswith('robot_'):
                GL.glDeleteLists(self._display_lists[key], 1)
                del self._display_lists[key]
        
        # 为每个链接创建显示列表
        links = self._robot_model.get('links', {})
        for link_name, link_data in links.items():
            list_name = f'robot_{link_name}'
            self._display_lists[list_name] = GL.glGenLists(1)
            
            GL.glNewList(self._display_lists[list_name], GL.GL_COMPILE)
            self._render_link_geometry(link_data)
            GL.glEndList()
    
    def _create_robot_display_lists_async(self):
        """为机器人模型创建显示列表（异步版本）"""
        if not self._robot_model:
            return
        
        # 清理旧的显示列表
        for key in list(self._display_lists.keys()):
            if key.startswith('robot_'):
                GL.glDeleteLists(self._display_lists[key], 1)
                del self._display_lists[key]
        
        # 为每个链接创建显示列表（先创建占位符）
        links = self._robot_model.get('links', {})
        for link_name, link_data in links.items():
            list_name = f'robot_{link_name}'
            self._display_lists[list_name] = GL.glGenLists(1)
            
            GL.glNewList(self._display_lists[list_name], GL.GL_COMPILE)
            self._render_link_geometry_with_placeholders(link_data)
            GL.glEndList()
            
            # 异步加载所有网格
            self._async_load_all_meshes(link_data)
    
    def _render_link_geometry_with_placeholders(self, link_data: Dict[str, Any]):
        """渲染链接几何体（使用占位符）"""
        # 渲染视觉几何体
        for visual_data in link_data.get('visual', []):
            self._render_geometry_with_placeholder(visual_data)
        
        # 渲染碰撞几何体（可选）
        for collision_data in link_data.get('collision', []):
            self._render_geometry_with_placeholder(collision_data)
    
    def _render_geometry_with_placeholder(self, geometry_data: Dict[str, Any]):
        """渲染单个几何体（使用占位符）"""
        glPushMatrix()
        
        # 应用原点变换
        origin = geometry_data.get('origin', {})
        if 'xyz' in origin:
            glTranslatef(*origin['xyz'])
        if 'rpy' in origin:
            glRotatef(origin['rpy'][2] * 180/np.pi, 0, 0, 1)  # roll
            glRotatef(origin['rpy'][1] * 180/np.pi, 0, 1, 0)  # pitch
            glRotatef(origin['rpy'][0] * 180/np.pi, 1, 0, 0)  # yaw
        
        # 设置材质
        material = geometry_data.get('material', {})
        if 'color' in material:
            glColor4f(*material['color'])
        else:
            glColor3f(0.8, 0.8, 0.8)  # 默认颜色
        
        # 渲染具体几何形状
        shape_type = geometry_data.get('shape')
        params = geometry_data.get('parameters', {})
        
        if shape_type == 'mesh':
            if 'filename' in params:
                filename = params['filename']
                # 检查是否已有显示列表或占位符
                if filename in self._mesh_cache:
                    # 已有缓存，直接渲染
                    display_list = self._mesh_cache[filename]
                    if 'scale' in params:
                        scale = params['scale']
                        glScalef(scale[0], scale[1], scale[2])
                    GL.glCallList(display_list)
                else:
                    # 使用占位符
                    print(f"信息: 使用占位符显示网格，等待异步加载: {filename}")
                    glScalef(0.1, 0.1, 0.1)
                    self._draw_cube()
        else:
            # 其他几何类型正常渲染
            if shape_type == 'box':
                if 'size' in params:
                    size = params['size']
                    glScalef(size[0]/2, size[1]/2, size[2]/2)
                    self._draw_cube()
            elif shape_type == 'sphere':
                if 'radius' in params:
                    radius = params['radius']
                    self._draw_sphere(radius)
            elif shape_type == 'cylinder':
                if 'radius' in params and 'length' in params:
                    radius = params['radius']
                    length = params['length']
                    glTranslatef(0, 0, -length/2)
                    gluCylinder(radius, radius, length, 16, 2)
        
        glPopMatrix()
    
    def _async_load_all_meshes(self, link_data: Dict[str, Any]):
        """异步加载所有网格文件"""
        # 收集所有网格文件
        all_mesh_files = set()
        
        # 从视觉几何体中收集
        for visual_data in link_data.get('visual', []):
            if visual_data.get('shape') == 'mesh' and 'filename' in visual_data.get('parameters', {}):
                all_mesh_files.add(visual_data['parameters']['filename'])
        
        # 从碰撞几何体中收集
        for collision_data in link_data.get('collision', []):
            if collision_data.get('shape') == 'mesh' and 'filename' in collision_data.get('parameters', {}):
                all_mesh_files.add(collision_data['parameters']['filename'])
        
        # 异步加载每个网格
        for mesh_filename in all_mesh_files:
            if mesh_filename not in self._mesh_cache and mesh_filename not in self._pending_meshes:
                self._pending_meshes[mesh_filename] = True
                self._mesh_loading_executor.submit(self._async_load_mesh_task, mesh_filename)
    
    def _async_load_mesh_task(self, filename: str):
        """异步加载网格任务"""
        try:
            print(f"[异步加载] 开始加载网格: {filename}")
            
            # 使用MeshLoader加载网格
            mesh = self.mesh_loader.load_mesh(filename)
            if mesh is None:
                error_msg = f"MeshLoader加载失败: {filename}"
                print(f"[异步加载] {error_msg}")
                self.mesh_load_failed.emit(filename, error_msg)
                return
            
            # 在工作线程中处理网格数据，但不执行OpenGL操作
            # 将网格数据和相关信息发送到主线程进行OpenGL操作
            self.mesh_loaded.emit(filename, mesh)
            
        except Exception as e:
            error_msg = f"异步加载任务异常 {filename}: {e}"
            print(f"[异步加载] {error_msg}")
            self.mesh_load_failed.emit(filename, error_msg)
        finally:
            # 从待处理列表中移除
            if filename in self._pending_meshes:
                del self._pending_meshes[filename]
    
    def _on_mesh_loaded(self, filename: str, mesh: object):
        """网格加载完成信号处理"""
        print(f"[信号处理] 网格加载完成: {filename}")
        
        # 在主线程中创建显示列表
        try:
            self.makeCurrent()
            
            # 创建显示列表
            display_list = GL.glGenLists(1)
            GL.glNewList(display_list, GL.GL_COMPILE)
            self._render_mesh_opengl(mesh)
            GL.glEndList()
            
            # 缓存显示列表
            self._mesh_cache[filename] = display_list
            print(f"[信号处理] 成功创建显示列表并缓存: {filename}")
            
            self.doneCurrent()
            
        except Exception as e:
            error_msg = f"显示列表创建失败 {filename}: {e}"
            print(f"[信号处理] {error_msg}")
            self.mesh_load_failed.emit(filename, error_msg)
            return
        
        # 触发重绘
        self.update()
    
    def _on_mesh_load_failed(self, filename: str, error_message: str):
        """网格加载失败信号处理"""
        print(f"[信号处理] 网格加载失败: {filename} - {error_message}")
        # 可以在这里添加错误处理逻辑，比如显示错误提示
    
    def _draw_cube(self):
        """绘制立方体"""
        vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # 底面
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # 顶面
        ]
        
        faces = [
            [0, 1, 2, 3],  # 底面
            [4, 5, 6, 7],  # 顶面
            [0, 1, 5, 4],  # 前面
            [2, 3, 7, 6],  # 后面
            [0, 3, 7, 4],  # 左面
            [1, 2, 6, 5]   # 右面
        ]
        
        GL.glBegin(GL.GL_QUADS)
        for face in faces:
            for vertex_idx in face:
                GL.glVertex3fv(vertices[vertex_idx])
        GL.glEnd()
    
    def _draw_sphere(self, radius: float):
        """绘制球体"""
        # 简单的球体近似，使用多个四边形面片
        slices = 16
        stacks = 8
        
        for i in range(stacks):
            lat0 = np.pi * (-0.5 + (i) / stacks)
            z0 = np.sin(lat0) * radius
            zr0 = np.cos(lat0)
            
            lat1 = np.pi * (-0.5 + (i + 1) / stacks)
            z1 = np.sin(lat1) * radius
            zr1 = np.cos(lat1)
            
            GL.glBegin(GL.GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * np.pi * (j) / slices
                x = np.cos(lng)
                y = np.sin(lng)
                
                GL.glNormal3f(x * zr0, y * zr0, z0 / radius)
                GL.glVertex3f(x * zr0 * radius, y * zr0 * radius, z0)
                GL.glNormal3f(x * zr1, y * zr1, z1 / radius)
                GL.glVertex3f(x * zr1 * radius, y * zr1 * radius, z1)
            GL.glEnd()
    
    def _render_link_geometry(self, link_data: Dict[str, Any]):
        """渲染链接几何体"""
        # 渲染视觉几何体
        for visual_data in link_data.get('visual', []):
            self._render_geometry(visual_data)
        
        # 渲染碰撞几何体（可选）
        for collision_data in link_data.get('collision', []):
            self._render_geometry(collision_data)
    
    def _render_geometry(self, geometry_data: Dict[str, Any]):
        """渲染单个几何体"""
        glPushMatrix()
        
        # 应用原点变换
        origin = geometry_data.get('origin', {})
        if 'xyz' in origin:
            glTranslatef(*origin['xyz'])
        if 'rpy' in origin:
            glRotatef(origin['rpy'][2] * 180/np.pi, 0, 0, 1)  # roll
            glRotatef(origin['rpy'][1] * 180/np.pi, 0, 1, 0)  # pitch
            glRotatef(origin['rpy'][0] * 180/np.pi, 1, 0, 0)  # yaw
        
        # 设置材质
        material = geometry_data.get('material', {})
        if 'color' in material:
            glColor4f(*material['color'])
        else:
            glColor3f(0.8, 0.8, 0.8)  # 默认颜色
        
        # 渲染具体几何形状
        shape_type = geometry_data.get('shape')
        params = geometry_data.get('parameters', {})
        
        if shape_type == 'box':
            if 'size' in params:
                size = params['size']
                glScalef(size[0]/2, size[1]/2, size[2]/2)
                self._draw_cube()
        
        elif shape_type == 'sphere':
            if 'radius' in params:
                radius = params['radius']
                self._draw_sphere(radius)
        
        elif shape_type == 'cylinder':
            if 'radius' in params and 'length' in params:
                radius = params['radius']
                length = params['length']
                glTranslatef(0, 0, -length/2)
                gluCylinder(radius, radius, length, 16, 2)
        
        elif shape_type == 'mesh':
            if 'filename' in params:
                filename = params['filename']
                # 加载网格并获取显示列表
                display_list = self._load_mesh(filename)
                if display_list is not None:
                    # 应用缩放
                    if 'scale' in params:
                        scale = params['scale']
                        glScalef(scale[0], scale[1], scale[2])
                    # 调用显示列表渲染网格
                    GL.glCallList(display_list)
                else:
                    # 加载失败时使用立方体占位符
                    print(f"警告: 网格文件加载失败，使用立方体占位符: {filename}")
                    glScalef(0.1, 0.1, 0.1)
                    self._draw_cube()
        
        glPopMatrix()
    
    def _initialize_joint_angles(self):
        """初始化关节角度"""
        if not self._robot_model:
            return
        
        self._joint_angles.clear()
        joints = self._robot_model.get('joints', {})
        
        for joint_name, joint_data in joints.items():
            if joint_data['type'] in ['revolute', 'prismatic', 'continuous']:
                # 设置默认角度/位置
                limits = joint_data.get('limits', {})
                if 'lower' in limits and 'upper' in limits:
                    # 设置为中间值
                    self._joint_angles[joint_name] = (limits['lower'] + limits['upper']) / 2
                else:
                    self._joint_angles[joint_name] = 0.0
    
    def set_joint_angle(self, joint_name: str, angle: float):
        """设置单个关节角度"""
        if self._robot_model and joint_name in self._robot_model.get('joints', {}):
            self._joint_angles[joint_name] = angle
            self.update()
        else:
            print(f"警告: 关节 '{joint_name}' 不存在于当前模型中")
    
    def set_joint_angles(self, angles: Dict[str, float]):
        """批量设置关节角度"""
        if self._robot_model:
            valid_joints = self._robot_model.get('joints', {})
            for joint_name, angle in angles.items():
                if joint_name in valid_joints:
                    self._joint_angles[joint_name] = angle
            self.update()
        else:
            print("警告: 没有加载机器人模型")
    
    def get_joint_angles(self) -> Dict[str, float]:
        """获取当前关节角度"""
        return self._joint_angles.copy()

    def cleanup(self):
        """清理OpenGL资源"""
        # 删除显示列表
        for display_list in self._display_lists.values():
            GL.glDeleteLists(display_list, 1)
        
        # 清理网格缓存
        for display_list in self._mesh_cache.values():
            GL.glDeleteLists(display_list, 1)
        
        # 清理着色器程序
        if self._shader_program:
            self._shader_program.deleteLater()
        
        # 清理URDF解析器缓存
        if self._urdf_parser:
            self._urdf_parser.clear_cache()
        
        # 清理异步加载资源
        self._mesh_loading_executor.shutdown(wait=False)
        self._pending_meshes.clear()
        
        print("OpenGL渲染器资源已清理")

# 工具函数
def create_gl_renderer(parent=None) -> GLRenderer:
    """创建OpenGL渲染器实例"""
    return GLRenderer(parent)