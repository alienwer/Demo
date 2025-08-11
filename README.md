# Flexiv Robot Demo

## 项目简介
本项目为Flexiv机器人控制与仿真演示平台，支持真实机器人与仿真两种模式，集成3D可视化、URDF解析、串口通信、教学与轨迹等功能。

## 目录结构
```
app/                # 所有Python源代码
  main.py           # 主入口
  control/          # 控制与通信模块
  model/            # 机器人模型与数据
  visualization/    # 3D渲染与URDF解析
  ui/               # UI文件
resources/          # 机器人URDF、网格、配置
  urdf/             # URDF模型（已标定，可直接使用）
  meshes/           # 网格模型
  config/           # RViz等配置
archive/            # 测试文件和文档归档（可安全删除）
launch/             # ROS仿真启动文件
docs/               # 说明文档、API手册
requirements.txt    # 依赖声明
package.xml         # ROS包声明
```

## 快速启动
```bash
pip install -r requirements.txt
python3 app/main.py [--sim|--hardware]
```
- `--sim`：仿真/教学模式（无硬件）
- `--hardware`：真实机器人模式（需flexivrdk）

## 主要功能
- 支持Flexiv机器人控制与仿真
- 3D可视化与交互（旋转、缩放、平移、阴影、预设视角）
- URDF模型与网格解析
- URDF同步功能（硬件模式下可同步机器人实际运动学参数）
- 串口通信与状态监控
- 教学点与轨迹生成功能
- ROS仿真与RViz支持

## 测试与类型检查
```bash
mypy app/           # 类型检查
pytest              # 自动化测试
```

## 文档生成
```bash
cd docs_sphinx
make html           # 生成API文档
```

## 贡献与开发规范
- 代码需PEP8风格，注释与类型提示规范
- 所有新功能需配套测试用例
- 详细文档与用法示例见 docs/ docs_sphinx/

---
Flexiv Robotics Team