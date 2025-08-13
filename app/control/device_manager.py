'''
Author: LK
Date: 2025-01-XX XX:XX:XX
LastEditTime: 2025-01-XX XX:XX:XX
LastEditors: LK
FilePath: /Demo/app/control/device_manager.py
'''

import threading
import time
import json
import socket
import subprocess
from typing import Dict, Any, List, Optional, Tuple, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from dataclasses import dataclass, asdict
from enum import Enum
import ipaddress

try:
    from flexiv import Device
except ImportError:
    # 仿真模式下的模拟类
    class Device:
        def __init__(self):
            self.discovered_devices = {
                "192.168.2.100": {
                    "ip": "192.168.2.100",
                    "name": "Rizon4-001",
                    "model": "Rizon4",
                    "serial": "RZ4001234567",
                    "firmware_version": "2.8.1",
                    "hardware_version": "1.2",
                    "status": "online",
                    "last_seen": time.time(),
                    "capabilities": ["real_time_control", "primitive_execution", "force_control"],
                    "network_info": {
                        "mac_address": "00:1A:2B:3C:4D:5E",
                        "subnet_mask": "255.255.255.0",
                        "gateway": "192.168.2.1",
                        "dns": ["8.8.8.8", "8.8.4.4"]
                    }
                },
                "192.168.2.101": {
                    "ip": "192.168.2.101",
                    "name": "Rizon4-002",
                    "model": "Rizon4",
                    "serial": "RZ4001234568",
                    "firmware_version": "2.8.0",
                    "hardware_version": "1.2",
                    "status": "offline",
                    "last_seen": time.time() - 3600,
                    "capabilities": ["real_time_control", "primitive_execution"],
                    "network_info": {
                        "mac_address": "00:1A:2B:3C:4D:5F",
                        "subnet_mask": "255.255.255.0",
                        "gateway": "192.168.2.1",
                        "dns": ["8.8.8.8", "8.8.4.4"]
                    }
                }
            }
        
        def discover_devices(self, timeout: float = 5.0) -> List[Dict[str, Any]]:
            """发现设备"""
            # 模拟发现延迟
            time.sleep(min(timeout, 1.0))
            
            # 更新在线设备状态
            current_time = time.time()
            for device_info in self.discovered_devices.values():
                if current_time - device_info["last_seen"] < 300:  # 5分钟内视为在线
                    device_info["status"] = "online"
                else:
                    device_info["status"] = "offline"
            
            return list(self.discovered_devices.values())
        
        def get_device_info(self, ip: str) -> Optional[Dict[str, Any]]:
            """获取设备信息"""
            return self.discovered_devices.get(ip)
        
        def ping_device(self, ip: str) -> bool:
            """Ping设备"""
            if ip in self.discovered_devices:
                # 模拟ping延迟
                time.sleep(0.1)
                return self.discovered_devices[ip]["status"] == "online"
            return False
        
        def connect_device(self, ip: str) -> bool:
            """连接设备"""
            if ip in self.discovered_devices:
                device_info = self.discovered_devices[ip]
                if device_info["status"] == "online":
                    device_info["last_seen"] = time.time()
                    return True
            return False
        
        def disconnect_device(self, ip: str) -> bool:
            """断开设备连接"""
            return ip in self.discovered_devices
        
        def get_device_status(self, ip: str) -> Optional[str]:
            """获取设备状态"""
            device_info = self.discovered_devices.get(ip)
            return device_info["status"] if device_info else None
        
        def update_device_config(self, ip: str, config: Dict[str, Any]) -> bool:
            """更新设备配置"""
            if ip in self.discovered_devices:
                # 模拟配置更新
                return True
            return False
        
        def get_device_config(self, ip: str) -> Optional[Dict[str, Any]]:
            """获取设备配置"""
            if ip in self.discovered_devices:
                return {
                    "network": self.discovered_devices[ip]["network_info"],
                    "control_mode": "position",
                    "safety_limits": {
                        "max_velocity": 2.0,
                        "max_acceleration": 5.0,
                        "max_jerk": 20.0
                    },
                    "communication": {
                        "rt_port": 8080,
                        "nrt_port": 8081,
                        "timeout": 5.0
                    }
                }
            return None
        
        def reboot_device(self, ip: str) -> bool:
            """重启设备"""
            if ip in self.discovered_devices:
                # 模拟重启过程
                device_info = self.discovered_devices[ip]
                device_info["status"] = "rebooting"
                return True
            return False
        
        def shutdown_device(self, ip: str) -> bool:
            """关闭设备"""
            if ip in self.discovered_devices:
                device_info = self.discovered_devices[ip]
                device_info["status"] = "shutdown"
                return True
            return False
        
        def get_network_interfaces(self) -> List[Dict[str, Any]]:
            """获取网络接口"""
            return [
                {
                    "name": "eth0",
                    "ip": "192.168.2.10",
                    "netmask": "255.255.255.0",
                    "gateway": "192.168.2.1",
                    "status": "up"
                },
                {
                    "name": "wlan0",
                    "ip": "192.168.1.100",
                    "netmask": "255.255.255.0",
                    "gateway": "192.168.1.1",
                    "status": "down"
                }
            ]
        
        def scan_network(self, network: str) -> List[str]:
            """扫描网络"""
            # 模拟网络扫描
            if network.startswith("192.168.2"):
                return ["192.168.2.100", "192.168.2.101"]
            elif network.startswith("192.168.1"):
                return ["192.168.1.100"]
            return []

class DeviceStatus(Enum):
    """设备状态"""
    UNKNOWN = "unknown"           # 未知
    OFFLINE = "offline"           # 离线
    ONLINE = "online"             # 在线
    CONNECTING = "connecting"     # 连接中
    CONNECTED = "connected"       # 已连接
    DISCONNECTING = "disconnecting"  # 断开中
    REBOOTING = "rebooting"       # 重启中
    SHUTDOWN = "shutdown"         # 已关闭
    ERROR = "error"               # 错误
    MAINTENANCE = "maintenance"   # 维护中

class DeviceType(Enum):
    """设备类型"""
    RIZON4 = "Rizon4"             # Rizon4机器人
    RIZON4S = "Rizon4s"           # Rizon4s机器人
    RIZON10 = "Rizon10"           # Rizon10机器人
    RIZON10S = "Rizon10s"         # Rizon10s机器人
    UNKNOWN = "Unknown"           # 未知设备

class ConnectionType(Enum):
    """连接类型"""
    ETHERNET = "ethernet"         # 以太网
    WIFI = "wifi"                 # WiFi
    USB = "usb"                   # USB
    SERIAL = "serial"             # 串口

@dataclass
class NetworkInterface:
    """网络接口信息"""
    name: str
    ip: str
    netmask: str
    gateway: str
    mac_address: str
    status: str
    connection_type: ConnectionType
    
    def __post_init__(self):
        if isinstance(self.connection_type, str):
            self.connection_type = ConnectionType(self.connection_type)

@dataclass
class DeviceInfo:
    """设备信息"""
    ip: str
    name: str
    model: str
    serial: str
    firmware_version: str
    hardware_version: str
    status: DeviceStatus
    device_type: DeviceType
    capabilities: List[str]
    network_interfaces: List[NetworkInterface]
    last_seen: float
    ping_latency: Optional[float] = None
    connection_quality: Optional[float] = None
    
    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = DeviceStatus(self.status)
        if isinstance(self.device_type, str):
            self.device_type = DeviceType(self.device_type)
        if self.last_seen == 0.0:
            self.last_seen = time.time()
    
    @property
    def is_online(self) -> bool:
        """是否在线"""
        return self.status in [DeviceStatus.ONLINE, DeviceStatus.CONNECTED]
    
    @property
    def time_since_last_seen(self) -> float:
        """距离上次见到的时间"""
        return time.time() - self.last_seen

@dataclass
class ScanResult:
    """扫描结果"""
    network: str
    scan_time: float
    devices_found: List[str]
    scan_duration: float
    
    def __post_init__(self):
        if self.scan_time == 0.0:
            self.scan_time = time.time()

class DeviceManager(QObject):
    """设备管理器
    
    负责Flexiv机器人设备的发现、连接和管理，包括：
    - 设备自动发现
    - 网络扫描
    - 设备连接管理
    - 状态监控
    - 配置管理
    - 网络诊断
    """
    
    # 信号定义
    device_discovered = pyqtSignal(object)  # DeviceInfo
    device_status_changed = pyqtSignal(str, str)  # ip, status
    device_connected = pyqtSignal(str)  # ip
    device_disconnected = pyqtSignal(str)  # ip
    scan_started = pyqtSignal(str)  # network
    scan_completed = pyqtSignal(object)  # ScanResult
    network_status_changed = pyqtSignal(str)  # status_message
    device_error = pyqtSignal(str, str)  # ip, error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设备API
        self.device_api = Device()
        
        # 设备管理
        self.devices = {}  # ip -> DeviceInfo
        self.connected_devices = set()  # 已连接设备的IP
        self.scan_results = {}  # network -> ScanResult
        
        # 网络接口
        self.network_interfaces = []
        
        # 监控线程
        self.monitor_thread = None
        self.scan_thread = None
        self.monitor_lock = threading.Lock()
        self.stop_monitoring = threading.Event()
        
        # 定时器
        self.discovery_timer = QTimer()
        self.discovery_timer.timeout.connect(self.auto_discover_devices)
        
        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(self.ping_all_devices)
        
        # 配置
        self.auto_discovery_enabled = True
        self.auto_discovery_interval = 30.0  # 秒
        self.ping_interval = 10.0  # 秒
        self.device_timeout = 300.0  # 设备超时时间（秒）
        self.ping_timeout = 2.0  # Ping超时时间（秒）
        
        # 初始化
        self.init_device_manager()
    
    def init_device_manager(self):
        """初始化设备管理器"""
        try:
            # 获取网络接口
            self.update_network_interfaces()
            
            # 初始发现
            self.discover_devices()
            
            self.network_status_changed.emit("设备管理器已初始化")
            
        except Exception as e:
            self.network_status_changed.emit(f"设备管理器初始化失败: {str(e)}")
    
    def start_monitoring(self, discovery_interval: float = 30.0, ping_interval: float = 10.0):
        """开始监控设备"""
        self.auto_discovery_interval = discovery_interval
        self.ping_interval = ping_interval
        
        self.stop_monitoring.clear()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(
            target=self._device_monitor_loop,
            args=(1.0,),  # 监控间隔
            daemon=True
        )
        self.monitor_thread.start()
        
        # 启动定时器
        if self.auto_discovery_enabled:
            self.discovery_timer.start(int(discovery_interval * 1000))
        
        self.ping_timer.start(int(ping_interval * 1000))
        
        self.network_status_changed.emit("设备监控已启动")
    
    def stop_monitoring(self):
        """停止监控设备"""
        self.stop_monitoring.set()
        
        # 停止定时器
        self.discovery_timer.stop()
        self.ping_timer.stop()
        
        # 等待监控线程结束
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        
        self.network_status_changed.emit("设备监控已停止")
    
    def _device_monitor_loop(self, interval: float):
        """设备监控循环"""
        while not self.stop_monitoring.is_set():
            try:
                with self.monitor_lock:
                    # 检查设备超时
                    self.check_device_timeouts()
                    
                    # 更新连接质量
                    self.update_connection_quality()
                
                time.sleep(interval)
                
            except Exception as e:
                self.network_status_changed.emit(f"设备监控错误: {str(e)}")
                time.sleep(interval)
    
    def discover_devices(self, timeout: float = 5.0) -> List[DeviceInfo]:
        """发现设备"""
        try:
            # 使用Device API发现设备
            devices_data = self.device_api.discover_devices(timeout)
            
            discovered_devices = []
            
            for device_data in devices_data:
                # 转换为DeviceInfo对象
                device_info = self.create_device_info(device_data)
                
                # 更新设备列表
                old_device = self.devices.get(device_info.ip)
                self.devices[device_info.ip] = device_info
                
                # 发送信号
                if not old_device:
                    self.device_discovered.emit(device_info)
                elif old_device.status != device_info.status:
                    self.device_status_changed.emit(device_info.ip, device_info.status.value)
                
                discovered_devices.append(device_info)
            
            self.network_status_changed.emit(f"发现 {len(discovered_devices)} 个设备")
            return discovered_devices
            
        except Exception as e:
            self.network_status_changed.emit(f"设备发现错误: {str(e)}")
            return []
    
    def create_device_info(self, device_data: Dict[str, Any]) -> DeviceInfo:
        """创建设备信息对象"""
        # 解析设备类型
        model = device_data.get("model", "Unknown")
        device_type = DeviceType.UNKNOWN
        
        if "Rizon4s" in model:
            device_type = DeviceType.RIZON4S
        elif "Rizon4" in model:
            device_type = DeviceType.RIZON4
        elif "Rizon10s" in model:
            device_type = DeviceType.RIZON10S
        elif "Rizon10" in model:
            device_type = DeviceType.RIZON10
        
        # 解析网络接口
        network_interfaces = []
        network_info = device_data.get("network_info", {})
        if network_info:
            interface = NetworkInterface(
                name="eth0",
                ip=device_data["ip"],
                netmask=network_info.get("subnet_mask", "255.255.255.0"),
                gateway=network_info.get("gateway", ""),
                mac_address=network_info.get("mac_address", ""),
                status="up",
                connection_type=ConnectionType.ETHERNET
            )
            network_interfaces.append(interface)
        
        # 解析状态
        status_str = device_data.get("status", "unknown")
        try:
            status = DeviceStatus(status_str)
        except ValueError:
            status = DeviceStatus.UNKNOWN
        
        return DeviceInfo(
            ip=device_data["ip"],
            name=device_data.get("name", f"Device-{device_data['ip']}"),
            model=model,
            serial=device_data.get("serial", ""),
            firmware_version=device_data.get("firmware_version", ""),
            hardware_version=device_data.get("hardware_version", ""),
            status=status,
            device_type=device_type,
            capabilities=device_data.get("capabilities", []),
            network_interfaces=network_interfaces,
            last_seen=device_data.get("last_seen", time.time())
        )
    
    def auto_discover_devices(self):
        """自动发现设备（定时器回调）"""
        if self.auto_discovery_enabled:
            self.discover_devices()
    
    def scan_network(self, network: str, timeout: float = 10.0) -> ScanResult:
        """扫描网络"""
        try:
            self.scan_started.emit(network)
            start_time = time.time()
            
            # 使用Device API扫描网络
            found_ips = self.device_api.scan_network(network)
            
            scan_duration = time.time() - start_time
            
            # 创建扫描结果
            scan_result = ScanResult(
                network=network,
                scan_time=start_time,
                devices_found=found_ips,
                scan_duration=scan_duration
            )
            
            self.scan_results[network] = scan_result
            self.scan_completed.emit(scan_result)
            
            # 对发现的IP进行详细查询
            for ip in found_ips:
                device_info = self.device_api.get_device_info(ip)
                if device_info:
                    device_obj = self.create_device_info(device_info)
                    self.devices[ip] = device_obj
                    self.device_discovered.emit(device_obj)
            
            return scan_result
            
        except Exception as e:
            self.network_status_changed.emit(f"网络扫描错误: {str(e)}")
            return ScanResult(network, time.time(), [], 0.0)
    
    def scan_network_async(self, network: str, timeout: float = 10.0):
        """异步扫描网络"""
        def scan_worker():
            self.scan_network(network, timeout)
        
        self.scan_thread = threading.Thread(target=scan_worker, daemon=True)
        self.scan_thread.start()
    
    def connect_device(self, ip: str) -> bool:
        """连接设备"""
        try:
            if ip not in self.devices:
                self.device_error.emit(ip, "设备不存在")
                return False
            
            device_info = self.devices[ip]
            if device_info.status == DeviceStatus.CONNECTED:
                return True
            
            # 更新状态为连接中
            device_info.status = DeviceStatus.CONNECTING
            self.device_status_changed.emit(ip, device_info.status.value)
            
            # 使用Device API连接
            success = self.device_api.connect_device(ip)
            
            if success:
                device_info.status = DeviceStatus.CONNECTED
                device_info.last_seen = time.time()
                self.connected_devices.add(ip)
                self.device_connected.emit(ip)
                self.network_status_changed.emit(f"设备已连接: {device_info.name} ({ip})")
            else:
                device_info.status = DeviceStatus.ERROR
                self.device_error.emit(ip, "连接失败")
            
            self.device_status_changed.emit(ip, device_info.status.value)
            return success
            
        except Exception as e:
            self.device_error.emit(ip, f"连接错误: {str(e)}")
            return False
    
    def disconnect_device(self, ip: str) -> bool:
        """断开设备连接"""
        try:
            if ip not in self.devices:
                return False
            
            device_info = self.devices[ip]
            if device_info.status != DeviceStatus.CONNECTED:
                return True
            
            # 更新状态为断开中
            device_info.status = DeviceStatus.DISCONNECTING
            self.device_status_changed.emit(ip, device_info.status.value)
            
            # 使用Device API断开连接
            success = self.device_api.disconnect_device(ip)
            
            if success:
                device_info.status = DeviceStatus.ONLINE
                self.connected_devices.discard(ip)
                self.device_disconnected.emit(ip)
                self.network_status_changed.emit(f"设备已断开: {device_info.name} ({ip})")
            else:
                device_info.status = DeviceStatus.ERROR
                self.device_error.emit(ip, "断开连接失败")
            
            self.device_status_changed.emit(ip, device_info.status.value)
            return success
            
        except Exception as e:
            self.device_error.emit(ip, f"断开连接错误: {str(e)}")
            return False
    
    def ping_device(self, ip: str) -> bool:
        """Ping设备"""
        try:
            start_time = time.time()
            success = self.device_api.ping_device(ip)
            ping_time = time.time() - start_time
            
            if ip in self.devices:
                device_info = self.devices[ip]
                if success:
                    device_info.ping_latency = ping_time * 1000  # 转换为毫秒
                    device_info.last_seen = time.time()
                    
                    # 更新状态
                    if device_info.status == DeviceStatus.OFFLINE:
                        device_info.status = DeviceStatus.ONLINE
                        self.device_status_changed.emit(ip, device_info.status.value)
                else:
                    device_info.ping_latency = None
                    
                    # 更新状态为离线
                    if device_info.status == DeviceStatus.ONLINE:
                        device_info.status = DeviceStatus.OFFLINE
                        self.device_status_changed.emit(ip, device_info.status.value)
            
            return success
            
        except Exception as e:
            self.device_error.emit(ip, f"Ping错误: {str(e)}")
            return False
    
    def ping_all_devices(self):
        """Ping所有设备（定时器回调）"""
        for ip in list(self.devices.keys()):
            self.ping_device(ip)
    
    def check_device_timeouts(self):
        """检查设备超时"""
        current_time = time.time()
        
        for ip, device_info in self.devices.items():
            if device_info.time_since_last_seen > self.device_timeout:
                if device_info.status != DeviceStatus.OFFLINE:
                    device_info.status = DeviceStatus.OFFLINE
                    self.device_status_changed.emit(ip, device_info.status.value)
                    
                    # 如果设备已连接，则断开连接
                    if ip in self.connected_devices:
                        self.connected_devices.discard(ip)
                        self.device_disconnected.emit(ip)
    
    def update_connection_quality(self):
        """更新连接质量"""
        for device_info in self.devices.values():
            if device_info.ping_latency is not None:
                # 基于延迟计算连接质量（0-100）
                if device_info.ping_latency < 10:
                    quality = 100
                elif device_info.ping_latency < 50:
                    quality = 80
                elif device_info.ping_latency < 100:
                    quality = 60
                elif device_info.ping_latency < 200:
                    quality = 40
                else:
                    quality = 20
                
                device_info.connection_quality = quality
            else:
                device_info.connection_quality = 0
    
    def update_network_interfaces(self):
        """更新网络接口信息"""
        try:
            interfaces_data = self.device_api.get_network_interfaces()
            
            self.network_interfaces = []
            for interface_data in interfaces_data:
                interface = NetworkInterface(
                    name=interface_data["name"],
                    ip=interface_data["ip"],
                    netmask=interface_data["netmask"],
                    gateway=interface_data["gateway"],
                    mac_address=interface_data.get("mac_address", ""),
                    status=interface_data["status"],
                    connection_type=ConnectionType.ETHERNET  # 默认以太网
                )
                self.network_interfaces.append(interface)
            
        except Exception as e:
            self.network_status_changed.emit(f"更新网络接口错误: {str(e)}")
    
    def get_device_config(self, ip: str) -> Optional[Dict[str, Any]]:
        """获取设备配置"""
        try:
            return self.device_api.get_device_config(ip)
        except Exception as e:
            self.device_error.emit(ip, f"获取配置错误: {str(e)}")
            return None
    
    def update_device_config(self, ip: str, config: Dict[str, Any]) -> bool:
        """更新设备配置"""
        try:
            success = self.device_api.update_device_config(ip, config)
            if success:
                self.network_status_changed.emit(f"设备配置已更新: {ip}")
            else:
                self.device_error.emit(ip, "配置更新失败")
            return success
        except Exception as e:
            self.device_error.emit(ip, f"配置更新错误: {str(e)}")
            return False
    
    def reboot_device(self, ip: str) -> bool:
        """重启设备"""
        try:
            if ip not in self.devices:
                return False
            
            device_info = self.devices[ip]
            success = self.device_api.reboot_device(ip)
            
            if success:
                device_info.status = DeviceStatus.REBOOTING
                self.device_status_changed.emit(ip, device_info.status.value)
                self.network_status_changed.emit(f"设备重启中: {device_info.name} ({ip})")
            else:
                self.device_error.emit(ip, "重启失败")
            
            return success
            
        except Exception as e:
            self.device_error.emit(ip, f"重启错误: {str(e)}")
            return False
    
    def shutdown_device(self, ip: str) -> bool:
        """关闭设备"""
        try:
            if ip not in self.devices:
                return False
            
            device_info = self.devices[ip]
            success = self.device_api.shutdown_device(ip)
            
            if success:
                device_info.status = DeviceStatus.SHUTDOWN
                self.connected_devices.discard(ip)
                self.device_status_changed.emit(ip, device_info.status.value)
                self.device_disconnected.emit(ip)
                self.network_status_changed.emit(f"设备已关闭: {device_info.name} ({ip})")
            else:
                self.device_error.emit(ip, "关闭失败")
            
            return success
            
        except Exception as e:
            self.device_error.emit(ip, f"关闭错误: {str(e)}")
            return False
    
    def get_devices(self, status_filter: Optional[DeviceStatus] = None) -> List[DeviceInfo]:
        """获取设备列表"""
        devices = list(self.devices.values())
        
        if status_filter:
            devices = [device for device in devices if device.status == status_filter]
        
        return devices
    
    def get_connected_devices(self) -> List[DeviceInfo]:
        """获取已连接设备列表"""
        return [device for device in self.devices.values() if device.ip in self.connected_devices]
    
    def get_device_by_ip(self, ip: str) -> Optional[DeviceInfo]:
        """根据IP获取设备信息"""
        return self.devices.get(ip)
    
    def get_device_by_name(self, name: str) -> Optional[DeviceInfo]:
        """根据名称获取设备信息"""
        for device in self.devices.values():
            if device.name == name:
                return device
        return None
    
    def get_device_by_serial(self, serial: str) -> Optional[DeviceInfo]:
        """根据序列号获取设备信息"""
        for device in self.devices.values():
            if device.serial == serial:
                return device
        return None
    
    def get_network_interfaces(self) -> List[NetworkInterface]:
        """获取网络接口列表"""
        return self.network_interfaces
    
    def get_scan_results(self) -> List[ScanResult]:
        """获取扫描结果列表"""
        return list(self.scan_results.values())
    
    def clear_devices(self):
        """清空设备列表"""
        # 断开所有连接
        for ip in list(self.connected_devices):
            self.disconnect_device(ip)
        
        self.devices.clear()
        self.connected_devices.clear()
        self.network_status_changed.emit("设备列表已清空")
    
    def export_device_list(self, file_path: str) -> bool:
        """导出设备列表"""
        try:
            devices_data = []
            for device in self.devices.values():
                device_dict = asdict(device)
                # 转换枚举为字符串
                device_dict["status"] = device.status.value
                device_dict["device_type"] = device.device_type.value
                devices_data.append(device_dict)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(devices_data, f, indent=2, ensure_ascii=False)
            
            self.network_status_changed.emit(f"设备列表已导出: {file_path}")
            return True
            
        except Exception as e:
            self.network_status_changed.emit(f"导出设备列表错误: {str(e)}")
            return False
    
    def import_device_list(self, file_path: str) -> bool:
        """导入设备列表"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                devices_data = json.load(f)
            
            imported_count = 0
            for device_data in devices_data:
                try:
                    # 重建网络接口
                    interfaces = []
                    for interface_data in device_data.get("network_interfaces", []):
                        interface = NetworkInterface(**interface_data)
                        interfaces.append(interface)
                    
                    device_data["network_interfaces"] = interfaces
                    
                    # 创建设备信息
                    device_info = DeviceInfo(**device_data)
                    self.devices[device_info.ip] = device_info
                    
                    imported_count += 1
                    
                except Exception as e:
                    self.network_status_changed.emit(f"导入设备错误: {str(e)}")
                    continue
            
            self.network_status_changed.emit(f"已导入 {imported_count} 个设备")
            return True
            
        except Exception as e:
            self.network_status_changed.emit(f"导入设备列表错误: {str(e)}")
            return False
    
    def get_device_summary(self) -> Dict[str, Any]:
        """获取设备摘要"""
        total_devices = len(self.devices)
        online_devices = len([d for d in self.devices.values() if d.status == DeviceStatus.ONLINE])
        connected_devices = len(self.connected_devices)
        offline_devices = len([d for d in self.devices.values() if d.status == DeviceStatus.OFFLINE])
        
        # 按设备类型统计
        device_types = {}
        for device in self.devices.values():
            device_type = device.device_type.value
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        return {
            "total_devices": total_devices,
            "online_devices": online_devices,
            "connected_devices": connected_devices,
            "offline_devices": offline_devices,
            "device_types": device_types,
            "network_interfaces": len(self.network_interfaces),
            "auto_discovery_enabled": self.auto_discovery_enabled,
            "last_update": time.time()
        }