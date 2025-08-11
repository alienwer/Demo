'''
Author: LK
Date: 2025-07-18 16:22:32
LastEditTime: 2025-07-18 17:20:12
LastEditors: LK
Description: 
FilePath: /Demo/app/visualization/mesh_loader.py
'''
import trimesh

class MeshLoader:
    def __init__(self):
        self.cache = {}
    def load_mesh(self, mesh_path):
        # 支持 package://meshes/ 路径
        if mesh_path.startswith('package://meshes/'):
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            mesh_path = os.path.join(project_root, 'resources', 'meshes', mesh_path[len('package://meshes/'):])
        if mesh_path in self.cache:
            return self.cache[mesh_path]
        try:
            mesh = trimesh.load(mesh_path, force='mesh')
            self.cache[mesh_path] = mesh
            return mesh
        except Exception as e:
            print(f"[MeshLoader] 加载失败: {mesh_path}, 错误: {e}")
            return None 