"""
配置管理器模块
提供统一的配置管理接口，支持配置的加载、保存、验证和热重载
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from ...config.settings import ROBOT_CONFIG
from ...config.constants import RobotState, GripperState, MotionPrimitive


@dataclass
class AppConfig:
    """应用程序配置数据类"""
    robot_type: str = "simulator"  # 机器人类型: simulator/hardware
    robot_id: str = "Simulator-Rizon4"  # 机器人ID
    update_rate: int = 100  # 状态更新频率(Hz)
    log_level: str = "INFO"  # 日志级别
    auto_connect: bool = True  # 是否自动连接
    simulation_enabled: bool = True  # 是否启用仿真
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """从字典创建配置"""
        return cls(**data)


class ConfigManager:
    """配置管理器类"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._logger = logging.getLogger(__name__)
            self._config_dir = Path.home() / ".flexiv_demo"
            self._config_file = self._config_dir / "config.json"
            self._app_config = AppConfig()
            self._robot_config = ROBOT_CONFIG
            self._initialized = True
            self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._app_config = AppConfig.from_dict(config_data)
                self._logger.info("配置文件加载成功")
            else:
                self._save_config()  # 创建默认配置文件
                self._logger.info("创建默认配置文件")
        except Exception as e:
            self._logger.error(f"加载配置文件失败: {e}")
    
    def _save_config(self) -> None:
        """保存配置文件"""
        try:
            self._config_dir.mkdir(exist_ok=True)
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._app_config.to_dict(), f, indent=2, ensure_ascii=False)
            self._logger.info("配置文件保存成功")
        except Exception as e:
            self._logger.error(f"保存配置文件失败: {e}")
    
    def get_app_config(self) -> AppConfig:
        """获取应用程序配置"""
        return self._app_config
    
    def get_robot_config(self) -> Dict[str, Any]:
        """获取机器人配置"""
        return self._robot_config
    
    def update_app_config(self, config: Dict[str, Any]) -> bool:
        """更新应用程序配置"""
        try:
            self._app_config = AppConfig.from_dict(config)
            self._save_config()
            return True
        except Exception as e:
            self._logger.error(f"更新配置失败: {e}")
            return False
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        config_dict = self._app_config.to_dict()
        return config_dict.get(key, default)
    
    def set_config_value(self, key: str, value: Any) -> bool:
        """设置配置值"""
        try:
            config_dict = self._app_config.to_dict()
            config_dict[key] = value
            self._app_config = AppConfig.from_dict(config_dict)
            self._save_config()
            return True
        except Exception as e:
            self._logger.error(f"设置配置值失败: {e}")
            return False


# 全局配置管理器实例
config_manager = ConfigManager()