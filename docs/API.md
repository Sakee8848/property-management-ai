# API 文档

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Bearer Token (JWT)
- **Content-Type**: application/json

## 认证接口

### 用户注册

```http
POST /api/auth/register
```

**请求参数:**
```json
{
  "username": "test_user",
  "email": "user@example.com",
  "phone": "13800138000",
  "password": "password123",
  "full_name": "张三"
}
```

**响应:**
```json
{
  "id": 1,
  "username": "test_user",
  "email": "user@example.com",
  "role": "owner",
  "is_active": true
}
```

### 用户登录

```http
POST /api/auth/login
```

**请求参数 (form-data):**
```
username: test_user
password: password123
```

**响应:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "test_user",
    "role": "owner"
  }
}
```

### 获取当前用户信息

```http
GET /api/auth/me
Authorization: Bearer <token>
```

## AI聊天接口

### 发送消息

```http
POST /api/chat/send
Authorization: Bearer <token>
```

**请求参数:**
```json
{
  "content": "物业费怎么缴纳?",
  "conversation_id": null
}
```

**响应:**
```json
{
  "id": 1,
  "role": "assistant",
  "content": "您可以通过以下方式缴纳物业费...",
  "sources": [
    {
      "document_id": 1,
      "title": "物业缴费指南",
      "score": 0.95
    }
  ],
  "created_at": "2024-01-15T10:00:00"
}
```

### 获取会话列表

```http
GET /api/chat/conversations
Authorization: Bearer <token>
```

### 获取会话详情

```http
GET /api/chat/conversations/{conversation_id}
Authorization: Bearer <token>
```

## 文档管理接口

### 上传文档

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求参数:**
```
file: <file>
title: "物业管理规章制度"
category: "regulation"
```

**响应:**
```json
{
  "id": 1,
  "title": "物业管理规章制度",
  "category": "regulation",
  "file_name": "规章制度.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "summary": "本文档包含...",
  "is_processed": true,
  "created_at": "2024-01-15T10:00:00"
}
```

### 获取文档列表

```http
GET /api/documents/?category=regulation&search=停车
Authorization: Bearer <token>
```

**查询参数:**
- `category`: 分类筛选
- `search`: 关键词搜索

### 语义搜索

```http
GET /api/documents/search/semantic?query=停车场规定&limit=5
Authorization: Bearer <token>
```

### 删除文档

```http
DELETE /api/documents/{document_id}
Authorization: Bearer <token>
```

## 支付管理接口

### 获取账单列表

```http
GET /api/payments/bills?status=pending&fee_type=property
Authorization: Bearer <token>
```

**查询参数:**
- `status`: pending/paid/overdue
- `fee_type`: property/water/electricity/parking

**响应:**
```json
[
  {
    "id": 1,
    "bill_number": "BILL202401001",
    "fee_type": "property",
    "amount": 1500.00,
    "late_fee": 0.00,
    "total_amount": 1500.00,
    "billing_period": "2024-01",
    "due_date": "2024-01-31",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### 发起支付

```http
POST /api/payments/pay
Authorization: Bearer <token>
```

**请求参数:**
```json
{
  "bill_id": 1,
  "payment_method": "wechat"
}
```

**响应 (微信支付):**
```json
{
  "success": true,
  "payment_params": {
    "appId": "...",
    "timeStamp": "...",
    "nonceStr": "...",
    "package": "...",
    "signType": "...",
    "paySign": "..."
  },
  "message": "请使用微信完成支付"
}
```

**响应 (支付宝):**
```json
{
  "success": true,
  "payment_url": "https://openapi.alipay.com/gateway.do?...",
  "message": "请跳转到支付宝完成支付"
}
```

## 物业项目接口

### 获取物业列表

```http
GET /api/properties/
Authorization: Bearer <token>
```

### 获取物业详情

```http
GET /api/properties/{property_id}
Authorization: Bearer <token>
```

## 错误响应

所有错误响应格式:

```json
{
  "detail": "错误描述信息"
}
```

**常见状态码:**
- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权(需要登录)
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器错误

## 完整API文档

启动后端服务后访问:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
