#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细的URDF同步测试

用于深入测试SyncURDF功能和文件生成机制

Author: LK
Date: 2025-01-XX
"""

import os
import sys
import time
import shutil

def test_sync_urdf_with_monitoring():
    """
    监控URDF同步过程中的文件变化
    """
    print("=== 详细URDF同步测试 ===")
    
    # 读取机器人序列号
    try:
        with open('.robot_sn', 'r') as f:
            robot_sn = f.read().strip()
        print(f"机器人序列号: {robot_sn}")
    except:
        print("❌ 无法读取机器人序列号")
        return False
    
    # 检查URDF目录
    urdf_dir = os.path.join(os.getcwd(), 'resources', 'urdf')
    print(f"URDF目录: {urdf_dir}")
    
    # 记录同步前的文件状态
    print("\n=== 同步前文件状态 ===")
    before_files = set()
    if os.path.exists(urdf_dir):
        before_files = set(os.listdir(urdf_dir))
        print(f"现有文件: {sorted(before_files)}")
    else:
        print("❌ URDF目录不存在")
        return False
    
    # 选择模板文件
    template_files = [f for f in before_files if f.endswith('.urdf') and 'calibrated' not in f]
    if not template_files:
        print("❌ 未找到模板URDF文件")
        return False
    
    # 根据机器人型号选择合适的模板
    if 'rizon10' in robot_sn.lower():
        preferred_template = 'flexiv_rizon10_kinematics.urdf'
        if preferred_template not in template_files:
            preferred_template = 'flexiv_rizon10s_kinematics.urdf'
    else:
        preferred_template = 'flexiv_rizon4s_kinematics.urdf'
        if preferred_template not in template_files:
            preferred_template = 'flexiv_rizon4_kinematics.urdf'
    
    if preferred_template not in template_files:
        preferred_template = template_files[0]
    
    template_path = os.path.join(urdf_dir, preferred_template)
    print(f"选择的模板文件: {preferred_template}")
    
    # 连接机器人并执行同步
    try:
        from flexivrdk import Robot, Model
        
        print("\n=== 连接机器人 ===")
        robot = Robot(robot_sn)
        
        if not robot.connected():
            print("❌ 机器人未连接")
            return False
        
        print("✓ 机器人已连接")
        
        print("\n=== 初始化Model ===")
        model = Model(robot)
        print("✓ Model初始化成功")
        
        print("\n=== 执行URDF同步 ===")
        print(f"调用: model.SyncURDF('{template_path}')")
        
        # 执行同步
        start_time = time.time()
        model.SyncURDF(template_path)
        end_time = time.time()
        
        print(f"✓ SyncURDF调用完成，耗时: {end_time - start_time:.2f}秒")
        
        # 等待文件生成
        print("\n=== 监控文件变化 ===")
        for i in range(10):  # 等待最多10秒
            time.sleep(1)
            current_files = set(os.listdir(urdf_dir))
            new_files = current_files - before_files
            
            if new_files:
                print(f"✓ 发现新文件: {sorted(new_files)}")
                break
            else:
                print(f"等待文件生成... ({i+1}/10)")
        
        # 最终文件状态
        print("\n=== 同步后文件状态 ===")
        after_files = set(os.listdir(urdf_dir))
        new_files = after_files - before_files
        
        if new_files:
            print(f"✓ 新生成的文件: {sorted(new_files)}")
            
            # 检查新文件内容
            for new_file in new_files:
                file_path = os.path.join(urdf_dir, new_file)
                file_size = os.path.getsize(file_path)
                print(f"  - {new_file}: {file_size} bytes")
                
                # 读取文件前几行
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_lines = [f.readline().strip() for _ in range(3)]
                    print(f"    前3行: {first_lines}")
                except Exception as e:
                    print(f"    读取失败: {str(e)}")
            
            return True
        else:
            print("❌ 未生成新文件")
            
            # 检查是否有文件被修改
            print("\n=== 检查文件修改时间 ===")
            for file_name in before_files:
                if file_name.endswith('.urdf'):
                    file_path = os.path.join(urdf_dir, file_name)
                    mtime = os.path.getmtime(file_path)
                    if mtime > start_time:
                        print(f"✓ 文件已更新: {file_name}")
                        return True
            
            print("❌ 没有文件被修改或生成")
            return False
            
    except Exception as e:
        print(f"❌ 同步测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_urdf_sync_api_usage():
    """
    检查SyncURDF API的正确使用方法
    """
    print("\n=== 检查SyncURDF API使用 ===")
    
    try:
        from flexivrdk import Model
        
        # 检查Model类的方法
        model_methods = [method for method in dir(Model) if not method.startswith('_')]
        print(f"Model类可用方法: {model_methods}")
        
        # 检查SyncURDF方法签名
        if hasattr(Model, 'SyncURDF'):
            import inspect
            sig = inspect.signature(Model.SyncURDF)
            print(f"SyncURDF方法签名: {sig}")
        else:
            print("❌ Model类没有SyncURDF方法")
            
    except Exception as e:
        print(f"❌ API检查失败: {str(e)}")

def test_alternative_sync_methods():
    """
    测试其他可能的同步方法
    """
    print("\n=== 测试其他同步方法 ===")
    
    try:
        # 读取机器人序列号
        with open('.robot_sn', 'r') as f:
            robot_sn = f.read().strip()
        
        from flexivrdk import Robot, Model
        robot = Robot(robot_sn)
        
        if not robot.connected():
            print("❌ 机器人未连接")
            return
        
        model = Model(robot)
        
        # 检查Model类的其他方法
        model_methods = [method for method in dir(model) if not method.startswith('_') and callable(getattr(model, method))]
        print(f"Model实例可用方法: {model_methods}")
        
        # 尝试其他可能的URDF相关方法
        urdf_methods = [method for method in model_methods if 'urdf' in method.lower() or 'sync' in method.lower()]
        print(f"URDF相关方法: {urdf_methods}")
        
    except Exception as e:
        print(f"❌ 其他方法测试失败: {str(e)}")

def main():
    """
    主测试流程
    """
    print("详细URDF同步测试工具")
    print("=" * 60)
    
    # 检查API使用
    check_urdf_sync_api_usage()
    
    # 测试其他方法
    test_alternative_sync_methods()
    
    # 执行详细同步测试
    success = test_sync_urdf_with_monitoring()
    
    print("\n" + "=" * 60)
    print(f"测试结果: {'✓ 成功' if success else '❌ 失败'}")
    
    if not success:
        print("\n可能的原因:")
        print("1. SyncURDF可能不会生成新文件，而是修改现有文件")
        print("2. 标定后的URDF可能保存在其他位置")
        print("3. 需要特定的机器人状态或模式")
        print("4. API使用方法可能不正确")
        print("5. 权限问题导致文件无法写入")

if __name__ == "__main__":
    main()