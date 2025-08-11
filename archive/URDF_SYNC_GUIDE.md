# URDF同步功能使用指南

## 概述

URDF同步功能允许将连接的Flexiv机器人的实际运动学参数同步到模板URDF文件中，生成标定后的URDF文件，确保仿真模型与实际机器人的运动学参数完全一致。

## 功能原理

### 1. 同步过程
- **模板URDF**: 使用`resources/urdf/`目录中的标准URDF文件作为模板
- **实际参数获取**: 通过Flexiv RDK从连接的机器人获取实际运动学参数
- **标定文件生成**: 在同一目录下生成带`_calibrated`后缀的标定URDF文件
- **模型更新**: 自动重新加载标定后的URDF文件到3D可视化系统

### 2. 支持的机器人型号
- Flexiv Rizon 4
- Flexiv Rizon 4s  
- Flexiv Rizon 10
- Flexiv Rizon 10s

## 使用步骤

### 前提条件
1. **硬件连接**: 确保机器人已正确连接到网络
2. **软件环境**: 确保已安装Flexiv RDK (>=1.6.0)
3. **运行模式**: 必须在硬件模式下运行（非仿真模式）
4. **机器人状态**: 机器人必须已连接并使能

### 操作步骤

#### 1. 连接机器人
```
1. 在主界面输入正确的机器人序列号
2. 点击"连接"按钮
3. 等待连接成功（状态灯变绿）
4. 确保机器人已使能
```

#### 2. 执行URDF同步
```
1. 在"机器人操作"区域找到"URDF同步"按钮
2. 点击"URDF同步"按钮
3. 观察状态信息，等待同步完成
4. 检查是否生成了标定后的URDF文件
```

#### 3. 验证同步结果
```
1. 检查resources/urdf/目录是否生成了*_calibrated.urdf文件
2. 观察3D可视化是否已更新为标定后的模型
3. 验证机器人运动是否与可视化同步
```

## 故障排除

### 常见错误及解决方案

#### 1. "机器人控制器未初始化，请先连接机器人"
**原因**: 未连接机器人或连接失败
**解决方案**:
- 检查机器人序列号是否正确
- 确保机器人已开机并连接到网络
- 重新尝试连接

#### 2. "仿真模式下无法同步URDF"
**原因**: 当前运行在仿真模式下
**解决方案**:
- 确保在启动应用时选择了硬件模式
- 重新启动应用并选择硬件模式

#### 3. "Model实例未初始化，无法同步URDF"
**原因**: Flexiv RDK的Model实例未正确初始化
**解决方案**:
- 确保机器人已连接并使能
- 等待机器人控制线程完全启动
- 检查Flexiv RDK是否正确安装

#### 4. "Robot实例未初始化或Flexiv RDK不可用"
**原因**: Robot实例创建失败或RDK库问题
**解决方案**:
- 检查Flexiv RDK安装是否完整
- 确认机器人序列号格式正确
- 检查网络连接和防火墙设置

#### 5. "未找到模板URDF文件"
**原因**: resources/urdf目录中缺少对应的URDF模板文件
**解决方案**:
- 检查resources/urdf/目录是否存在
- 确认目录中有对应机器人型号的URDF文件
- 检查文件权限是否正确

#### 6. "标定URDF文件未找到"
**原因**: 同步过程中未成功生成标定文件
**解决方案**:
- 检查同步过程是否有错误信息
- 确认有写入权限到resources/urdf/目录
- 重新尝试同步操作

### 调试工具

#### 运行测试脚本
```bash
# 激活conda环境
conda activate demo-env

# 运行URDF同步测试
python test_urdf_sync.py
```

测试脚本会检查:
- URDF模板文件是否存在
- RobotControl类是否能正确初始化
- 同步逻辑是否正常
- 提供详细的故障排除建议

## 技术细节

### 文件结构
```
resources/urdf/
├── flexiv_rizon4s_kinematics.urdf          # 模板文件
├── flexiv_rizon4s_kinematics_calibrated.urdf  # 标定后文件（同步生成）
├── flexiv_rizon4_kinematics.urdf
├── flexiv_rizon10s_kinematics.urdf
└── flexiv_rizon10_kinematics.urdf
```

### 代码实现要点

#### 1. Model实例管理
```python
# 在RobotControl.sync_urdf()中
if self.model is None:
    # 动态初始化Model实例
    self.model = Model(self.robot)
```

#### 2. 路径查找逻辑
```python
# 自动查找模板URDF文件
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
possible_paths = [
    os.path.join(project_root, 'resources', 'urdf', 'flexiv_rizon4s_kinematics.urdf'),
    # ... 其他路径
]
```

#### 3. 标定文件处理
```python
# 查找标定后的URDF文件
calibrated_files = [
    'flexiv_rizon4s_kinematics_calibrated.urdf',
    # ... 其他标定文件名
]
```

### API调用

#### Flexiv RDK SyncURDF方法
```python
# 调用Flexiv RDK的同步方法
self.model.SyncURDF(template_urdf_path)
```

该方法会:
1. 读取模板URDF文件
2. 获取机器人实际运动学参数
3. 更新URDF中的运动学参数
4. 在同一目录生成标定后的URDF文件

## 最佳实践

### 1. 同步时机
- **首次连接**: 每次连接新机器人时建议执行同步
- **定期校准**: 定期执行同步以确保精度
- **硬件更换**: 更换机器人硬件后必须重新同步

### 2. 文件管理
- **备份原文件**: 同步前备份原始URDF文件
- **版本控制**: 将标定后的URDF文件纳入版本控制
- **文档记录**: 记录同步时间和机器人状态

### 3. 验证方法
- **运动对比**: 对比实际机器人运动与仿真运动
- **精度测试**: 执行精度测试验证同步效果
- **多点验证**: 在不同关节位置验证同步精度

## 注意事项

1. **安全第一**: 同步过程中确保机器人处于安全状态
2. **网络稳定**: 确保网络连接稳定，避免同步中断
3. **权限检查**: 确保有足够权限写入URDF目录
4. **版本兼容**: 确保Flexiv RDK版本与机器人固件兼容
5. **备份重要**: 同步前备份重要的配置文件

## 支持与反馈

如果在使用过程中遇到问题:
1. 首先运行测试脚本进行基础检查
2. 查看应用日志获取详细错误信息
3. 参考本文档的故障排除部分
4. 联系技术支持获取进一步帮助

---

**更新日期**: 2025-01-XX  
**版本**: 1.0  
**适用于**: Flexiv RDK >= 1.6.0