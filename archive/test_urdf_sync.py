#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URDF同步功能测试脚本
用于验证和调试URDF同步功能

Author: LK
Date: 2025-01-XX
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.control.robot_control import RobotControl

def test_urdf_sync_paths():
    """测试URDF同步路径查找功能"""
    print("=== URDF同步路径测试 ===")
    
    # 模拟RobotControl的路径查找逻辑
    project_root = os.path.dirname(__file__)
    urdf_dir = os.path.join(project_root, 'resources', 'urdf')
    
    print(f"项目根目录: {project_root}")
    print(f"URDF目录: {urdf_dir}")
    print(f"URDF目录是否存在: {os.path.exists(urdf_dir)}")
    
    if os.path.exists(urdf_dir):
        print("\nURDF目录中的文件:")
        files = os.listdir(urdf_dir)
        urdf_files = [f for f in files if f.endswith('.urdf')]
        for i, file in enumerate(urdf_files, 1):
            print(f"  {i}. {file}")
    
    # 测试模板URDF文件查找
    possible_paths = [
        os.path.join(project_root, 'resources', 'urdf', 'flexiv_rizon4s_kinematics.urdf'),
        os.path.join(project_root, 'resources', 'urdf', 'flexiv_rizon4_kinematics.urdf'),
        os.path.join(project_root, 'resources', 'urdf', 'flexiv_rizon10s_kinematics.urdf'),
        os.path.join(project_root, 'resources', 'urdf', 'flexiv_rizon10_kinematics.urdf')
    ]
    
    print("\n模板URDF文件查找结果:")
    found_template = None
    for i, path in enumerate(possible_paths, 1):
        exists = os.path.exists(path)
        print(f"  {i}. {os.path.basename(path)}: {'✓' if exists else '✗'}")
        if exists and found_template is None:
            found_template = path
    
    if found_template:
        print(f"\n找到模板文件: {os.path.basename(found_template)}")
        return found_template
    else:
        print("\n❌ 未找到任何模板URDF文件")
        return None

def test_robot_control_init():
    """测试RobotControl初始化"""
    print("\n=== RobotControl初始化测试 ===")
    
    try:
        # 测试仿真模式初始化
        print("测试仿真模式初始化...")
        robot_control = RobotControl(robot_id="test-robot", hardware=False)
        print("✓ 仿真模式初始化成功")
        
        # 测试硬件模式初始化（如果Flexiv RDK可用）
        try:
            from flexivrdk import Robot, Model
            print("✓ Flexiv RDK可用")
            
            print("测试硬件模式初始化...")
            robot_control_hw = RobotControl(robot_id="test-robot", hardware=True)
            print("✓ 硬件模式初始化成功")
            
        except ImportError:
            print("⚠️  Flexiv RDK不可用，跳过硬件模式测试")
        except Exception as e:
            print(f"❌ 硬件模式初始化失败: {str(e)}")
            
    except Exception as e:
        print(f"❌ RobotControl初始化失败: {str(e)}")
        return False
    
    return True

def test_sync_urdf_logic():
    """测试URDF同步逻辑"""
    print("\n=== URDF同步逻辑测试 ===")
    
    try:
        # 创建仿真模式的RobotControl实例
        robot_control = RobotControl(robot_id="test-robot", hardware=False)
        
        # 测试仿真模式下的同步（应该失败）
        print("测试仿真模式下的URDF同步...")
        result = robot_control.sync_urdf()
        if not result:
            print("✓ 仿真模式正确拒绝URDF同步")
        else:
            print("❌ 仿真模式不应该允许URDF同步")
        
        # 如果Flexiv RDK可用，测试硬件模式
        try:
            from flexivrdk import Robot, Model
            print("\n测试硬件模式下的URDF同步逻辑...")
            robot_control_hw = RobotControl(robot_id="test-robot", hardware=True)
            
            # 注意：这里不会真正连接机器人，只是测试逻辑
            print("⚠️  硬件模式需要真实机器人连接才能完成同步测试")
            
        except ImportError:
            print("⚠️  Flexiv RDK不可用，跳过硬件模式同步测试")
            
    except Exception as e:
        print(f"❌ URDF同步逻辑测试失败: {str(e)}")
        return False
    
    return True

def print_troubleshooting_guide():
    """打印故障排除指南"""
    print("\n" + "="*50)
    print("URDF同步功能故障排除指南")
    print("="*50)
    
    print("\n1. 检查前提条件:")
    print("   ✓ 确保已安装Flexiv RDK")
    print("   ✓ 确保机器人已连接并使能")
    print("   ✓ 确保在硬件模式下运行（非仿真模式）")
    
    print("\n2. 检查文件路径:")
    print("   ✓ 确保resources/urdf目录存在")
    print("   ✓ 确保目录中有对应的URDF模板文件")
    print("   ✓ 检查文件权限是否正确")
    
    print("\n3. 常见错误及解决方案:")
    print("   • 'Model实例未初始化': 确保机器人已连接并启动了控制线程")
    print("   • '仿真模式下无法同步': 切换到硬件模式")
    print("   • '未找到模板URDF文件': 检查resources/urdf目录")
    print("   • 'Robot实例未初始化': 确保机器人连接成功")
    
    print("\n4. 调试步骤:")
    print("   1. 运行此测试脚本检查基础配置")
    print("   2. 检查应用日志中的详细错误信息")
    print("   3. 确认机器人序列号正确")
    print("   4. 检查网络连接和防火墙设置")
    
    print("\n5. 成功同步后:")
    print("   ✓ 会在resources/urdf目录生成*_calibrated.urdf文件")
    print("   ✓ 应用会自动重新加载标定后的模型")
    print("   ✓ 3D可视化会更新为标定后的运动学参数")

def main():
    """主测试函数"""
    print("URDF同步功能测试工具")
    print("=" * 30)
    
    # 执行各项测试
    template_found = test_urdf_sync_paths()
    control_init_ok = test_robot_control_init()
    sync_logic_ok = test_sync_urdf_logic()
    
    # 总结测试结果
    print("\n" + "="*30)
    print("测试结果总结")
    print("="*30)
    print(f"模板URDF文件: {'✓' if template_found else '❌'}")
    print(f"RobotControl初始化: {'✓' if control_init_ok else '❌'}")
    print(f"同步逻辑: {'✓' if sync_logic_ok else '❌'}")
    
    if template_found and control_init_ok and sync_logic_ok:
        print("\n🎉 基础配置检查通过！")
        print("现在可以尝试连接真实机器人并测试URDF同步功能。")
    else:
        print("\n⚠️  发现配置问题，请参考故障排除指南。")
    
    # 打印故障排除指南
    print_troubleshooting_guide()

if __name__ == "__main__":
    main()