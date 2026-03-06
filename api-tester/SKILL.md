---
name: api-tester
description: API 测试工具。快速测试 HTTP 请求，查看响应，支持 JSON 格式化输出。
---

# API Tester

快速测试 HTTP API 端点的工具。

## 基本用法

### GET 请求
```bash
# 简单 GET
curl http://localhost:8000/api/novel/1

# 带查询参数
curl "http://api.example.com/search?q=test&page=1"
```

### POST 请求
```bash
# JSON 请求
curl -X POST http://localhost:8000/api/novel/create \
  -H "Content-Type: application/json" \
  -d '{"requirement": "test", "genre": "都市"}'

# Form 请求
curl -X POST http://example.com/api \
  -d "name=value"
```

## 调试选项

```bash
# 显示完整响应
curl http://localhost:8000/api/novel/1

# 只显示 HTTP 状态码
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/novel/1

# 显示响应头
curl -I http://localhost:8000/api/novel/1

# 显示请求过程
curl -v http://localhost:8000/api/novel/1

# 超时设置
curl --connect-timeout 5 http://localhost:8000/api/novel/1
```

## JSON 处理

```bash
# 格式化输出
curl http://localhost:8000/api/novel/1 | python3 -m json.tool

# 提取字段
curl http://localhost:8000/api/novel/1 | python3 -c "import sys,json; print(json.load(sys.stdin).get('title'))"

# 管道工具 jq (如果安装)
curl http://localhost:8000/api/novel/1 | jq '.title'
```

## 常用场景

### 测试服务是否运行
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000
# 返回 200 = 正常
```

### 测试数据库是否有数据
```bash
curl http://localhost:8000/api/novels | python3 -m json.tool | head -20
```

### 测试 WebSocket
```bash
# 使用 wscat (需要安装)
npm install -g wscat
wscat -c ws://localhost:8000/ws
```

### 测试 CORS
```bash
curl -H "Origin: http://example.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://localhost:8000/api/novel/1 \
     -I
```

## 快速健康检查脚本

```bash
#!/bin/bash
# health-check.sh

BASE_URL=${1:-http://localhost:8000}

echo "=== API Health Check ==="
echo "Base URL: $BASE_URL"
echo ""

echo -n "Backend: "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/docs)
if [ "$STATUS" = "200" ]; then
    echo "✓ OK"
else
    echo "✗ Failed ($STATUS)"
fi

echo -n "Frontend: "
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✓ OK"
else
    echo "✗ Failed ($FRONTEND_STATUS)"
fi
```

## 常见错误码

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 400 | 请求错误 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
| 000 | 连接失败 (服务未启动) |
