#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URDF同步问题诊断脚本

用于诊断已连接机器人但URDF同步失败的问题

Author: LK
Date: 2025-01-XX
"""

import os
import sys
import time

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.control.robot_control import RobotControl

def check_flexiv_rdk():
    """
    检查Flexiv RDK是否可用
    """
    print("=== 检查Flexiv RDK ===")    
    try:
        import flexivrdk
        print(f"✓ Flexiv RDK已安装，版本: {flexivrdk.__version__ if hasattr(flexivrdk, '__version__') else '未知'}")
        
        # 检查关键类是否可用
        from flexivrdk import Robot, Model
        print("✓ Robot和Model类导入成功")
        return True
    except ImportError as e:
        print(f"❌ Flexiv RDK导入失败: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Flexiv RDK检查异常: {str(e)}")
        return False

def check_robot_connection(robot_sn: str):
    """
    检查机器人连接状态
    """
    print(f"\n=== 检查机器人连接: {robot_sn} ===")
    
    try:
        from flexivrdk import Robot
        robot = Robot(robot_sn)
        
        # 检查连接状态
        print(f"机器人连接状态: {robot.connected()}")
        
        if robot.connected():
            print(f"机器人使能状态: {robot.operational()}")
            print(f"机器人故障状态: {robot.fault()}")
            print(f"机器人模式: {robot.mode()}")
            
            # 获取机器人状态
            try:
                states = robot.states()
                print(f"关节角度: {list(states.q)[:3]}... (前3个关节)")
                print("✓ 机器人状态获取成功")
            except Exception as e:
                print(f"⚠️  获取机器人状态失败: {str(e)}")
            
            return robot
        else:
            print("❌ 机器人未连接")
            return None
            
    except Exception as e:
        print(f"❌ 机器人连接检查失败: {str(e)}")
        return None

def check_model_initialization(robot):
    """
    检查Model实例初始化
    """
    print("\n=== 检查Model实例初始化 ===")
    
    if robot is None:
        print("❌ Robot实例为空，无法初始化Model")
        return None
    
    try:
        from flexivrdk import Model
        model = Model(robot)
        print("✓ Model实例初始化成功")
        return model
    except Exception as e:
        print(f"❌ Model实例初始化失败: {str(e)}")
        return None

def check_urdf_files():
    """
    检查URDF文件状态
    """
    print("\n=== 检查URDF文件 ===")
    
    project_root = os.path.dirname(__file__)
    urdf_dir = os.path.join(project_root, 'resources', 'urdf')
    
    print(f"URDF目录: {urdf_dir}")
    
    if not os.path.exists(urdf_dir):
        print(f"❌ URDF目录不存在: {urdf_dir}")
        return []
    
    # 列出所有URDF文件
    urdf_files = [f for f in os.listdir(urdf_dir) if f.endswith('.urdf')]
    print(f"找到的URDF文件: {urdf_files}")
    
    # 检查模板文件
    template_files = [f for f in urdf_files if 'calibrated' not in f]
    calibrated_files = [f for f in urdf_files if 'calibrated' in f]
    
    print(f"模板URDF文件: {template_files}")
    print(f"标定后URDF文件: {calibrated_files}")
    
    return urdf_files

def test_urdf_sync_direct(robot, model, template_urdf_path):
    """
    直接测试URDF同步功能
    """
    print(f"\n=== 直接测试URDF同步: {os.path.basename(template_urdf_path)} ===")
    
    if not os.path.exists(template_urdf_path):
        print(f"❌ 模板文件不存在: {template_urdf_path}")
        return False
    
    try:
        print("开始调用model.SyncURDF()...")
        model.SyncURDF(template_urdf_path)
        print("✓ SyncURDF调用成功")
        
        # 检查是否生成了标定后的文件
        time.sleep(1)  # 等待文件生成
        
        urdf_dir = os.path.dirname(template_urdf_path)
        calibrated_files = [f for f in os.listdir(urdf_dir) if f.endswith('.urdf') and 'calibrated' in f]
        
        if calibrated_files:
            print(f"✓ 找到标定后文件: {calibrated_files}")
            return True
        else:
            print("⚠️  SyncURDF调用成功但未找到标定后文件")
            return False
            
    except Exception as e:
        print(f"❌ SyncURDF调用失败: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        return False

def test_robot_control_sync(robot_sn: str):
    """
    测试RobotControl类的sync_urdf方法
    """
    print(f"\n=== 测试RobotControl.sync_urdf(): {robot_sn} ===")
    
    try:
        # 创建RobotControl实例
        robot_control = RobotControl(robot_id=robot_sn, hardware=True)
        
        # 启动控制线程
        robot_control.start()
        time.sleep(3)  # 等待初始化完成
        
        # 检查robot和model实例
        print(f"Robot实例: {robot_control.robot is not None}")
        print(f"Model实例: {robot_control.model is not None}")
        
        if robot_control.robot:
            print(f"Robot连接状态: {robot_control.robot.connected()}")
        
        # 尝试同步URDF
        print("调用robot_control.sync_urdf()...")
        result = robot_control.sync_urdf()
        print(f"同步结果: {result}")
        
        # 停止控制线程
        robot_control.stop_robot()
        
        return result
        
    except Exception as e:
        print(f"❌ RobotControl测试失败: {str(e)}")
        return False

def main():
    """
    主诊断流程
    """
    print("URDF同步问题诊断工具")
    print("=" * 50)
    
    # 配置 - 从.robot_sn文件读取实际序列号
    try:
        with open('.robot_sn', 'r') as f:
            ROBOT_SN = f.read().strip()
        print(f"从.robot_sn文件读取到机器人序列号: {ROBOT_SN}")
    except:
        ROBOT_SN = "Rizon4-062468"  # 备用序列号
        print(f"使用默认机器人序列号: {ROBOT_SN}")
    
    # 步骤1: 检查Flexiv RDK
    if not check_flexiv_rdk():
        print("\n❌ Flexiv RDK不可用，请检查安装")
        return
    
    # 步骤2: 检查URDF文件
    urdf_files = check_urdf_files()
    if not urdf_files:
        print("\n❌ 未找到URDF文件")
        return
    
    # 步骤3: 检查机器人连接
    robot = check_robot_connection(ROBOT_SN)
    if robot is None:
        print("\n❌ 机器人连接失败")
        return
    
    # 步骤4: 检查Model初始化
    model = check_model_initialization(robot)
    if model is None:
        print("\n❌ Model初始化失败")
        return
    
    # 步骤5: 直接测试URDF同步
    project_root = os.path.dirname(__file__)
    template_urdf = os.path.join(project_root, 'resources', 'urdf', 'flexiv_rizon4s_kinematics.urdf')
    
    if os.path.exists(template_urdf):
        sync_success = test_urdf_sync_direct(robot, model, template_urdf)
        if not sync_success:
            print("\n❌ 直接URDF同步失败")
    else:
        print(f"\n⚠️  模板文件不存在: {template_urdf}")
    
    # 步骤6: 测试RobotControl类
    print("\n" + "=" * 50)
    control_success = test_robot_control_sync(ROBOT_SN)
    
    # 总结
    print("\n" + "=" * 50)
    print("诊断总结:")
    print(f"- Flexiv RDK: ✓")
    print(f"- URDF文件: ✓ ({len(urdf_files)}个文件)")
    print(f"- 机器人连接: {'✓' if robot else '❌'}")
    print(f"- Model初始化: {'✓' if model else '❌'}")
    print(f"- 直接URDF同步: {'✓' if 'sync_success' in locals() and sync_success else '❌'}")
    print(f"- RobotControl同步: {'✓' if control_success else '❌'}")
    
    if robot and model and not ('sync_success' in locals() and sync_success):
        print("\n🔍 建议检查项:")
        print("1. 机器人是否处于正确的模式")
        print("2. 网络连接是否稳定")
        print("3. 文件权限是否正确")
        print("4. Flexiv RDK版本是否兼容")
        print("5. 机器人固件版本是否支持URDF同步")

if __name__ == "__main__":
    main()