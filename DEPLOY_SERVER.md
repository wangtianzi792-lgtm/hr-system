# HR 系统服务器部署指南

## 1. 准备服务器

```bash
# Ubuntu/Debian
apt update && apt install -y python3 python3-pip nginx redis-server

# 安装依赖
cd /path/to/extracted
pip3 install -r requirements.txt
```

## 2. 配置

编辑 `extracted/app/core/config.py`：

```python
# 生产环境建议用 PostgreSQL
DATABASE_URL: str = "postgresql://user:password@localhost:5432/hr_db"

# Redis（如果是 Linux 服务器，localhost 即可）
REDIS_URL: str = "redis://localhost:6379/0"
```

或创建 `.env` 文件：

```
DATABASE_URL=postgresql://user:password@localhost:5432/hr_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=你的随机密钥
DEBUG=false
```

## 3. 数据库（PostgreSQL）

```bash
# 创建数据库
sudo -u postgres psql
CREATE DATABASE hr_db;
CREATE USER hr_user WITH ENCRYPTED PASSWORD '密码';
GRANT ALL PRIVILEGES ON DATABASE hr_db TO hr_user;
\q

# 初始化表（FastAPI 启动时会自动创建）
# 管理员账号：admin / admin123
```

## 4. 启动后端

方式一：直接启动（测试用）
```bash
cd /path/to/extracted
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

方式二：systemd 管理（推荐）
```bash
# 创建服务文件
sudo nano /etc/systemd/system/hr-backend.service
```

写入：
```ini
[Unit]
Description=HR Attendance System
After=network.target redis.service postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/extracted
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable hr-backend
sudo systemctl start hr-backend
```

## 5. 配置 Nginx 反向代理

```bash
sudo nano /etc/nginx/sites-available/hr
```

写入：
```nginx
server {
    listen 80;
    server_name 你的域名或IP;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/hr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 6. SSL 证书（可选）

```bash
apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d 你的域名
```

## 7. 防火墙

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 8. 检查状态

```bash
sudo systemctl status hr-backend
sudo nginx -t
curl http://localhost:8000/health
```

## 文件传输

从本机拷贝到服务器：
```bash
scp -r /Users/jiuhua/HR系统/extracted user@服务器IP:/opt/hr_system/
```

## 目录结构

```
/opt/hr_system/
├── app/              # 后端代码
│   ├── main.py      # 入口
│   ├── core/        # 配置
│   └── api/         # API 路由
├── dist/            # Vue 前端（构建产物）
├── attendance.db   # SQLite 数据库（开发用）
└── requirements.txt
```
