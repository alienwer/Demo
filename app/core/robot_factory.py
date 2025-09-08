"""
机器人控制工厂 - 根据配置创建合适的机器人控制实例
"""

import logging
from typing import Optional, Type, Dict, Any

from .base_control import BaseRobotControl
from .hardware_control import HardwareRobotControl
from .simulator_control import SimulatorRobotControl
from ...config.settings import ROBOT_CONFIG


class RobotControlFactory:
    """机器人控制工厂类"""
    
    _instance = None
    _logger = logging.getLogger(__name__)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def create_robot_control(cls, 
                            robot_type: Optional[str] = None,
                            robot_id: Optional[str] = None,
                            **kwargs) -> BaseRobotControl:
        """创建机器人控制实例
        输入: robot_type - 机器人类型, robot_id - 机器人ID, kwargs - 其他参数
        输出: 机器人控制实例
        """
        # 获取配置
        config = ROBOT_CONFIG
        
        # 确定机器人类型
        if robot_type is None:
            robot_type = config.get('robot_type', 'simulator')
        
        # 确定机器人ID
        if robot_id is None:
            robot_id = config.get('robot_id', 'Rizon4-062468')
        
        cls._logger.info(f"创建机器人控制实例 - 类型: {robot_type}, ID: {robot_id}")
        
        # 根据类型创建相应的控制实例
        if robot_type.lower() == 'hardware':
            return cls._create_hardware_control(robot_id, **kwargs)
        elif robot_type.lower() == 'simulator':
            return cls._create_simulator_control(robot_id, **kwargs)
        else:
            cls._logger.warning(f"未知的机器人类型: {robot_type}, 使用模拟器模式")
            return cls._create_simulator_control(robot_id, **kwargs)
    
    @classmethod
    def _create_hardware_control(cls, robot_id: str, **kwargs) -> HardwareRobotControl:
        """创建硬件机器人控制实例
        输入: robot_id - 机器人ID, kwargs - 其他参数
        输出: 硬件机器人控制实例
        """
        try:
            # 检查Flexiv RDK是否可用
            import importlib
            spec = importlib.util.find_spec('flexivrdk')
            if spec is None:
                cls._logger.warning("Flexiv RDK未安装，无法创建硬件控制实例")
                return cls._create_simulator_control(robot_id, **kwargs)
            
            # 创建硬件控制实例
            control = HardwareRobotControl(robot_id)
            cls._logger.info("硬件机器人控制实例创建成功")
            return control
            
        except ImportError as e:
            cls._logger.error(f"Flexiv RDK导入失败: {e}")
            return cls._create_simulator_control(robot_id, **kwargs)
        except Exception as e:
            cls._logger.error(f"创建硬件控制实例失败: {e}")
            return cls._create_simulator_control(robot_id, **kwargs)
    
    @classmethod
    def _create_simulator_control(cls, robot_id: str, **kwargs) -> SimulatorRobotControl:
        """创建模拟器机器人控制实例
        输入: robot_id - 机器人ID, kwargs - 其他参数
        输出: 模拟器机器人控制实例
        """
        try:
            control = SimulatorRobotControl(robot_id)
            cls._logger.info("模拟器机器人控制实例创建成功")
            return control
        except Exception as e:
            cls._logger.error(f"创建模拟器控制实例失败: {e}")
            raise
    
    @classmethod
    def get_available_robot_types(cls) -> Dict[str, str]:
        """获取可用的机器人类型
        输出: 机器人类型字典
        """
        types = {
            'simulator': '模拟器模式 - 无硬件依赖',
            'hardware': '硬件模式 - 需要Flexiv RDK和真实机器人'
        }
        
        # 检查硬件模式是否可用
        try:
            import importlib
            spec = importlib.util.find_spec('flexivrdk')
            if spec is None:
                types['hardware'] += ' (未安装)'
        except:
            types['hardware'] += ' (不可用)'
        
        return types
    
    @classmethod
    def validate_robot_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证机器人配置
        输入: config - 配置字典
        输出: 验证后的配置字典
        """
        validated_config = config.copy()
        
        # 验证机器人类型
        robot_type = config.get('robot_type', 'simulator')
        if robot_type not in ['simulator', 'hardware']:
            cls._logger.warning(f"无效的机器人类型: {robot_type}, 使用默认值: simulator")
            validated_config['robot_type'] = 'simulator'
        
        # 验证机器人ID
        robot_id = config.get('robot_id', '')
        if not robot_id:
            validated_config['robot_id'] = 'Rizon4-062468' if robot_type == 'hardware' else 'Simulator-Rizon4'
        
        # 验证网络配置
        network_config = config.get('network', {})
        if not isinstance(network_config, dict):
            validated_config['network'] = {}
        
        # 设置默认网络配置
        default_network = {
            'robot_ip': '192.168.2.100',
            'local_ip': '192.168.2.200',
            'timeout': 5.0,
            'retry_attempts': 3
        }
        
        for key, default_value in default_network.items():
            if key not in validated_config.get('network', {}):
                validated_config.setdefault('network', {})[key] = default_value
        
        return validated_config
    
    @classmethod
    def create_from_config(cls, config: Optional[Dict[str, Any]] = None) -> BaseRobotControl:
        """根据配置创建机器人控制实例
        输入: config - 配置字典
        输出: 机器人控制实例
        """
        if config is None:
            config = ROBOT_CONFIG
        
        # 验证配置
        validated_config = cls.validate_robot_config(config)
        
        # 创建控制实例
        robot_type = validated_config.get('robot_type', 'simulator')
        robot_id = validated_config.get('robot_id', 
                                      'Rizon4-062468' if robot_type == 'hardware' else 'Simulator-Rizon4')
        
        return cls.create_robot_control(robot_type, robot_id)


def create_robot_control(robot_type: Optional[str] = None, 
                        robot_id: Optional[str] = None,
                        **kwargs) -> BaseRobotControl:
    """创建机器人控制实例的便捷函数
    输入: robot_type - 机器人类型, robot_id - 机器人ID, kwargs - 其他参数
    输出: 机器人控制实例
    """
    return RobotControlFactory.create_robot_control(robot_type, robot_id, **kwargs)


def create_from_config(config: Optional[Dict[str, Any]] = None) -> BaseRobotControl:
    """根据配置创建机器人控制实例的便捷函数
    输入: config - 配置字典
    输出: 机器人控制实例
    """
    return RobotControlFactory.create_from_config(config)