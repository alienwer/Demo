# URDF解析器 - 支持多种URDF格式和模型缓存
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import os
import hashlib
import json
from pathlib import Path

class URDFParser:
    """URDF解析器，支持多种格式和模型缓存"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """初始化URDF解析器
        
        Args:
            cache_dir: 缓存目录路径，如果为None则禁用缓存
        """
        self.cache_dir = cache_dir
        self._mesh_cache: Dict[str, Dict] = {}
        self._material_cache: Dict[str, Dict] = {}
        
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    def load_urdf(self, urdf_path: str, use_cache: bool = True) -> Dict[str, Any]:
        """加载URDF文件
        
        Args:
            urdf_path: URDF文件路径
            use_cache: 是否使用缓存
            
        Returns:
            解析后的机器人模型数据
        """
        urdf_path = os.path.abspath(urdf_path)
        
        # 检查缓存
        cache_key = self._get_cache_key(urdf_path)
        if use_cache and self.cache_dir:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                print(f"从缓存加载URDF模型: {urdf_path}")
                return cached_data
        
        print(f"解析URDF文件: {urdf_path}")
        
        try:
            # 解析URDF文件
            tree = ET.parse(urdf_path)
            root = tree.getroot()
            
            # 提取机器人基本信息
            robot_info = self._parse_robot_info(root)
            
            # 解析链接(links)
            links = self._parse_links(root)
            
            # 解析关节(joints)
            joints = self._parse_joints(root)
            
            # 解析材料(materials)
            materials = self._parse_materials(root)
            
            # 构建机器人模型
            robot_model = {
                'name': robot_info.get('name', 'unknown'),
                'links': links,
                'joints': joints,
                'materials': materials,
                'metadata': {
                    'urdf_path': urdf_path,
                    'file_hash': cache_key,
                    'link_count': len(links),
                    'joint_count': len(joints),
                    'dof': self._calculate_dof(joints)
                }
            }
            
            # 保存到缓存
            if use_cache and self.cache_dir:
                self._save_to_cache(cache_key, robot_model)
            
            return robot_model
            
        except Exception as e:
            print(f"URDF解析失败: {e}")
            raise
    
    def _parse_robot_info(self, root: ET.Element) -> Dict[str, Any]:
        """解析机器人基本信息"""
        robot_info = {}
        
        # 机器人名称
        if 'name' in root.attrib:
            robot_info['name'] = root.attrib['name']
        
        # 其他属性
        for attr in ['version', 'type']:
            if attr in root.attrib:
                robot_info[attr] = root.attrib[attr]
        
        return robot_info
    
    def _parse_links(self, root: ET.Element) -> Dict[str, Dict]:
        """解析链接(links)"""
        links = {}
        
        for link_elem in root.findall('link'):
            link_name = link_elem.attrib.get('name', 'unknown')
            link_data = {
                'name': link_name,
                'visual': [],
                'collision': [],
                'inertial': None
            }
            
            # 解析视觉几何体
            for visual_elem in link_elem.findall('visual'):
                visual_data = self._parse_geometry(visual_elem, 'visual')
                if visual_data:
                    link_data['visual'].append(visual_data)
            
            # 解析碰撞几何体
            for collision_elem in link_elem.findall('collision'):
                collision_data = self._parse_geometry(collision_elem, 'collision')
                if collision_data:
                    link_data['collision'].append(collision_data)
            
            # 解析惯性参数
            inertial_elem = link_elem.find('inertial')
            if inertial_elem is not None:
                link_data['inertial'] = self._parse_inertial(inertial_elem)
            
            links[link_name] = link_data
        
        return links
    
    def _parse_geometry(self, elem: ET.Element, geom_type: str) -> Optional[Dict]:
        """解析几何体"""
        geometry_data = {'type': geom_type}
        
        # 解析原点(origin)
        origin_elem = elem.find('origin')
        if origin_elem is not None:
            geometry_data['origin'] = self._parse_origin(origin_elem)
        
        # 解析几何体类型
        geometry_elem = elem.find('geometry')
        if geometry_elem is not None:
            # 检查几何体类型
            for geom_type in ['box', 'cylinder', 'sphere', 'mesh']:
                geom_elem = geometry_elem.find(geom_type)
                if geom_elem is not None:
                    geometry_data['shape'] = geom_type
                    geometry_data['parameters'] = self._parse_shape_parameters(geom_elem, geom_type)
                    break
        
        # 解析材质
        material_elem = elem.find('material')
        if material_elem is not None:
            geometry_data['material'] = self._parse_material(material_elem)
        
        return geometry_data if 'shape' in geometry_data else None
    
    def _parse_origin(self, origin_elem: ET.Element) -> Dict[str, Any]:
        """解析原点变换"""
        origin = {'xyz': [0.0, 0.0, 0.0], 'rpy': [0.0, 0.0, 0.0]}
        
        if 'xyz' in origin_elem.attrib:
            origin['xyz'] = [float(x) for x in origin_elem.attrib['xyz'].split()]
        
        if 'rpy' in origin_elem.attrib:
            origin['rpy'] = [float(x) for x in origin_elem.attrib['rpy'].split()]
        
        return origin
    
    def _parse_shape_parameters(self, geom_elem: ET.Element, geom_type: str) -> Dict[str, Any]:
        """解析几何体参数"""
        params = {}
        
        if geom_type == 'box':
            if 'size' in geom_elem.attrib:
                params['size'] = [float(x) for x in geom_elem.attrib['size'].split()]
        
        elif geom_type == 'cylinder':
            if 'radius' in geom_elem.attrib:
                params['radius'] = float(geom_elem.attrib['radius'])
            if 'length' in geom_elem.attrib:
                params['length'] = float(geom_elem.attrib['length'])
        
        elif geom_type == 'sphere':
            if 'radius' in geom_elem.attrib:
                params['radius'] = float(geom_elem.attrib['radius'])
        
        elif geom_type == 'mesh':
            if 'filename' in geom_elem.attrib:
                filename = geom_elem.attrib['filename']
                # 解析package://协议
                if filename.startswith('package://'):
                    filename = self._resolve_package_uri(filename)
                params['filename'] = filename
            if 'scale' in geom_elem.attrib:
                params['scale'] = [float(x) for x in geom_elem.attrib['scale'].split()]
        
        return params
    
    def _parse_material(self, material_elem: ET.Element) -> Dict[str, Any]:
        """解析材质"""
        material = {}
        
        if 'name' in material_elem.attrib:
            material['name'] = material_elem.attrib['name']
        
        # 解析颜色
        color_elem = material_elem.find('color')
        if color_elem is not None and 'rgba' in color_elem.attrib:
            material['color'] = [float(x) for x in color_elem.attrib['rgba'].split()]
        
        # 解析纹理
        texture_elem = material_elem.find('texture')
        if texture_elem is not None and 'filename' in texture_elem.attrib:
            material['texture'] = texture_elem.attrib['filename']
        
        return material
    
    def _parse_inertial(self, inertial_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """解析惯性参数"""
        inertial = {}
        
        # 解析质量
        mass_elem = inertial_elem.find('mass')
        if mass_elem is not None and 'value' in mass_elem.attrib:
            inertial['mass'] = float(mass_elem.attrib['value'])
        
        # 解析惯性矩阵
        inertia_elem = inertial_elem.find('inertia')
        if inertia_elem is not None:
            inertial_matrix = np.zeros((3, 3))
            for attr in ['ixx', 'ixy', 'ixz', 'iyy', 'iyz', 'izz']:
                if attr in inertia_elem.attrib:
                    value = float(inertia_elem.attrib[attr])
                    if attr == 'ixx': inertial_matrix[0, 0] = value
                    elif attr == 'ixy': inertial_matrix[0, 1] = value
                    elif attr == 'ixz': inertial_matrix[0, 2] = value
                    elif attr == 'iyy': inertial_matrix[1, 1] = value
                    elif attr == 'iyz': inertial_matrix[1, 2] = value
                    elif attr == 'izz': inertial_matrix[2, 2] = value
            
            # 填充对称部分
            inertial_matrix[1, 0] = inertial_matrix[0, 1]
            inertial_matrix[2, 0] = inertial_matrix[0, 2]
            inertial_matrix[2, 1] = inertial_matrix[1, 2]
            
            inertial['inertia'] = inertial_matrix.tolist()
        
        return inertial if inertial else None
    
    def _parse_joints(self, root: ET.Element) -> Dict[str, Dict]:
        """解析关节"""
        joints = {}
        
        for joint_elem in root.findall('joint'):
            joint_name = joint_elem.attrib.get('name', 'unknown')
            joint_type = joint_elem.attrib.get('type', 'fixed')
            
            joint_data = {
                'name': joint_name,
                'type': joint_type,
                'parent': None,
                'child': None,
                'axis': [1.0, 0.0, 0.0],  # 默认X轴
                'limits': None,
                'origin': {'xyz': [0.0, 0.0, 0.0], 'rpy': [0.0, 0.0, 0.0]}
            }
            
            # 解析父链接和子链接
            parent_elem = joint_elem.find('parent')
            if parent_elem is not None and 'link' in parent_elem.attrib:
                joint_data['parent'] = parent_elem.attrib['link']
            
            child_elem = joint_elem.find('child')
            if child_elem is not None and 'link' in child_elem.attrib:
                joint_data['child'] = child_elem.attrib['link']
            
            # 解析关节轴
            axis_elem = joint_elem.find('axis')
            if axis_elem is not None and 'xyz' in axis_elem.attrib:
                joint_data['axis'] = [float(x) for x in axis_elem.attrib['xyz'].split()]
            
            # 解析原点
            origin_elem = joint_elem.find('origin')
            if origin_elem is not None:
                joint_data['origin'] = self._parse_origin(origin_elem)
            
            # 解析限制
            limit_elem = joint_elem.find('limit')
            if limit_elem is not None:
                limits = {}
                for attr in ['lower', 'upper', 'effort', 'velocity']:
                    if attr in limit_elem.attrib:
                        limits[attr] = float(limit_elem.attrib[attr])
                joint_data['limits'] = limits
            
            joints[joint_name] = joint_data
        
        return joints
    
    def _parse_materials(self, root: ET.Element) -> Dict[str, Dict]:
        """解析全局材料"""
        materials = {}
        
        for material_elem in root.findall('material'):
            material_data = self._parse_material(material_elem)
            if 'name' in material_data:
                materials[material_data['name']] = material_data
        
        return materials
    
    def _calculate_dof(self, joints: Dict[str, Dict]) -> int:
        """计算自由度"""
        dof = 0
        for joint in joints.values():
            if joint['type'] in ['revolute', 'prismatic', 'continuous']:
                dof += 1
        return dof
    
    def _resolve_package_uri(self, uri: str) -> str:
        """解析package://协议URI
        
        Args:
            uri: package://协议URI，格式为package://package_name/path/to/file
            
        Returns:
            解析后的绝对文件路径
        """
        if not uri.startswith('package://'):
            return uri
        
        # 移除package://前缀
        path_part = uri[10:]  # len('package://') = 10
        
        # 分割包名和文件路径
        parts = path_part.split('/', 1)
        if len(parts) < 2:
            print(f"警告: 无效的package URI格式: {uri}")
            return uri
        
        package_name, file_path = parts
        
        # 查找包对应的资源目录
        package_dirs = {
            'meshes': '/Users/liangkang/WorkSpace-Me/Demo/resources/meshes',
            'urdf': '/Users/liangkang/WorkSpace-Me/Demo/resources/urdf'
        }
        
        if package_name in package_dirs:
            resolved_path = os.path.join(package_dirs[package_name], file_path)
            if os.path.exists(resolved_path):
                return resolved_path
            else:
                print(f"警告: 包资源文件不存在: {resolved_path}")
                return uri
        else:
            print(f"警告: 未知的包名: {package_name}")
            return uri
    
    def _get_cache_key(self, urdf_path: str) -> str:
        """生成缓存键"""
        # 基于文件内容和修改时间生成唯一键
        file_stat = os.stat(urdf_path)
        file_hash = hashlib.md5()
        
        with open(urdf_path, 'rb') as f:
            file_hash.update(f.read())
        
        return f"{file_hash.hexdigest()}_{file_stat.st_mtime}"
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从缓存加载数据"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"缓存加载失败: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """保存数据到缓存"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"缓存保存失败: {e}")
    
    def clear_cache(self):
        """清空缓存"""
        if self.cache_dir and os.path.exists(self.cache_dir):
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
            print("URDF缓存已清空")

# 工具函数
def create_urdf_parser(cache_dir: Optional[str] = None) -> URDFParser:
    """创建URDF解析器实例"""
    return URDFParser(cache_dir)