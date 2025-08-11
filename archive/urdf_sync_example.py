#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URDF同步功能使用示例

本示例展示如何在代码中使用URDF同步功能，包括:
1. 连接机器人
2. 执行URDF同步
3. 加载标定后的URDF文件
4. 错误处理

Author: LK
Date: 2025-01-XX
"""

import os
import sys
import time

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.control.robot_control import RobotControl
from app.model.robot_model import RobotModel

def connect_robot(robot_sn: str, hardware_mode: bool = True) -> RobotControl:
    """
    连接机器人
    
    Args:
        robot_sn: 机器人序列号
        hardware_mode: 是否使用硬件模式
        
    Returns:
        RobotControl: 机器人控制实例
    """
    print(f"正在连接机器人: {robot_sn}...")
    
    try:
        # 创建RobotControl实例
        robot_control = RobotControl(robot_id=robot_sn, hardware=hardware_mode)
        
        if hardware_mode:
            # 硬件模式下检查连接状态
            if hasattr(robot_control, 'robot') and robot_control.robot:
                # 等待连接建立
                for i in range(10):  # 最多等待5秒
                    if robot_control.robot.connected():
                        print(f"✓ 机器人连接成功: {robot_sn}")
                        return robot_control
                    time.sleep(0.5)
                    print(f"连接尝试 {i+1}/10...")
                
                print(f"❌ 机器人连接失败: 无法建立与 {robot_sn} 的连接")
                return None
            else:
                print("❌ Robot实例创建失败")
                return None
        else:
            # 仿真模式
            print(f"✓ 仿真模式连接: {robot_sn}")
            return robot_control
            
    except Exception as e:
        print(f"❌ 连接机器人异常: {str(e)}")
        return None

def sync_urdf_with_robot(robot_control: RobotControl, template_urdf_path: str = None) -> bool:
    """
    执行URDF同步
    
    Args:
        robot_control: 机器人控制实例
        template_urdf_path: 模板URDF文件路径（可选）
        
    Returns:
        bool: 同步是否成功
    """
    print("开始URDF同步...")
    
    try:
        # 执行同步
        success = robot_control.sync_urdf(template_urdf_path)
        
        if success:
            print("✓ URDF同步成功")
            return True
        else:
            print("❌ URDF同步失败")
            return False
            
    except Exception as e:
        print(f"❌ URDF同步异常: {str(e)}")
        return False

def find_calibrated_urdf() -> str:
    """
    查找标定后的URDF文件
    
    Returns:
        str: 标定后URDF文件路径，如果未找到则返回None
    """
    project_root = os.path.dirname(os.path.dirname(__file__))
    urdf_dir = os.path.join(project_root, 'resources', 'urdf')
    
    # 可能的标定后URDF文件名
    calibrated_files = [
        'flexiv_rizon4s_kinematics_calibrated.urdf',
        'flexiv_rizon4_kinematics_calibrated.urdf',
        'flexiv_rizon10s_kinematics_calibrated.urdf',
        'flexiv_rizon10_kinematics_calibrated.urdf'
    ]
    
    for filename in calibrated_files:
        path = os.path.join(urdf_dir, filename)
        if os.path.exists(path):
            print(f"✓ 找到标定后URDF文件: {filename}")
            return path
    
    print("❌ 未找到标定后URDF文件")
    return None

def load_calibrated_model(calibrated_urdf_path: str) -> RobotModel:
    """
    加载标定后的机器人模型
    
    Args:
        calibrated_urdf_path: 标定后URDF文件路径
        
    Returns:
        RobotModel: 机器人模型实例
    """
    print(f"加载标定后的机器人模型: {os.path.basename(calibrated_urdf_path)}")
    
    try:
        robot_model = RobotModel()
        success = robot_model.load_calibrated_urdf(calibrated_urdf_path)
        
        if success:
            print("✓ 标定后模型加载成功")
            return robot_model
        else:
            print("❌ 标定后模型加载失败")
            return None
            
    except Exception as e:
        print(f"❌ 加载标定后模型异常: {str(e)}")
        return None

def complete_urdf_sync_workflow(robot_sn: str, hardware_mode: bool = True):
    """
    完整的URDF同步工作流程
    
    Args:
        robot_sn: 机器人序列号
        hardware_mode: 是否使用硬件模式
    """
    print("=" * 50)
    print("URDF同步完整工作流程")
    print("=" * 50)
    
    # 步骤1: 连接机器人
    print("\n步骤1: 连接机器人")
    robot_control = connect_robot(robot_sn, hardware_mode)
    
    if not robot_control:
        print("❌ 机器人连接失败，终止流程")
        return False
    
    # 步骤2: 启动机器人控制线程（硬件模式下）
    if hardware_mode:
        print("\n步骤2: 启动机器人控制线程")
        try:
            robot_control.start()
            time.sleep(2)  # 等待线程启动
            print("✓ 机器人控制线程已启动")
        except Exception as e:
            print(f"❌ 启动控制线程失败: {str(e)}")
            return False
    
    # 步骤3: 执行URDF同步
    print("\n步骤3: 执行URDF同步")
    sync_success = sync_urdf_with_robot(robot_control)
    
    if not sync_success:
        print("❌ URDF同步失败，终止流程")
        return False
    
    # 步骤4: 查找标定后的URDF文件
    print("\n步骤4: 查找标定后URDF文件")
    calibrated_urdf_path = find_calibrated_urdf()
    
    if not calibrated_urdf_path:
        print("❌ 未找到标定后URDF文件，终止流程")
        return False
    
    # 步骤5: 加载标定后的模型
    print("\n步骤5: 加载标定后模型")
    robot_model = load_calibrated_model(calibrated_urdf_path)
    
    if not robot_model:
        print("❌ 加载标定后模型失败")
        return False
    
    # 步骤6: 验证同步结果
    print("\n步骤6: 验证同步结果")
    print("✓ URDF同步工作流程完成")
    print(f"✓ 标定后URDF文件: {os.path.basename(calibrated_urdf_path)}")
    print("✓ 机器人模型已更新为标定后参数")
    
    # 清理资源
    if hardware_mode and robot_control:
        try:
            robot_control.stop_robot()
            print("✓ 机器人控制已停止")
        except Exception as e:
            print(f"⚠️  停止机器人控制时出现异常: {str(e)}")
    
    return True

def example_error_handling():
    """
    错误处理示例
    """
    print("\n=" * 50)
    print("错误处理示例")
    print("=" * 50)
    
    # 示例1: 仿真模式下尝试同步（应该失败）
    print("\n示例1: 仿真模式下尝试同步")
    robot_control_sim = RobotControl(robot_id="test-robot", hardware=False)
    result = robot_control_sim.sync_urdf()
    print(f"仿真模式同步结果: {'成功' if result else '失败（预期）'}")
    
    # 示例2: 无效路径处理
    print("\n示例2: 使用无效模板路径")
    robot_control_hw = RobotControl(robot_id="test-robot", hardware=True)
    result = robot_control_hw.sync_urdf("/invalid/path/template.urdf")
    print(f"无效路径同步结果: {'成功' if result else '失败（预期）'}")

def main():
    """
    主函数 - 演示URDF同步功能的使用
    """
    print("URDF同步功能使用示例")
    
    # 配置参数
    ROBOT_SN = "Rizon4-062468"  # 替换为实际的机器人序列号
    HARDWARE_MODE = True  # 设置为False进行仿真模式测试
    
    # 检查是否为演示模式
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("\n运行演示模式（仅显示错误处理示例）")
        example_error_handling()
        return
    
    # 警告信息
    if HARDWARE_MODE:
        print("\n⚠️  警告: 当前配置为硬件模式")
        print("请确保:")
        print("1. 机器人已正确连接")
        print("2. 机器人序列号正确")
        print("3. 网络连接正常")
        print("\n如果没有实际机器人，请将HARDWARE_MODE设置为False")
        
        response = input("\n是否继续？(y/N): ")
        if response.lower() != 'y':
            print("已取消操作")
            return
    
    # 执行完整工作流程
    success = complete_urdf_sync_workflow(ROBOT_SN, HARDWARE_MODE)
    
    if success:
        print("\n🎉 URDF同步示例执行成功！")
    else:
        print("\n❌ URDF同步示例执行失败")
        print("\n请检查:")
        print("1. 机器人连接状态")
        print("2. 网络连接")
        print("3. Flexiv RDK安装")
        print("4. 文件权限")
    
    # 显示错误处理示例
    example_error_handling()

if __name__ == "__main__":
    main()