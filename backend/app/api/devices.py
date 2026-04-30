from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse, DeviceStatus
from app.services.zk_service import ZKServiceManager, ZKDeviceService

router = APIRouter(prefix="/devices", tags=["设备管理"])


@router.post("/", response_model=DeviceResponse)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """添加考勤机设备"""
    # 测试连接
    if not ZKServiceManager.test_connection(device.ip_address, device.port):
        raise HTTPException(status_code=400, detail="无法连接到考勤机，请检查IP和端口")
    
    # 获取设备信息
    device_info = None
    try:
        with ZKDeviceService(device.ip_address, device.port) as service:
            device_info = service.get_device_info()
    except Exception:
        pass
    
    # 创建设备记录
    db_device = Device(
        name=device.name,
        ip_address=device.ip_address,
        port=device.port,
        device_type=device.device_type,
        serial_number=device_info.get("serial_number") if device_info else None,
        status="online",
        location=device.location,
        is_active=True
    )
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    return db_device


@router.get("/", response_model=List[DeviceResponse])
def list_devices(skip: int = 0, limit: int = 100, check_status: bool = False, db: Session = Depends(get_db)):
    """获取设备列表，check_status=true时实时检测所有设备状态"""
    devices = db.query(Device).offset(skip).limit(limit).all()
    
    if check_status:
        for device in devices:
            try:
                with ZKDeviceService(device.ip_address, device.port) as service:
                    info = service.get_device_info()
                    device.status = "online" if info else "offline"
            except Exception:
                device.status = "offline"
        db.commit()
    
    return devices


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(device_id: int, db: Session = Depends(get_db)):
    """获取设备详情"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(device_id: int, device_update: DeviceUpdate, db: Session = Depends(get_db)):
    """更新设备信息"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 更新字段
    for field, value in device_update.dict(exclude_unset=True).items():
        setattr(device, field, value)
    
    db.commit()
    db.refresh(device)
    return device


@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    """删除设备"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    db.delete(device)
    db.commit()
    return {"message": "设备删除成功"}


@router.get("/{device_id}/status", response_model=DeviceStatus)
def get_device_status(device_id: int, db: Session = Depends(get_db)):
    """获取设备状态"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 测试连接
    try:
        with ZKDeviceService(device.ip_address, device.port) as service:
            info = service.get_device_info()
            if info:
                return {
                    "device_id": device_id,
                    "status": "online",
                    "user_count": info.get("user_count"),
                    "record_count": info.get("record_count"),
                    "firmware_version": info.get("firmware_version"),
                    "device_time": service.get_time()
                }
    except Exception:
        pass
    
    return {
        "device_id": device_id,
        "status": "offline",
        "user_count": None,
        "record_count": None,
        "firmware_version": None,
        "device_time": None
    }


@router.post("/{device_id}/sync")
def sync_device(device_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """同步考勤机数据"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # TODO: 启动后台任务同步数据
    return {"message": "同步任务已启动", "device_id": device_id}


@router.post("/{device_id}/download-records")
def download_records(device_id: int, db: Session = Depends(get_db)):
    """从考勤机下载打卡记录"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    try:
        with ZKDeviceService(device.ip_address, device.port) as service:
            records = service.get_attendance_records()
            
            # 更新设备最后同步时间
            device.last_sync = datetime.now()
            db.commit()
            
            return {
                "message": "打卡数据下载成功",
                "device_id": device_id,
                "device_name": device.name,
                "record_count": len(records),
                "records": records[:100]  # 最多返回前100条
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载打卡数据失败: {str(e)}")


@router.post("/{device_id}/restart")
def restart_device(device_id: int, db: Session = Depends(get_db)):
    """重启考勤机"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    try:
        with ZKDeviceService(device.ip_address, device.port) as service:
            service.restart()
            return {"message": "重启指令已发送", "device_id": device_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重启失败: {str(e)}")


@router.post("/{device_id}/test-connection")
def test_connection(device_id: int, db: Session = Depends(get_db)):
    """测试设备连接"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    success = ZKServiceManager.test_connection(device.ip_address, device.port)
    return {
        "device_id": device_id,
        "connected": success,
        "message": "连接成功" if success else "连接失败"
    }
