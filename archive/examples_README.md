# URDF同步功能示例

本目录包含了URDF同步功能的使用示例和测试脚本，帮助开发者理解和集成URDF同步功能。

## 文件说明

### 1. `urdf_sync_example.py`
完整的URDF同步功能使用示例，展示了从连接机器人到加载标定后模型的完整工作流程。

**主要功能：**
- 机器人连接管理
- URDF同步执行
- 标定后URDF文件查找和加载
- 错误处理和异常管理
- 资源清理

**使用方法：**
```bash
# 激活conda环境
conda activate demo-env

# 运行完整示例（需要实际机器人）
python examples/urdf_sync_example.py

# 运行演示模式（仅显示错误处理，无需实际机器人）
python examples/urdf_sync_example.py --demo
```

### 2. `test_urdf_sync.py`
基础配置和路径验证测试脚本，用于检查URDF同步功能的基础环境配置。

**主要功能：**
- URDF模板文件路径验证
- RobotControl类初始化测试
- 基础配置检查

**使用方法：**
```bash
# 激活conda环境
conda activate demo-env

# 运行测试
python test_urdf_sync.py
```

## 使用前准备

### 1. 环境配置
```bash
# 确保已激活正确的conda环境
conda activate demo-env

# 检查必要的依赖
python -c "import flexivrdk; print('Flexiv RDK已安装')"
python -c "import numpy; print('NumPy已安装')"
```

### 2. 机器人配置
在运行硬件模式示例前，请确保：
- 机器人已正确连接到网络
- 机器人序列号正确（在示例中修改`ROBOT_SN`变量）
- 机器人处于可连接状态

### 3. 文件权限
确保对以下目录有读写权限：
- `resources/urdf/` - 用于读取模板URDF文件和写入标定后文件
- 项目根目录 - 用于创建临时文件

## 示例运行流程

### 完整工作流程
1. **连接机器人** - 建立与实际机器人的连接
2. **启动控制线程** - 初始化机器人控制和Model实例
3. **执行URDF同步** - 调用Flexiv RDK的SyncURDF API
4. **查找标定文件** - 自动查找生成的标定后URDF文件
5. **加载标定模型** - 更新机器人模型为标定后参数
6. **验证结果** - 确认同步成功并显示结果
7. **清理资源** - 安全停止机器人控制

### 错误处理示例
- 仿真模式下的同步尝试（预期失败）
- 无效文件路径处理
- 网络连接异常处理
- 机器人状态异常处理

## 常见问题排查

### 1. 连接失败
```
❌ 机器人连接失败: 无法建立与 Rizon4-XXXXXX 的连接
```
**解决方案：**
- 检查机器人序列号是否正确
- 确认机器人网络连接正常
- 验证防火墙设置
- 检查机器人是否被其他程序占用

### 2. URDF同步失败
```
❌ URDF同步失败
```
**解决方案：**
- 确认处于硬件模式
- 检查Model实例是否正确初始化
- 验证模板URDF文件路径
- 确认机器人连接状态正常

### 3. 找不到标定文件
```
❌ 未找到标定后URDF文件
```
**解决方案：**
- 确认URDF同步已成功执行
- 检查`resources/urdf/`目录权限
- 验证标定文件是否正确生成
- 查看控制台输出的详细错误信息

### 4. 模块导入错误
```
ModuleNotFoundError: No module named 'flexivrdk'
```
**解决方案：**
- 确认已激活正确的conda环境：`conda activate demo-env`
- 检查Flexiv RDK是否正确安装
- 验证Python路径配置

## 开发指南

### 集成到现有项目
1. 复制`urdf_sync_example.py`中的关键函数
2. 根据项目需求修改错误处理逻辑
3. 调整文件路径和配置参数
4. 添加项目特定的验证步骤

### 自定义配置
```python
# 自定义机器人型号和序列号
ROBOT_SN = "your-robot-serial-number"
ROBOT_TYPE = "rizon4s"  # 或 rizon4, rizon10, rizon10s

# 自定义URDF文件路径
TEMPLATE_URDF = f"resources/urdf/flexiv_{ROBOT_TYPE}_kinematics.urdf"
CALIBRATED_URDF = f"resources/urdf/flexiv_{ROBOT_TYPE}_kinematics_calibrated.urdf"
```

### 扩展功能
- 添加多机器人支持
- 实现批量URDF同步
- 集成到GUI应用程序
- 添加同步结果验证
- 实现自动重试机制

## 技术支持

如果在使用过程中遇到问题，请：
1. 查看控制台输出的详细错误信息
2. 运行测试脚本验证基础配置
3. 检查`URDF_SYNC_GUIDE.md`中的故障排除部分
4. 确认Flexiv RDK版本兼容性

## 相关文档

- `../URDF_SYNC_GUIDE.md` - URDF同步功能详细指南
- `../README.md` - 项目总体说明
- Flexiv RDK官方文档 - API参考手册