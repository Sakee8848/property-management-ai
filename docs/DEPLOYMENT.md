# 部署指南

## 本地开发环境

### 1. 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (可选)

### 2. 快速启动

#### 使用 Docker Compose(推荐)

```bash
# 克隆项目
cd /Users/tonyyu/Documents/物业管理

# 复制环境变量文件
cp backend/.env.example backend/.env

# 编辑 .env 文件,填入必要的配置(OpenAI API Key等)
vim backend/.env

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 访问应用
# 前端: http://localhost:5173
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/api/docs
```

#### 手动启动

**后端服务:**

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动数据库(PostgreSQL, Redis, Qdrant)
# 使用Docker启动
docker-compose up -d postgres redis qdrant

# 运行数据库迁移
alembic upgrade head

# 启动应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端服务:**

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

## 生产环境部署

### 1. 服务器要求

- 2核CPU, 4GB内存以上
- Ubuntu 20.04+ / CentOS 7+
- Docker & Docker Compose

### 2. 部署步骤

#### 准备工作

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 上传代码

```bash
# 使用Git
git clone <your-repo-url>
cd 物业管理

# 或使用scp上传
scp -r /Users/tonyyu/Documents/物业管理 user@server:/opt/
```

#### 配置环境变量

```bash
cd /opt/物业管理

# 复制并编辑环境变量
cp backend/.env.example backend/.env
vim backend/.env

# 重要配置项:
# - DATABASE_URL: PostgreSQL连接
# - OPENAI_API_KEY: OpenAI密钥
# - SECRET_KEY: JWT密钥(生成随机字符串)
# - 支付配置: 微信/支付宝密钥
```

#### 启动服务

```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 配置Nginx反向代理

```nginx
# /etc/nginx/sites-available/property-management

server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/property-management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 配置HTTPS(使用Let's Encrypt)

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 3. 数据库备份

```bash
# 备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backup/postgres

docker exec property-postgres pg_dump -U postgres property_management | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# 保留最近7天的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

### 4. 监控与日志

#### 日志管理

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看所有日志
docker-compose logs -f

# 清理日志
docker-compose logs --tail=0 -f
```

#### 性能监控

可以使用以下工具:
- Prometheus + Grafana (系统指标)
- Sentry (错误追踪)
- ELK Stack (日志分析)

### 5. 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose build

# 重启服务(零停机时间)
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend

# 数据库迁移
docker-compose exec backend alembic upgrade head
```

### 6. 常见问题

**Q: 容器无法启动?**
```bash
# 查看日志
docker-compose logs backend

# 检查端口占用
netstat -tulpn | grep 8000
```

**Q: 数据库连接失败?**
```bash
# 检查数据库容器
docker-compose ps postgres

# 进入数据库容器
docker-compose exec postgres psql -U postgres
```

**Q: 前端无法连接后端?**
- 检查 frontend/src/utils/axios.js 中的 baseURL
- 确保后端服务正常运行
- 检查CORS配置

## 性能优化建议

1. **数据库优化**
   - 为常用查询字段添加索引
   - 定期清理过期数据
   - 使用连接池

2. **缓存策略**
   - Redis缓存热点数据
   - 使用CDN加速静态资源

3. **AI服务优化**
   - 使用Celery异步处理文档
   - 批量向量化处理
   - 限流保护

4. **前端优化**
   - 代码分割
   - 图片懒加载
   - 启用Gzip压缩

## 安全建议

1. 修改默认密码和密钥
2. 启用HTTPS
3. 配置防火墙规则
4. 定期更新依赖
5. 限制API访问频率
6. 备份重要数据
