"""
运动学计算模块
提供正向运动学、逆向运动学和雅可比矩阵计算功能
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.spatial.transform import Rotation


class KinematicsSolver:
    """运动学求解器"""
    
    def __init__(self, urdf_model: Dict[str, any]):
        """
        初始化运动学求解器
        
        Args:
            urdf_model: URDF解析器返回的机器人模型字典
        """
        self.urdf_model = urdf_model
        self.joints = urdf_model.get('joints', {})
        self.links = urdf_model.get('links', {})
        
        # 构建运动学链
        self.kinematic_chain = self._build_kinematic_chain()
        
    def _build_kinematic_chain(self) -> List[Dict[str, any]]:
        """构建运动学链"""
        chain = []
        current_link = self.urdf_model.get('root_link')
        
        while current_link:
            # 找到连接到当前链接的关节
            joint_for_link = None
            for joint_name, joint_data in self.joints.items():
                if joint_data['child'] == current_link:
                    joint_for_link = joint_data
                    joint_for_link['name'] = joint_name
                    break
            
            if not joint_for_link:
                break
                
            chain.append({
                'joint': joint_for_link,
                'link': self.links.get(current_link, {})
            })
            
            # 移动到父链接
            current_link = joint_for_link.get('parent')
            
        return list(reversed(chain))  # 从基座到末端执行器
    
    def forward_kinematics(self, joint_angles: Dict[str, float]) -> np.ndarray:
        """
        正向运动学计算
        
        Args:
            joint_angles: 关节角度字典 {关节名: 角度(弧度)}
            
        Returns:
            4x4齐次变换矩阵，表示末端执行器位姿
        """
        # 从基座坐标系开始
        T = np.eye(4)
        
        for segment in self.kinematic_chain:
            joint_data = segment['joint']
            joint_name = joint_data['name']
            
            # 获取关节角度（默认为0）
            angle = joint_angles.get(joint_name, 0.0)
            
            # 获取关节原点变换
            origin = joint_data.get('origin', {})
            xyz = origin.get('xyz', [0, 0, 0])
            rpy = origin.get('rpy', [0, 0, 0])
            
            # 构建关节变换矩阵
            T_joint = self._build_transform_matrix(xyz, rpy)
            
            # 根据关节类型添加关节变换
            if joint_data['type'] == 'revolute':
                # 旋转关节
                axis = joint_data.get('axis', [1, 0, 0])
                R_joint = self._rotation_matrix(axis, angle)
                T_joint_rot = np.eye(4)
                T_joint_rot[:3, :3] = R_joint
                T_joint = T_joint @ T_joint_rot
            elif joint_data['type'] == 'prismatic':
                # 平移关节
                axis = joint_data.get('axis', [1, 0, 0])
                T_joint_trans = np.eye(4)
                T_joint_trans[:3, 3] = np.array(axis) * angle
                T_joint = T_joint @ T_joint_trans
            
            # 累积变换
            T = T @ T_joint
            
            # 添加链接变换（如果有）
            link_origin = segment['link'].get('origin', {})
            if 'xyz' in link_origin or 'rpy' in link_origin:
                link_xyz = link_origin.get('xyz', [0, 0, 0])
                link_rpy = link_origin.get('rpy', [0, 0, 0])
                T_link = self._build_transform_matrix(link_xyz, link_rpy)
                T = T @ T_link
        
        return T
    
    def inverse_kinematics(self, 
                          target_pose: np.ndarray,
                          initial_angles: Optional[Dict[str, float]] = None,
                          max_iterations: int = 100,
                          tolerance: float = 1e-6) -> Tuple[Dict[str, float], bool]:
        """
        逆向运动学计算（使用雅可比矩阵伪逆）
        
        Args:
            target_pose: 目标位姿（4x4齐次变换矩阵）
            initial_angles: 初始关节角度（可选）
            max_iterations: 最大迭代次数
            tolerance: 收敛容差
            
        Returns:
            (关节角度字典, 是否收敛)
        """
        # 初始化关节角度
        if initial_angles is None:
            current_angles = {name: 0.0 for name in self.joints.keys()}
        else:
            current_angles = initial_angles.copy()
        
        for iteration in range(max_iterations):
            # 计算当前位姿
            current_pose = self.forward_kinematics(current_angles)
            
            # 计算位姿误差
            error = self._pose_error(current_pose, target_pose)
            
            if np.linalg.norm(error) < tolerance:
                return current_angles, True
            
            # 计算雅可比矩阵
            J = self.jacobian(current_angles)
            
            # 使用伪逆求解关节角度增量
            J_pinv = np.linalg.pinv(J)
            delta_theta = J_pinv @ error
            
            # 更新关节角度
            joint_names = list(self.joints.keys())
            for i, joint_name in enumerate(joint_names):
                current_angles[joint_name] += delta_theta[i]
                
                # 应用关节限制
                limits = self.joints[joint_name].get('limits', {})
                if 'lower' in limits and 'upper' in limits:
                    current_angles[joint_name] = np.clip(
                        current_angles[joint_name],
                        limits['lower'],
                        limits['upper']
                    )
        
        return current_angles, False
    
    def jacobian(self, joint_angles: Dict[str, float]) -> np.ndarray:
        """
        计算雅可比矩阵
        
        Args:
            joint_angles: 当前关节角度
            
        Returns:
            6xN雅可比矩阵（N为关节数量）
        """
        n_joints = len(self.joints)
        J = np.zeros((6, n_joints))
        
        # 计算末端执行器位姿
        T_end = self.forward_kinematics(joint_angles)
        p_end = T_end[:3, 3]
        
        joint_names = list(self.joints.keys())
        
        for j in range(n_joints):
            # 计算第j个关节的位姿
            partial_angles = {name: 0.0 for name in joint_names}
            for i in range(j + 1):
                partial_angles[joint_names[i]] = joint_angles[joint_names[i]]
            
            T_joint = self.forward_kinematics(partial_angles)
            p_joint = T_joint[:3, 3]
            
            # 获取关节轴（在基座坐标系中）
            joint_data = self.joints[joint_names[j]]
            axis_local = np.array(joint_data.get('axis', [1, 0, 0]))
            
            # 将关节轴转换到基座坐标系
            R_joint = T_joint[:3, :3]
            axis_world = R_joint @ axis_local
            
            # 计算雅可比矩阵列
            if joint_data['type'] == 'revolute':
                # 旋转关节
                J[:3, j] = np.cross(axis_world, p_end - p_joint)
                J[3:, j] = axis_world
            elif joint_data['type'] == 'prismatic':
                # 平移关节
                J[:3, j] = axis_world
                J[3:, j] = np.zeros(3)
        
        return J
    
    def _build_transform_matrix(self, xyz: List[float], rpy: List[float]) -> np.ndarray:
        """构建齐次变换矩阵"""
        T = np.eye(4)
        
        # 设置平移
        T[:3, 3] = np.array(xyz)
        
        # 设置旋转（RPY顺序：Roll-Pitch-Yaw）
        if any(rpy):
            R = Rotation.from_euler('xyz', rpy).as_matrix()
            T[:3, :3] = R
        
        return T
    
    def _rotation_matrix(self, axis: List[float], angle: float) -> np.ndarray:
        """绕任意轴旋转的旋转矩阵"""
        axis = np.array(axis)
        axis = axis / np.linalg.norm(axis)  # 归一化
        
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        
        # 罗德里格斯旋转公式
        R = np.eye(3) * cos_a
        R += np.outer(axis, axis) * (1 - cos_a)
        R += np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ]) * sin_a
        
        return R
    
    def _pose_error(self, current_pose: np.ndarray, target_pose: np.ndarray) -> np.ndarray:
        """计算位姿误差"""
        error = np.zeros(6)
        
        # 位置误差
        error[:3] = target_pose[:3, 3] - current_pose[:3, 3]
        
        # 姿态误差（使用轴角表示）
        R_current = current_pose[:3, :3]
        R_target = target_pose[:3, :3]
        R_error = R_target @ R_current.T
        
        # 从旋转矩阵提取轴角
        angle = np.arccos((np.trace(R_error) - 1) / 2)
        if abs(angle) > 1e-6:
            axis = np.array([
                R_error[2, 1] - R_error[1, 2],
                R_error[0, 2] - R_error[2, 0],
                R_error[1, 0] - R_error[0, 1]
            ]) / (2 * np.sin(angle))
            error[3:] = axis * angle
        
        return error


def create_kinematics_solver(urdf_model: Dict[str, any]) -> KinematicsSolver:
    """创建运动学求解器实例"""
    return KinematicsSolver(urdf_model)