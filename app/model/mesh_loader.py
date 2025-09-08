"""
网格加载器 - 负责加载和缓存网格文件
"""
import trimesh
import os
from typing import Dict, Optional

class MeshLoader:
    def __init__(self):
        self.cache: Dict[str, trimesh.Trimesh] = {}
    
    def load_mesh(self, mesh_path: str) -> Optional[trimesh.Trimesh]:
        """加载网格文件并缓存"""
        # 支持 package://meshes/ 路径
        if mesh_path.startswith('package://meshes/'):
            # 计算到ui/resources目录的正确路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ui_resources_dir = os.path.join(current_dir, '..', 'ui', 'resources')
            mesh_path = os.path.join(ui_resources_dir, 'meshes', mesh_path[len('package://meshes/'):])
        
        if mesh_path in self.cache:
            return self.cache[mesh_path]
        
        try:
            mesh = trimesh.load(mesh_path, force='mesh')
            self.cache[mesh_path] = mesh
            return mesh
        except Exception as e:
            print(f"[MeshLoader] 加载失败: {mesh_path}, 错误: {e}")
            return None