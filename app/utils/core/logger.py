"""
日志模块 - 提供统一的日志记录功能

功能特性：
1. 多级别日志记录（DEBUG, INFO, WARNING, ERROR, CRITICAL）
2. 文件和控制台双重输出
3. 日志文件轮转（按大小和日期）
4. 线程安全的日志记录
5. 统一的日志格式
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import os


class Logger:
    """日志管理器类"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, log_dir: Optional[str] = None, log_level: int = logging.INFO):
        """初始化日志管理器
        输入: log_dir - 日志目录路径, log_level - 日志级别
        """
        if self._initialized:
            return
            
        # 设置日志目录
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置根日志记录器
        self.logger = logging.getLogger()
        self.logger.setLevel(log_level)
        
        # 清除现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 添加文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / 'flexiv_demo.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self._initialized = True
        self.info("日志系统初始化完成")
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志记录器
        输入: name - 日志记录器名称
        输出: 配置好的日志记录器实例
        """
        return logging.getLogger(name)
    
    def debug(self, msg: str, *args, **kwargs):
        """记录DEBUG级别日志"""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """记录INFO级别日志"""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """记录WARNING级别日志"""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """记录ERROR级别日志"""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """记录CRITICAL级别日志"""
        self.logger.critical(msg, *args, **kwargs)
    
    def set_level(self, level: int):
        """设置日志级别"""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)


# 全局日志实例
logger = Logger()

# 便捷函数
def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器
    输入: name - 模块名称
    输出: 配置好的日志记录器实例
    """
    return logger.get_logger(name)

def debug(msg: str, *args, **kwargs):
    """记录DEBUG级别日志"""
    logger.debug(msg, *args, **kwargs)

def info(msg: str, *args, **kwargs):
    """记录INFO级别日志"""
    logger.info(msg, *args, **kwargs)

def warning(msg: str, *args, **kwargs):
    """记录WARNING级别日志"""
    logger.warning(msg, *args, **kwargs)

def error(msg: str, *args, **kwargs):
    """记录ERROR级别日志"""
    logger.error(msg, *args, **kwargs)

def critical(msg: str, *args, **kwargs):
    """记录CRITICAL级别日志"""
    logger.critical(msg, *args, **kwargs)