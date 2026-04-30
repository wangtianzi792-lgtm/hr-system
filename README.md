# 人事考勤系统 (HR Attendance System)

## 项目概述
基于 Python + pyzk 的 ZKTeco xFace100 考勤机云端管理系统

## 技术栈
- **后端**: Python 3.11 + FastAPI
- **数据库**: PostgreSQL 14
- **缓存**: Redis
- **任务队列**: Celery + Redis
- **前端**: Vue 3 + Element Plus
- **部署**: Docker + Docker Compose
- **考勤机通信**: pyzk 库

## 系统架构
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   前端 (Vue3)   │────▶│  FastAPI 后端   │────▶│   PostgreSQL    │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │  Celery  │ │  Redis   │ │  xFace100│
            │  定时任务 │ │  缓存    │ │  考勤机  │
            └──────────┘ └──────────┘ └──────────┘
```

## 核心功能模块

### 1. 设备管理
- 考勤机配置（IP、端口、名称）
- 设备状态监控（在线/离线）
- 多设备支持

### 2. 员工管理
- 员工信息 CRUD
- 人脸/指纹模板同步
- 部门管理

### 3. 考勤管理
- 实时考勤记录采集
- 考勤规则配置（班次、节假日）
- 迟到/早退/旷工自动计算
- 加班/请假/出差审批

### 4. 报表统计
- 日报/月报/年报
- 考勤异常统计
- 导出 Excel/PDF

### 5. 系统管理
- 用户权限管理
- 操作日志
- 数据备份

## 项目结构
```
attendance_system/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 配置、安全
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 单元测试
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Vue3 前端
│   ├── src/
│   ├── public/
│   └── Dockerfile
├── docker-compose.yml      # Docker 编排
└── README.md
```

## 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+

### 部署步骤
```bash
# 1. 克隆项目
git clone <repository>
cd attendance_system

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 启动服务
docker-compose up -d

# 4. 初始化数据库
docker-compose exec backend alembic upgrade head

# 5. 创建管理员账户
docker-compose exec backend python scripts/create_admin.py
```

### 访问系统
- 前端: http://localhost:8080
- API 文档: http://localhost:8000/docs
- 管理员后台: http://localhost:8080/admin

## 考勤机配置

### xFace100 网络设置
1. 进入考勤机菜单 → 通讯设置 → 以太网
2. 设置 IP 地址（与服务器同网段）
3. 端口默认: 4370
4. 确保服务器能 ping 通考勤机 IP

### 系统添加设备
在管理后台 → 设备管理 → 添加设备：
- 设备名称: 一楼前台考勤机
- IP 地址: 192.168.1.100
- 端口: 4370
- 类型: xFace100

## API 接口文档

### 设备管理
- `POST /api/devices` - 添加设备
- `GET /api/devices` - 设备列表
- `GET /api/devices/{id}/status` - 设备状态
- `POST /api/devices/{id}/sync` - 同步数据

### 员工管理
- `POST /api/employees` - 添加员工
- `GET /api/employees` - 员工列表
- `PUT /api/employees/{id}` - 更新员工
- `POST /api/employees/{id}/enroll` - 下发到考勤机

### 考勤记录
- `GET /api/attendance` - 考勤记录查询
- `POST /api/attendance/collect` - 手动采集
- `GET /api/attendance/report` - 考勤报表

## 定时任务
- 每5分钟自动采集考勤记录
- 每天凌晨生成日报
- 每月1号生成月报
- 每周备份数据库

## 开发计划
1. **第一阶段**: 基础框架搭建 + 设备连接
2. **第二阶段**: 员工管理 + 考勤采集
3. **第三阶段**: 考勤规则 + 报表统计
4. **第四阶段**: 审批流程 + 权限管理
5. **第五阶段**: 前端优化 + 部署上线

## 注意事项
1. 确保服务器与考勤机网络互通
2. 防火墙开放 4370 端口
3. 定期备份数据库
4. 考勤机时间同步

## 技术支持
- pyzk 文档: https://github.com/fananimi/pyzk
- ZKTeco 官网: https://www.zkteco.com
