# 系统架构文档

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层 (H5移动端)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  登录注册  │  │  AI对话  │  │  文档管理  │  │  在线缴费  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                    Vue3 + Vant UI                            │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/API
┌────────────────────────┴────────────────────────────────────┐
│                     应用服务层 (FastAPI)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  认证服务  │  │  AI服务  │  │  文档服务  │  │  支付服务  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              业务逻辑层 (Services)                   │    │
│  │  - AI对话引擎 (OpenAI GPT-4 + LangChain)            │    │
│  │  - RAG检索增强 (Embedding + Vector Search)          │    │
│  │  - 文档处理 (PDF/Word/Excel解析 + OCR)              │    │
│  │  - 支付集成 (微信支付 + 支付宝)                      │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                      数据存储层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │   Qdrant     │      │
│  │  关系数据库   │  │    缓存      │  │  向量数据库   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    外部服务层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  OpenAI  │  │  微信支付  │  │  支付宝   │  │  OSS存储  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 技术选型

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | 3.4+ | 前端框架 |
| Vant | 4.8+ | 移动端UI组件库 |
| Pinia | 2.1+ | 状态管理 |
| Axios | 1.6+ | HTTP客户端 |
| Vite | 5.0+ | 构建工具 |
| Vue Router | 4.2+ | 路由管理 |

**选型理由:**
- Vue3提供更好的性能和TypeScript支持
- Vant是成熟的移动端组件库,开箱即用
- Vite提供极快的开发体验
- 轻量级,适合移动端H5应用

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.109+ | Web框架 |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.5+ | 数据验证 |
| OpenAI | 1.10+ | AI大模型 |
| LangChain | 0.1+ | RAG框架 |
| PostgreSQL | 15+ | 关系数据库 |
| Redis | 7+ | 缓存 |
| Qdrant | latest | 向量数据库 |

**选型理由:**
- FastAPI是现代、高性能的Python Web框架
- 原生支持异步,适合AI应用
- 自动生成API文档
- 强大的类型检查和验证
- 生态丰富,AI库支持好

### AI技术栈

| 技术 | 用途 |
|------|------|
| OpenAI GPT-4 | 主要对话模型 |
| text-embedding-3-small | 文本向量化 |
| LangChain | RAG框架 |
| Sentence Transformers | 离线向量化(可选) |
| Qdrant | 向量存储和检索 |

**RAG流程:**
```
用户问题 → 向量化 → 检索相关文档 → 构建上下文 → LLM生成回答
```

## 核心模块设计

### 1. 认证模块 (Auth)

**功能:**
- 用户注册/登录
- JWT Token生成和验证
- 权限控制(RBAC)
- 会话管理

**关键代码:**
```python
# JWT token生成
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 2. AI对话模块 (Chat)

**功能:**
- 多轮对话管理
- 上下文理解
- RAG检索增强
- 流式响应(可选)

**关键流程:**
```python
async def chat(conversation_id, user_message):
    # 1. 获取对话历史
    history = await get_conversation_history(conversation_id)
    
    # 2. RAG检索相关文档
    relevant_docs = await vector_store.search(user_message)
    
    # 3. 构建prompt
    messages = build_messages(history, relevant_docs, user_message)
    
    # 4. 调用LLM
    response = await openai.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages
    )
    
    return response
```

### 3. 文档管理模块 (Documents)

**功能:**
- 多格式文档上传
- 文本提取(PDF/Word/Excel/图片OCR)
- AI自动分类
- 智能摘要生成
- 向量化存储

**处理流程:**
```
上传文档 → 保存文件 → 提取文本 → AI分类 → 生成摘要 → 向量化 → 存储
```

**关键技术:**
- PyMuPDF: PDF文本提取
- python-docx: Word文档处理
- openpyxl: Excel处理
- pytesseract: OCR文字识别
- Sentence Transformers: 文本向量化

### 4. 支付模块 (Payment)

**功能:**
- 账单生成和管理
- 微信支付集成
- 支付宝集成
- 支付回调处理
- 订单查询

**支付流程:**
```
创建账单 → 用户发起支付 → 调用支付接口 → 跳转支付页面 
→ 用户完成支付 → 支付回调 → 更新订单状态
```

### 5. 向量检索模块 (Vector Store)

**功能:**
- 文档向量化
- 语义相似度搜索
- 向量存储管理

**检索流程:**
```python
async def search(query: str, limit: int = 5):
    # 1. 查询向量化
    query_vector = encoder.encode(query)
    
    # 2. 向量搜索
    results = await qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit
    )
    
    # 3. 返回相关文档
    return format_results(results)
```

## 数据模型

### 用户表 (users)
```sql
- id: 主键
- username: 用户名(唯一)
- email: 邮箱
- phone: 手机号
- hashed_password: 密码哈希
- role: 角色(admin/manager/owner)
- property_id: 所属物业ID
- created_at: 创建时间
```

### 物业表 (properties)
```sql
- id: 主键
- name: 物业名称
- code: 物业代码(唯一)
- address: 地址
- total_units: 总户数
- contact_phone: 联系电话
- config: 配置信息(JSON)
```

### 文档表 (documents)
```sql
- id: 主键
- property_id: 物业ID
- title: 标题
- category: 分类(枚举)
- file_path: 文件路径
- content: 文本内容
- summary: AI摘要
- vector_id: 向量ID
- created_at: 创建时间
```

### 账单表 (bills)
```sql
- id: 主键
- bill_number: 账单号(唯一)
- user_id: 用户ID
- fee_type: 费用类型
- amount: 金额
- due_date: 到期日期
- status: 状态(pending/paid/overdue)
```

### 对话表 (conversations)
```sql
- id: 主键
- user_id: 用户ID
- property_id: 物业ID
- title: 对话标题
- status: 状态
- message_count: 消息数量
```

### 消息表 (messages)
```sql
- id: 主键
- conversation_id: 对话ID
- role: 角色(user/assistant)
- content: 内容
- sources: 引用文档(JSON)
- created_at: 创建时间
```

## 安全设计

### 1. 认证安全
- JWT Token认证
- 密码BCrypt加密
- Token过期时间控制
- 防暴力破解(限流)

### 2. 数据安全
- 多租户数据隔离
- SQL注入防护(ORM)
- XSS防护
- CSRF防护

### 3. API安全
- HTTPS加密传输
- CORS跨域控制
- 请求频率限制
- 敏感数据脱敏

### 4. 支付安全
- 签名验证
- 回调IP白名单
- 订单防重放
- 金额校验

## 性能优化

### 1. 数据库优化
- 索引优化(用户名、邮箱、账单号等)
- 查询优化(避免N+1问题)
- 连接池配置
- 读写分离(可选)

### 2. 缓存策略
- Redis缓存热点数据
- 用户会话缓存
- API响应缓存
- 文档元数据缓存

### 3. AI性能优化
- 异步文档处理(Celery)
- 批量向量化
- 向量缓存
- 流式响应

### 4. 前端优化
- 代码分割
- 懒加载
- 图片压缩
- CDN加速

## 扩展性设计

### 1. 水平扩展
- 无状态API设计
- 负载均衡
- 数据库分片
- 微服务拆分(未来)

### 2. 功能扩展
- 插件化架构
- 配置化管理
- 多语言支持
- 多种AI模型支持

### 3. 集成扩展
- Webhook机制
- 开放API
- SSO单点登录
- 第三方服务集成

## 监控与运维

### 1. 日志系统
- 结构化日志(Loguru)
- 日志分级(DEBUG/INFO/WARNING/ERROR)
- 日志轮转
- ELK日志分析(可选)

### 2. 监控指标
- API响应时间
- 数据库性能
- AI调用次数和成本
- 错误率

### 3. 告警机制
- 服务异常告警
- 性能告警
- 费用告警
- 安全告警

## 部署架构

### 开发环境
```
Docker Compose
├── PostgreSQL (端口5432)
├── Redis (端口6379)
├── Qdrant (端口6333)
├── Backend (端口8000)
└── Frontend (端口5173)
```

### 生产环境
```
Nginx (反向代理 + SSL)
├── Frontend (静态文件)
├── Backend API (多实例)
│   ├── Gunicorn/Uvicorn Workers
│   └── Celery Workers
├── PostgreSQL (主从复制)
├── Redis (哨兵模式)
└── Qdrant (集群模式)
```

## 最佳实践

### 1. 代码规范
- PEP 8 (Python)
- ESLint + Prettier (JavaScript)
- 类型注解
- 文档注释

### 2. Git工作流
- 主分支保护
- Feature分支开发
- Code Review
- CI/CD自动化

### 3. 测试策略
- 单元测试(Pytest)
- 集成测试
- E2E测试
- 性能测试

### 4. 文档维护
- API文档自动生成
- 架构图定期更新
- 变更日志记录
- 部署手册完善

## 未来规划

### 短期(3个月)
- [ ] 完善报修功能
- [ ] 增加投诉管理
- [ ] 社区公告系统
- [ ] 访客登记

### 中期(6个月)
- [ ] 移动APP(React Native)
- [ ] 小程序版本
- [ ] IoT设备集成
- [ ] 数据大屏

### 长期(1年)
- [ ] AI预测性维护
- [ ] 智能能耗管理
- [ ] 社区商业服务
- [ ] 开放平台API
