# 机器人配置
ROBOT_CONFIG = {
    "default_robot_id": "Rizon4-062468",
    "default_ip": "192.168.2.100",
    "default_port": 8080,
    "joint_limits": {
        "min": [-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973],
        "max": [2.8973, 1.7628, 2.8973, -0.0698, 2.8973, 3.7525, 2.8973]
    },
    "velocity_limits": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    "acceleration_limits": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    "simulation": {
        "enabled": True,
        "update_rate": 100  # Hz
    }
}