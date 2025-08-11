#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终URDF同步功能测试脚本
用于验证修复后的URDF同步功能是否正常工作

作者: Assistant
日期: 2024
"""

import os
import sys
import time
from datetime import datetime

def test_urdf_sync_final():
    """最终URDF同步功能测试"""
    print("=" * 60)
    print("最终URDF同步功能测试")
    print("=" * 60)
    
    # 1. 检查环境
    print("\n1. 环境检查:")
    try:
        from flexivrdk import Robot, Model
        print("✓ Flexiv RDK导入成功")
    except ImportError as e:
        print(f"✗ Flexiv RDK导入失败: {e}")
        return False
    
    # 2. 读取机器人序列号
    print("\n2. 机器人配置:")
    try:
        with open('.robot_sn', 'r') as f:
            robot_sn = f.read().strip()
        print(f"✓ 机器人序列号: {robot_sn}")
    except FileNotFoundError:
        robot_sn = "Rizon10-062357"  # 备用序列号
        print(f"⚠ 使用备用序列号: {robot_sn}")
    
    # 3. 检查URDF目录
    print("\n3. URDF文件检查:")
    project_root = os.path.dirname(os.path.abspath(__file__))
    urdf_dir = os.path.join(project_root, 'resources', 'urdf')
    
    if not os.path.exists(urdf_dir):
        print(f"✗ URDF目录不存在: {urdf_dir}")
        return False
    
    urdf_files = [f for f in os.listdir(urdf_dir) if f.endswith('.urdf')]
    print(f"✓ URDF目录: {urdf_dir}")
    print(f"✓ 找到URDF文件: {urdf_files}")
    
    # 4. 测试RobotControl类的sync_urdf方法
    print("\n4. RobotControl URDF同步测试:")
    try:
        # 导入RobotControl类
        sys.path.append(os.path.join(project_root, 'app'))
        from control.robot_control import RobotControl
        
        print("✓ RobotControl类导入成功")
        
        # 创建RobotControl实例（硬件模式）
        robot_control = RobotControl(robot_id=robot_sn, hardware=True)
        print("✓ RobotControl实例创建成功")
        
        # 等待连接建立
        print("正在等待机器人连接...")
        time.sleep(2)
        
        # 检查连接状态
        if hasattr(robot_control, 'robot') and robot_control.robot:
            if robot_control.robot.connected():
                print("✓ 机器人连接成功")
                
                # 记录同步前的文件状态
                print("\n记录同步前文件状态:")
                file_states_before = {}
                for filename in urdf_files:
                    filepath = os.path.join(urdf_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    file_states_before[filename] = mtime
                    print(f"  {filename}: {datetime.fromtimestamp(mtime)}")
                
                # 执行URDF同步
                print("\n执行URDF同步...")
                success = robot_control.sync_urdf()
                
                if success:
                    print("✓ URDF同步成功")
                    
                    # 检查同步后的文件状态
                    print("\n检查同步后文件状态:")
                    file_states_after = {}
                    updated_files = []
                    
                    for filename in urdf_files:
                        filepath = os.path.join(urdf_dir, filename)
                        mtime = os.path.getmtime(filepath)
                        file_states_after[filename] = mtime
                        
                        if mtime > file_states_before[filename]:
                            updated_files.append(filename)
                            print(f"  ✓ {filename}: 已更新 ({datetime.fromtimestamp(mtime)})")
                        else:
                            print(f"  - {filename}: 未变化 ({datetime.fromtimestamp(mtime)})")
                    
                    # 检查last_synced_urdf_path属性
                    if hasattr(robot_control, 'last_synced_urdf_path'):
                        synced_path = robot_control.last_synced_urdf_path
                        print(f"\n✓ 同步文件路径已记录: {synced_path}")
                        
                        if os.path.exists(synced_path):
                            print(f"✓ 同步文件存在: {os.path.basename(synced_path)}")
                        else:
                            print(f"✗ 同步文件不存在: {synced_path}")
                    else:
                        print("\n⚠ 未找到last_synced_urdf_path属性")
                    
                    # 总结
                    print(f"\n同步结果总结:")
                    print(f"  - 更新的文件数量: {len(updated_files)}")
                    if updated_files:
                        print(f"  - 更新的文件: {updated_files}")
                    print(f"  - 同步状态: 成功")
                    
                    return True
                else:
                    print("✗ URDF同步失败")
                    return False
            else:
                print("✗ 机器人连接失败")
                return False
        else:
            print("✗ 机器人实例创建失败")
            return False
            
    except Exception as e:
        print(f"✗ RobotControl测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    try:
        success = test_urdf_sync_final()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 URDF同步功能测试通过！")
            print("\n修复要点:")
            print("1. ✓ 修正了Robot API调用方法（Enable/Brake/ClearFault）")
            print("2. ✓ 修改了主程序逻辑，支持直接修改模板文件的同步方式")
            print("3. ✓ 添加了last_synced_urdf_path属性记录同步文件路径")
            print("4. ✓ 改进了文件查找逻辑，按修改时间排序")
            print("\n现在可以正常使用URDF同步功能了！")
        else:
            print("❌ URDF同步功能测试失败")
            print("\n请检查:")
            print("1. 机器人是否正确连接")
            print("2. 机器人是否处于远程模式")
            print("3. 网络连接是否正常")
            print("4. RDK版本是否兼容")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()