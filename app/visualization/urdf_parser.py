import xml.etree.ElementTree as ET
import numpy as np

class URDFParser:
    def parse(self, urdf_path):
        tree = ET.parse(urdf_path)
        root = tree.getroot()
        robot = {'links': [], 'joints': [], 'materials': {}}
        # 解析材质
        for material in root.findall('material'):
            name = material.get('name')
            color = material.find('color')
            rgba = [1,1,1,1]
            if color is not None:
                rgba = [float(x) for x in color.get('rgba').split()]
            robot['materials'][name] = rgba
        # 解析link
        for link in root.findall('link'):
            link_data = {'name': link.get('name'), 'visual': [], 'material': None}
            visual = link.find('visual')
            if visual is not None:
                geometry = visual.find('geometry')
                mesh = geometry.find('mesh') if geometry is not None else None
                if mesh is not None:
                    filename = mesh.get('filename')
                    origin = visual.find('origin')
                    xyz = [0,0,0]
                    rpy = [0,0,0]
                    if origin is not None:
                        if origin.get('xyz'):
                            xyz = [float(x) for x in origin.get('xyz').split()]
                        if origin.get('rpy'):
                            rpy = [float(x) for x in origin.get('rpy').split()]
                    link_data['visual'].append({'type': 'mesh', 'filename': filename, 'origin': {'xyz': xyz, 'rpy': rpy}})
                material = visual.find('material')
                if material is not None:
                    link_data['material'] = material.get('name')
            robot['links'].append(link_data)
        
        # 解析joint
        for joint in root.findall('joint'):
            joint_data = {
                'name': joint.get('name'),
                'type': joint.get('type'),
                'parent': joint.find('parent').get('link'),
                'child': joint.find('child').get('link'),
                'axis': [0,0,1],
                'origin': {'xyz': [0,0,0], 'rpy': [0,0,0]}
            }
            axis = joint.find('axis')
            if axis is not None and axis.get('xyz'):
                joint_data['axis'] = [float(x) for x in axis.get('xyz').split()]
            origin = joint.find('origin')
            if origin is not None:
                if origin.get('xyz'):
                    joint_data['origin']['xyz'] = [float(x) for x in origin.get('xyz').split()]
                if origin.get('rpy'):
                    joint_data['origin']['rpy'] = [float(x) for x in origin.get('rpy').split()]
            robot['joints'].append(joint_data)
        
        # 为每个link添加父关节信息
        for link in robot['links']:
            link['parent_joint'] = None
            for joint in robot['joints']:
                if joint['child'] == link['name']:
                    link['parent_joint'] = joint['name']
                    break
        return robot 