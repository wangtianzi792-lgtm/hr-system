"""
ZKTeco 考勤机服务
使用 pyzk 库与考勤机通信
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from zk import ZK, const
from zk import base as zk_base

from app.core.config import settings

logger = logging.getLogger(__name__)

# Monkey patch: 修复日期解码错误（某些设备记录日期损坏）
_original_decode_time = zk_base.ZK._ZK__decode_time

def _safe_decode_time(self, t):
    """安全的日期解码，处理损坏的日期数据"""
    try:
        return _original_decode_time(self, t)
    except ValueError as e:
        logger.warning(f"日期解码失败: {e}，返回None")
        return None

zk_base.ZK._ZK__decode_time = _safe_decode_time


class ZKDeviceService:
    """考勤机设备服务"""
    
    def __init__(self, ip: str, port: int = 4370, timeout: int = 5):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.conn = None
        self.zk = ZK(ip, port=port, timeout=timeout)
    
    def connect(self) -> bool:
        """连接考勤机"""
        try:
            self.conn = self.zk.connect()
            logger.info(f"成功连接到考勤机 {self.ip}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"连接考勤机失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.conn:
            try:
                self.conn.disconnect()
                logger.info(f"已断开考勤机 {self.ip}:{self.port}")
            except Exception as e:
                logger.error(f"断开连接失败: {e}")
    
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """获取设备信息"""
        try:
            if not self.conn:
                if not self.connect():
                    return None
            
            # 使用实际的pyzk API
            self.conn.read_sizes()
            
            return {
                "firmware_version": self.conn.get_firmware_version(),
                "device_name": self.conn.get_device_name(),
                "serial_number": self.conn.get_serialnumber(),
                "platform": self.conn.get_platform(),
                "mac_address": self.conn.get_mac(),
                "user_count": len(self.conn.get_users()),
                "user_capacity": self.conn.users,
                "record_count": self.conn.records,
                "record_capacity": self.conn.rec_cap,
                "fp_count": self.conn.fingers,
                "fp_capacity": self.conn.fingers_cap,
                "face_count": self.conn.faces,
                "face_capacity": self.conn.faces_cap,
            }
        except Exception as e:
            logger.error(f"获取设备信息失败: {e}")
            return None
    
    def get_users(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        try:
            if not self.conn:
                if not self.connect():
                    return []
            
            users = self.conn.get_users()
            return [
                {
                    "uid": user.uid,
                    "user_id": user.user_id,
                    "name": user.name,
                    "privilege": user.privilege,
                    "password": user.password,
                    "group_id": user.group_id,
                }
                for user in users
            ]
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return []
    
    def set_user(self, user_id: str, name: str, password: str = "", 
                 privilege: int = 0, group_id: str = "") -> bool:
        """添加/更新用户"""
        try:
            if not self.conn:
                if not self.connect():
                    return False
            
            self.conn.set_user(
                uid=int(user_id),
                name=name,
                privilege=privilege,
                password=password,
                group_id=group_id,
                user_id=user_id
            )
            logger.info(f"成功设置用户: {name} ({user_id})")
            return True
        except Exception as e:
            logger.error(f"设置用户失败: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        try:
            if not self.conn:
                if not self.connect():
                    return False
            
            self.conn.delete_user(user_id=user_id)
            logger.info(f"成功删除用户: {user_id}")
            return True
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return False
    
    def get_attendance_records(self) -> List[Dict[str, Any]]:
        """获取考勤记录"""
        try:
            if not self.conn:
                if not self.connect():
                    return []
            
            records = self.conn.get_attendance()
            result = []
            for record in records:
                try:
                    # 跳过无效记录（日期为2000年或None，或未来日期）
                    if not record.timestamp or record.timestamp.year < 2020 or record.timestamp.year > 2030:
                        continue
                    # 跳过用户ID为空的记录或包含特殊字符的记录
                    if not record.user_id or not str(record.user_id).strip().isdigit():
                        continue
                    
                    result.append({
                        "user_id": str(record.user_id).strip(),
                        "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "status": record.status,
                        "punch": record.punch,
                        "uid": record.uid,
                    })
                except Exception as e:
                    logger.warning(f"解析单条考勤记录失败: {e}")
                    continue
            return result
        except Exception as e:
            logger.error(f"获取考勤记录失败: {e}")
            return []
    
    def clear_attendance(self) -> bool:
        """清空考勤记录"""
        try:
            if not self.conn:
                if not self.connect():
                    return False
            
            self.conn.clear_attendance()
            logger.info("成功清空考勤记录")
            return True
        except Exception as e:
            logger.error(f"清空考勤记录失败: {e}")
            return False
    
    def get_time(self) -> Optional[datetime]:
        """获取设备时间"""
        try:
            if not self.conn:
                if not self.connect():
                    return None
            
            return self.conn.get_time()
        except Exception as e:
            logger.error(f"获取设备时间失败: {e}")
            return None
    
    def set_time(self, dt: datetime) -> bool:
        """设置设备时间"""
        try:
            if not self.conn:
                if not self.connect():
                    return False
            
            self.conn.set_time(dt)
            logger.info(f"成功设置设备时间: {dt}")
            return True
        except Exception as e:
            logger.error(f"设置设备时间失败: {e}")
            return False
    
    def restart(self) -> bool:
        """重启设备"""
        try:
            if not self.conn:
                if not self.connect():
                    return False
            
            self.conn.restart()
            logger.info("设备重启指令已发送")
            return True
        except Exception as e:
            logger.error(f"重启设备失败: {e}")
            return False
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class ZKServiceManager:
    """考勤机服务管理器"""
    
    @staticmethod
    def test_connection(ip: str, port: int = 4370) -> bool:
        """测试考勤机连接"""
        try:
            with ZKDeviceService(ip, port) as service:
                info = service.get_device_info()
                return info is not None
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False
    
    @staticmethod
    def sync_attendance(ip: str, port: int = 4370) -> List[Dict[str, Any]]:
        """同步考勤记录"""
        try:
            with ZKDeviceService(ip, port) as service:
                return service.get_attendance_records()
        except Exception as e:
            logger.error(f"同步考勤记录失败: {e}")
            return []
