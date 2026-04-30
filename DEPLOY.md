# 人事考勤系统 - 部署指南

## 系统要求

### 服务器配置
- **CPU**: 2核+
- **内存**: 4GB+
- **硬盘**: 50GB+
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **网络**: 公网IP，带宽5Mbps+

### 软件环境
- Docker 20.10+
- Docker Compose 2.0+

## 部署步骤

### 1. 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# CentOS
sudo yum install -y docker
docker --version
docker-compose --version
```

### 2. 克隆项目

```bash
git clone <your-repo-url>
cd attendance_system
```

### 3. 配置环境变量

```bash
cp .env.example .env
nano .env
```

编辑 `.env` 文件：

```env
# 数据库配置
DB_USER=attendance
DB_PASSWORD=YourStrongPassword123
DB_NAME=attendance_db

# 应用配置
SECRET_KEY=YourSecretKeyHere
DEBUG=false

# 考勤机配置
ZK_DEFAULT_PORT=4370
```

### 4. 启动服务

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps
```

### 5. 初始化数据库

```bash
# 执行数据库迁移
docker-compose exec backend alembic upgrade head

# 创建管理员账户（如果需要）
docker-compose exec backend python scripts/create_admin.py
```

### 6. 配置 Nginx（生产环境）

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 证书
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 前端
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 7. 配置防火墙

```bash
# 开放必要端口
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 4370/tcp  # 考勤机通信端口
sudo ufw enable
```

## 考勤机网络配置

### 1. 配置考勤机 IP

在考勤机上设置：
- IP 地址: 与服务器同网段（如 192.168.1.100）
- 子网掩码: 255.255.255.0
- 网关: 192.168.1.1
- DNS: 8.8.8.8

### 2. 确保网络互通

```bash
# 从服务器测试连接
ping 192.168.1.100

# 测试端口
telnet 192.168.1.100 4370
```

### 3. 配置路由器（如果需要跨网段）

- 端口映射：将考勤机 4370 端口映射到公网
- 或者使用 VPN/专线连接

## 备份策略

### 自动备份

系统已配置定时备份任务，每天凌晨 0:30 自动备份数据库。

### 手动备份

```bash
# 备份数据库
docker-compose exec db pg_dump -U attendance attendance_db > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker-compose exec -T db psql -U attendance attendance_db < backup_20240115.sql
```

## 监控与维护

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看指定服务日志
docker-compose logs -f backend
docker-compose logs -f celery
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启指定服务
docker-compose restart backend
```

### 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose build

# 重启服务
docker-compose up -d
```

## 故障排查

### 常见问题

1. **无法连接考勤机**
   - 检查网络连通性
   - 确认考勤机 IP 和端口
   - 检查防火墙设置

2. **数据库连接失败**
   - 检查数据库容器状态
   - 确认数据库凭据
   - 查看数据库日志

3. **定时任务不执行**
   - 检查 Celery 容器状态
   - 查看 Celery 日志
   - 确认 Redis 连接

## 安全建议

1. **修改默认密码**
   - 数据库密码
   - 管理员账户密码
   - Redis 密码（如需）

2. **启用 HTTPS**
   - 配置 SSL 证书
   - 强制 HTTPS 访问

3. **限制访问**
   - 配置 IP 白名单
   - 使用 VPN 访问管理后台

4. **定期更新**
   - 更新系统补丁
   - 更新 Docker 镜像
   - 更新依赖包

## 联系方式

如有问题，请联系技术支持。
