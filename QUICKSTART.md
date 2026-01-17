# 快速启动指南

欢迎使用物业管理AI应用系统!本指南将帮助您在5分钟内启动应用。

## 🚀 快速开始 (推荐使用Docker)

### 前置要求

- Docker Desktop (Mac/Windows) 或 Docker Engine (Linux)
- 至少4GB可用内存

### 一键启动

```bash
# 1. 进入项目目录
cd /Users/tonyyu/Documents/物业管理

# 2. 复制环境变量文件
cp backend/.env.example backend/.env

# 3. 编辑环境变量(必须填写)
# 使用你喜欢的编辑器打开 backend/.env
# 必须配置的项目:
#   - OPENAI_API_KEY=your-openai-api-key  (必需)
#   - SECRET_KEY=生成一个随机字符串  (必需)

# 4. 启动所有服务
docker-compose up -d

# 5. 等待服务启动(约30秒)
# 查看启动日志
docker-compose logs -f
```

### 访问应用

- **前端H5界面**: http://localhost:5173
- **后端API文档**: http://localhost:8000/api/docs
- **健康检查**: http://localhost:8000/health

### 测试账号

首次使用需要注册账号:
1. 打开 http://localhost:5173
2. 点击"注册账号"
3. 填写信息并注册
4. 使用注册的账号登录

## 📱 功能演示

### 1. AI智能咨询

登录后,点击"智能咨询"或首页的"开始对话",尝试以下问题:
- "物业费怎么缴纳?"
- "如何报修?"
- "停车位规定是什么?"
- "装修需要什么手续?"

### 2. 文档管理

1. 进入"文档查询"页面
2. 点击右下角的"+"按钮
3. 上传PDF、Word等文档
4. AI会自动分类、提取内容并生成摘要
5. 可以使用语义搜索查找相关文档

### 3. 在线缴费

1. 进入"缴费中心"
2. 查看待缴费账单
3. 选择账单点击"立即缴费"
4. 选择支付方式(微信/支付宝)

**注意**: 支付功能需要配置微信/支付宝密钥

## 🛠️ 手动启动 (不使用Docker)

### 后端服务

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 需要手动启动数据库服务:
# - PostgreSQL (端口5432)
# - Redis (端口6379)  
# - Qdrant (端口6333)

# 启动应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 🎯 核心功能说明

### AI智能对话
- 基于GPT-4的智能客服
- 支持多轮对话上下文理解
- RAG技术结合本地文档知识库
- 24/7全天候响应

### 文档智能管理
- 支持PDF、Word、Excel、图片等格式
- AI自动分类归档
- OCR文字识别
- 智能摘要生成
- 语义搜索(支持模糊查询)

### 支付系统
- 集成微信支付、支付宝
- 账单自动生成
- 支付状态实时更新
- 电子账单查询

### 多租户架构
- 每个物业独立数据隔离
- 专属知识库
- 个性化AI服务

## ⚙️ 配置说明

### 必需配置

**backend/.env 文件中必须配置:**

1. **OPENAI_API_KEY** (必需)
   ```
   OPENAI_API_KEY=sk-your-openai-api-key
   ```
   - 获取方式: https://platform.openai.com/api-keys
   - 用于AI对话和文档处理

2. **SECRET_KEY** (必需)
   ```
   SECRET_KEY=your-random-secret-key-at-least-32-characters
   ```
   - 用于JWT token加密
   - 生成方式: `openssl rand -hex 32`

### 可选配置

3. **微信支付** (可选)
   ```
   WECHAT_PAY_APPID=your-appid
   WECHAT_PAY_MCH_ID=your-mch-id
   WECHAT_PAY_API_KEY=your-api-key
   ```

4. **支付宝** (可选)
   ```
   ALIPAY_APPID=your-appid
   ALIPAY_PRIVATE_KEY=your-private-key
   ALIPAY_PUBLIC_KEY=alipay-public-key
   ```

## 🐛 故障排除

### 容器无法启动

```bash
# 查看日志
docker-compose logs backend
docker-compose logs frontend

# 检查端口占用
lsof -i :5173  # 前端
lsof -i :8000  # 后端
lsof -i :5432  # PostgreSQL
```

### AI功能不可用

- 检查 OPENAI_API_KEY 是否正确配置
- 确认OpenAI账户有余额
- 查看后端日志: `docker-compose logs backend`

### 前端无法连接后端

- 确认后端服务正在运行: http://localhost:8000/health
- 检查浏览器控制台错误信息
- 确认CORS配置正确

### 数据库连接失败

```bash
# 检查PostgreSQL容器
docker-compose ps postgres

# 进入数据库
docker-compose exec postgres psql -U postgres -d property_management
```

## 📚 更多文档

- [完整部署指南](docs/DEPLOYMENT.md)
- [API文档](docs/API.md)
- [在线API文档](http://localhost:8000/api/docs)

## 💡 技术栈

**后端:**
- FastAPI - 现代Python Web框架
- PostgreSQL - 关系数据库
- Redis - 缓存
- Qdrant - 向量数据库
- OpenAI GPT-4 - 大语言模型
- LangChain - RAG框架

**前端:**
- Vue 3 - 渐进式框架
- Vant 4 - 移动端UI组件库
- Pinia - 状态管理
- Vite - 构建工具

## 🤝 获取帮助

如有问题:
1. 查看日志: `docker-compose logs -f`
2. 检查API文档: http://localhost:8000/api/docs
3. 查看详细部署指南: docs/DEPLOYMENT.md

## 🎉 开始使用

现在您可以:
1. 访问 http://localhost:5173 开始体验
2. 注册账号并登录
3. 与AI助手对话
4. 上传文档测试智能分类
5. 探索更多功能!

祝使用愉快! 🚀
