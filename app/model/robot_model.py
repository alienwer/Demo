import xml.etree.ElementTree as ET
import numpy as np
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

try:
    import trimesh
    TRIMESH_VERSION = trimesh.__version__
    print(f"[INFO] trimesh version: {TRIMESH_VERSION}")
except ImportError:
    trimesh = None
    print("[ERROR] trimesh is not installed. Mesh loading will not work.")

def check_obj_file_validity(obj_path):
    """简单检查obj文件内容是否标准"""
    if not os.path.exists(obj_path):
        print(f"[ERROR] OBJ文件不存在: {obj_path}")
        return False
    try:
        with open(obj_path, "r") as f:
            lines = f.readlines()
        has_vertex = any(line.startswith("v ") for line in lines)
        has_face = any(line.startswith("f ") for line in lines)
        if not has_vertex or not has_face:
            print(f"[WARNING] OBJ文件缺少顶点或面定义: {obj_path}")
            return False
        return True
    except Exception as e:
        print(f"[ERROR] 检查OBJ文件内容失败: {obj_path}, 错误: {e}")
        return False

def try_load_mesh_with_trimesh(mesh_path):
    """尝试用trimesh加载网格文件，增加详细异常捕获和日志"""
    if trimesh is None:
        print("[ERROR] trimesh库不可用，无法加载网格")
        return None
    if not os.path.exists(mesh_path):
        print(f"[ERROR] Mesh文件不存在: {mesh_path}")
        return None
    # 检查obj文件内容
    if mesh_path.lower().endswith(".obj"):
        if not check_obj_file_validity(mesh_path):
            print(f"[ERROR] OBJ文件内容不标准: {mesh_path}")
            return None
    try:
        mesh = trimesh.load(mesh_path, force='mesh')
        if mesh.is_empty:
            print(f"[ERROR] 加载网格后为空: {mesh_path}")
            return None
        print(f"[DEBUG] trimesh.load成功: {mesh_path}")
        return mesh
    except Exception as e:
        print(f"[ERROR] trimesh.load加载失败: {mesh_path}, 错误: {e}")
        import traceback
        traceback.print_exc()
        # 尝试手动解析obj文件
        if mesh_path.lower().endswith(".obj"):
            try:
                from trimesh.exchange import obj
                with open(mesh_path, "r") as f:
                    obj_data = f.read()
                mesh = obj.load_obj(obj_data)
                print(f"[DEBUG] 手动解析OBJ成功: {mesh_path}")
                return mesh
            except Exception as e2:
                print(f"[ERROR] 手动解析OBJ失败: {mesh_path}, 错误: {e2}")
                traceback.print_exc()
        return None

@dataclass
class Joint:
    name: str
    joint_type: str
    parent: str
    child: str
    origin: List[float]  # [x, y, z, roll, pitch, yaw]
    axis: List[float]    # [x, y, z]
    limits: Tuple[float, float]  # (lower, upper)

@dataclass
class Link:
    """Representation of a robot link"""
    def __init__(self, name, visual_geometry=None, collision_geometry=None, origin=None):
        self.name = name
        self.visual_geometry = visual_geometry
        self.collision_geometry = collision_geometry
        self.origin = origin or [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.transform = np.eye(4)
        self.parent = None  # Add parent attribute
        self.children = []  # Add children list
        self.mdh_params = {'a': 0.0, 'alpha': 0.0, 'd': 0.0, 'theta': 0.0}  # 初始化MDH参数
        self.joint = None  # 添加关节引用

    def set_mdh_params(self, a, alpha, d, theta):
        """设置MDH参数"""
        self.mdh_params = {'a': a, 'alpha': alpha, 'd': d, 'theta': theta}

    def get_transform_from_mdh(self):
        """根据MDH参数计算变换矩阵"""
        a, alpha, d, theta = self.mdh_params.values()
        ct, st = np.cos(theta), np.sin(theta)
        ca, sa = np.cos(alpha), np.sin(alpha)
        
        return np.array([
            [ct,        -st,         0,       a],
            [st*ca,     ct*ca,     -sa,     -sa*d],
            [st*sa,     ct*sa,      ca,      ca*d],
            [0,         0,          0,       1]
        ])
        
    def set_transform(self, matrix):
        """Set the transformation matrix for this link"""
        self.transform = matrix

    def get_transform(self):
        """Get the transformation matrix for this link"""
        return self.transform

    def update_joint_angles(self, joint_angles_dict):
        """根据关节角度更新连杆的MDH参数"""
        for joint_name, angle in joint_angles_dict.items():
            if joint_name in self.joints:
                joint = self.joints[joint_name]
                child_link = self.links[joint.child]
                
                # 更新MDH参数中的theta值
                if hasattr(child_link, 'mdh_params'):
                    child_link.mdh_params['theta'] = angle

    def update_link_transforms(self):
        """递归更新所有连杆的变换矩阵"""
        if not self.base_link:
            return
            
        base_link = self.links[self.base_link]
        base_link.set_transform(np.eye(4))
        self._update_link_transform_recursive(base_link)
        
    def _update_link_transform_recursive(self, parent_link):
        """递归更新子连杆的变换矩阵"""
        # 找到所有以当前连杆为父节点的关节
        for joint in self.joints.values():
            if joint.parent == parent_link.name:
                child_link = self.links[joint.child]
                
                # 计算子连杆的变换矩阵 = 父变换 × MDH变换
                parent_transform = parent_link.get_transform()
                child_mdh_transform = child_link.get_transform_from_mdh()
                child_transform = parent_transform @ child_mdh_transform
                
                child_link.set_transform(child_transform)
                
                # 继续递归更新子节点
                self._update_link_transform_recursive(child_link)

class RobotModel:
    def __init__(self):
        """初始化机器人模型的数据结构"""
        self.joints = {}  # 使用字典存储关节信息
        self.links = {}   # 使用字典存储连杆信息
        self.base_link = ""  # 基础连杆名称
        self.default_joint_angles = {}  # 默认关节角度
        self.joint_names = []  # 关节名称列表
        self.mesh_cache = {}  # 添加缺失的网格缓存属性初始化
        self.link_colors = {}  # 添加link_colors属性初始化
        self.parent_child_relations = {}  # 新增父子关系映射
        self.robot_mdh_params = {}  # 新增机器人MDH参数存储
        
    def load_meshes(self):
        """独立网格加载方法，增加详细异常捕获和日志"""
        for link in self.links.values():
            if link.visual_geometry and link.visual_geometry.get("type") == "mesh":
                mesh_path = link.visual_geometry.get("filename")
                if mesh_path and os.path.exists(mesh_path):
                    print(f"[INFO] 尝试加载网格: {mesh_path}")
                    mesh = try_load_mesh_with_trimesh(mesh_path)
                    if mesh is not None:
                        if hasattr(mesh, "geometry"):  # Scene
                            for geometry_name, geometry in mesh.geometry.items():
                                self.mesh_cache[f"{mesh_path}_{geometry_name}"] = geometry
                                print(f"[DEBUG] 缓存Scene子网格: {mesh_path}_{geometry_name}")
                        else:
                            self.mesh_cache[mesh_path] = mesh
                            print(f"[DEBUG] 缓存Mesh: {mesh_path}")
                    else:
                        print(f"[ERROR] 无法加载网格: {mesh_path}")
                else:
                    print(f"[WARNING] Mesh文件不存在或路径无效: {mesh_path}")
    
    def _update_link_transform_recursive(self, parent_link, visited=None):
        """递归更新子连杆的变换矩阵，增加防止循环的visited参数"""
        if visited is None:
            visited = set()
        if parent_link.name in visited:
            print(f"[ERROR] 检测到循环链接: {parent_link.name}")
            return
        visited.add(parent_link.name)
        
        # 原有递归逻辑
        for joint in self.joints.values():
            if joint.parent == parent_link.name:
                child_link = self.links[joint.child]
                
                # 计算子连杆的变换矩阵 = 父变换 × MDH变换
                parent_transform = parent_link.get_transform()
                child_mdh_transform = child_link.get_transform_from_mdh()
                child_transform = parent_transform @ child_mdh_transform
                
                child_link.set_transform(child_transform)
                
                # 继续递归更新子节点
                self._update_link_transform_recursive(child_link, visited)
    
    def update_link_transforms(self):
        """更新所有连杆的变换矩阵"""
        if not self.base_link or self.base_link not in self.links:
            print("[ERROR] 无效的基础连杆")
            return
            
        base_link = self.links[self.base_link]
        base_transform = np.eye(4)
        self._update_link_transform_recursive(base_link)
    
    def load_urdf(self, file_path: str, is_calibrated: bool = False) -> bool:
        """加载URDF格式的机器人模型文件，增加网格加载详细日志和异常捕获
        
        Args:
            file_path: URDF文件路径
            is_calibrated: 是否为标定后的URDF文件
        """
        try:
            if not os.path.exists(file_path):
                print("URDF文件不存在")
                return False

            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 清空现有数据
            self.joints.clear()
            self.links.clear()
            
            # 添加调试信息
            print(f"[DEBUG] Loading URDF file: {file_path}")

            # 解析机器人基本信息
            robot_name = root.get("name", "robot")
            print(f"[DEBUG] Robot name: {robot_name}")
            self.base_link = root.get("base_link", "")
            if not self.base_link:
                base_link_elem = root.find("link")
                if base_link_elem is None:
                    print("URDF文件中未找到任何连杆信息")
                    return False
                self.base_link = base_link_elem.get("name")

            # 解析连杆信息
            for link in root.findall("link"):
                link_name = link.get("name")
                visual = link.find("visual")
                geom_data = {}
                if visual is not None:
                    geometry = visual.find("geometry")
                    if geometry is not None:
                        # 处理网格文件路径
                        for geom_type in ["box", "cylinder", "sphere", "mesh"]:
                            geom = geometry.find(geom_type)
                            if geom is not None:
                                geom_data["type"] = geom_type
                                geom_data.update(geom.attrib)
                                # 处理网格文件路径
                                if geom_type == "mesh" and "filename" in geom.attrib:
                                    mesh_path = geom.get("filename")
                                    # 处理package://路径
                                    if mesh_path.startswith("package://"):
                                        rel_path = mesh_path[len("package://"):]
                                        base_dir = os.path.join(os.path.dirname(file_path), "..", "flexiv_resources")
                                        base_dir = os.path.abspath(base_dir)
                                        mesh_path = os.path.join(base_dir, rel_path)
                                        if not os.path.exists(mesh_path):
                                            print(f"在flexiv_resources目录查找mesh文件: {rel_path}")
                                            parent_dir = os.path.dirname(base_dir)
                                            mesh_path = os.path.join(parent_dir, rel_path)
                                            if not os.path.exists(mesh_path):
                                                print(f"警告: Mesh文件不存在: {mesh_path}")
                                                continue
                                    elif not os.path.isabs(mesh_path):
                                        mesh_path = os.path.abspath(os.path.join(os.path.dirname(file_path), mesh_path))
                                    geom_data["filename"] = mesh_path
                                    print(f"加载网格文件: {mesh_path}")
                                break

                    # 处理材质信息
                    material = visual.find("material")
                    if material is not None:
                        color = material.find("color")
                        if color is not None:
                            rgba = [float(x) for x in color.get("rgba", "0.8 0.8 0.8 1.0").split()]
                            geom_data["color"] = rgba

                    origin = visual.find("origin")
                    if origin is not None:
                        xyz = [float(x) for x in origin.get("xyz", "0 0 0").split()]
                        rpy = [float(x) for x in origin.get("rpy", "0 0 0").split()]
                    else:
                        xyz = [0, 0, 0]
                        rpy = [0, 0, 0]

                    self.links[link_name] = Link(
                        name=link_name,
                        visual_geometry=geom_data,
                        origin=xyz + rpy
                    )

            # 解析关节信息
            for joint in root.findall("joint"):
                joint_name = joint.get("name")
                joint_type = joint.get("type")
                parent = joint.find("parent").get("link")
                child = joint.find("child").get("link")

                origin = joint.find("origin")
                if origin is not None:
                    xyz = [float(x) for x in origin.get("xyz", "0 0 0").split()]
                    rpy = [float(x) for x in origin.get("rpy", "0 0 0").split()]
                else:
                    xyz = [0, 0, 0]
                    rpy = [0, 0, 0]

                axis = joint.find("axis")
                if axis is not None:
                    axis_xyz = [float(x) for x in axis.get("xyz", "0 0 1").split()]
                else:
                    axis_xyz = [0, 0, 1]

                limit = joint.find("limit")
                if limit is not None:
                    lower = float(limit.get("lower", "-3.14"))
                    upper = float(limit.get("upper", "3.14"))
                else:
                    lower, upper = -3.14, 3.14

                self.joints[joint_name] = Joint(
                    name=joint_name,
                    joint_type=joint_type,
                    parent=parent,
                    child=child,
                    origin=xyz + rpy,
                    axis=axis_xyz,
                    limits=(lower, upper)
                )

            # 解析关节后添加关节名称列表和默认角度
            self.joint_names = sorted([
                j.name for j in self.joints.values() 
                if j.joint_type in ["revolute", "prismatic"]
            ], key=lambda x: int(x.replace('joint', '')))
            
            # 确保关节名称排序正确
            if len(self.joint_names) > 0:
                try:
                    self.joint_names.sort(key=lambda x: int(x.replace('joint', '')))
                except ValueError:
                    pass
                    
            self.default_joint_angles = {name: 0.0 for name in self.joint_names}
            
            # 在解析完所有连杆后添加网格文件到缓存，增加详细异常捕获和日志
            for link in self.links.values():
                if link.visual_geometry and link.visual_geometry.get("type") == "mesh":
                    mesh_path = link.visual_geometry.get("filename")
                    if mesh_path and os.path.exists(mesh_path):
                        print(f"[INFO] 尝试加载网格: {mesh_path}")
                        mesh = try_load_mesh_with_trimesh(mesh_path)
                        if mesh is not None:
                            if hasattr(mesh, "geometry"):
                                for geometry_name, geometry in mesh.geometry.items():
                                    self.mesh_cache[f"{mesh_path}_{geometry_name}"] = geometry
                                    print(f"[DEBUG] 缓存Scene子网格: {mesh_path}_{geometry_name}")
                            else:
                                self.mesh_cache[mesh_path] = mesh
                                print(f"[DEBUG] 缓存Mesh: {mesh_path}")
                        else:
                            print(f"[ERROR] 无法加载网格: {mesh_path}")
                    else:
                        print(f"[WARNING] Mesh文件不存在或路径无效: {mesh_path}")
                        
            print(f"[DEBUG] Model loaded with {len(self.links)} links and {len(self.joints)} joints")
            print(f"[DEBUG] Joint names: {self.joint_names}")
            print(f"[DEBUG] Default joint angles: {self.default_joint_angles}")
            
            if is_calibrated:
                print("[INFO] 已加载标定后的URDF文件")
            else:
                if "rizon10" in robot_name.lower():
                    self.set_rizon10_mdh_parameters()
                    print("[DEBUG] Rizon10 MDH参数已设置")
            
            return True
        except Exception as e:
            print(f"加载URDF文件失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def get_joint_state(self) -> Dict[str, float]:
        """获取当前关节状态"""
        return self.default_joint_angles.copy()

    def get_joint_limits(self) -> List[Tuple[float, float]]:
        """获取所有关节的限位信息"""
        limits = []
        for joint in sorted(self.joints.values(), key=lambda x: x.name):
            if joint.joint_type in ["revolute", "prismatic"]:
                limits.append(joint.limits)
        return limits
        
    def set_rizon10_mdh_parameters(self):
        """设置 Rizon 10 机器人的 MDH 参数"""
        mdh_params = [
            (0, 0, 0.450, 0),       # Frame 1
            (np.pi/2, 0, 0.130, 0), # Frame 2
            (-np.pi/2, 0, 0.450, 0),# Frame 3
            (-np.pi/2, 0, 0.120, 0),# Frame 4
            (np.pi/2, 0, 0.395, 0), # Frame 5
            (np.pi/2, 0, 0.103, 0), # Frame 6
            (np.pi/2, 0.113, 0, 0), # Frame 7
            (0, 0, 0.096, np.pi)    # Flange
        ]
        self.robot_mdh_params = {"Rizon10": mdh_params}
        for i, params in enumerate(mdh_params):
            link_name = f"link{i+1}" if i < 7 else "flange"
            if link_name in self.links:
                self.links[link_name].set_mdh_params(*params)

    def get_link_parameters(self) -> List[Dict]:
        """获取所有连杆的参数信息"""
        parameters = []
        for link in self.links.values():
            parameters.append({
                "name": link.name,
                "geometry": link.visual_geometry,
                "origin": link.origin
            })
        return parameters

    def load_calibrated_urdf(self, calibrated_urdf_path: str) -> bool:
        """加载标定后的URDF文件
        
        Args:
            calibrated_urdf_path: 标定后的URDF文件路径
            
        Returns:
            bool: 加载是否成功
        """
        if not os.path.exists(calibrated_urdf_path):
            print(f"[ERROR] 标定后的URDF文件不存在: {calibrated_urdf_path}")
            return False
            
        print(f"[INFO] 开始加载标定后的URDF文件: {calibrated_urdf_path}")
        success = self.load_urdf(calibrated_urdf_path, is_calibrated=True)
        
        if success:
            print("[INFO] 标定后的URDF文件加载成功")
        else:
            print("[ERROR] 标定后的URDF文件加载失败")
            
        return success

    def update_kinematics(self, joint_angles: Dict[str, float]):
        """更新机器人运动学"""
        for name, angle in joint_angles.items():
            if name in self.default_joint_angles:
                self.default_joint_angles[name] = angle
        self.update_link_transforms()

    def parse_urdf(self, urdf_file):
        """Parse URDF file and build robot model"""
        # 删除这个冗余方法，因为它与load_urdf功能重复
        pass

    def _update_link_transform_recursive(self, parent_link):
        """
        递归更新子连杆的变换矩阵。
        对于每个以parent_link为父的关节，计算其子连杆的变换，并递归处理其子连杆。
        """
        for joint in self.joints.values():
            if joint.parent == parent_link.name:
                child_link = self.links[joint.child]
                # 获取父连杆的变换
                parent_transform = parent_link.get_transform()
                # 获取关节的变换（如果有运动变量，需考虑当前关节角度/位移）
                joint_transform = joint.get_transform(self.default_joint_angles.get(joint.name, 0.0))
                # 获取子连杆的MDH变换
                child_mdh_transform = child_link.get_transform_from_mdh()
                # 组合变换：父连杆 * 关节 * 子连杆MDH
                child_transform = parent_transform @ joint_transform @ child_mdh_transform
                child_link.set_transform(child_transform)
                # 递归处理下一级子连杆
                self._update_link_transform_recursive(child_link)
