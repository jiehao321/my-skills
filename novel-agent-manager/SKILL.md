---
name: novel-agent-manager
description: 启动、管理、测试 Novel Agent 前后端服务。包含启动命令、端口配置、API 测试、常见问题排查。
---

# Novel Agent Manager

管理 Novel Agent 前后端服务的技能。

## 快速启动

### 后端服务
```bash
cd /root/.openclaw/workspace/novel-agent
PYTHONPATH=/root/.openclaw/workspace/novel-agent python3 backend/main.py
```
- 默认端口: 8000
- API 文档: http://localhost:8000/docs

### 前端服务
```bash
cd /root/.openclaw/workspace/novel-agent/frontend
PORT=8080 npm run start
```
- 默认端口: 3000
- 可通过 PORT 环境变量指定端口

## 常用命令

### 启动服务
```bash
# 后端 (端口 8000)
cd /root/.openclaw/workspace/novel-agent && PYTHONPATH=/root/.openclaw/workspace/novel-agent nohup python3 backend/main.py > /tmp/novel-agent-backend.log 2>&1 &

# 前端 (端口 8080)
cd /root/.openclaw/workspace/novel-agent/frontend && PORT=8080 nohup npm run start > /tmp/novel-agent-frontend.log 2>&1 &
```

### 停止服务
```bash
pkill -f "python3.*main.py"
pkill -f "next start"
```

### 检查服务状态
```bash
# 检查端口
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/novel/1/chapter/1
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080

# 检查进程
ps aux | grep -E "uvicorn|next" | grep -v grep
```

### 查看日志
```bash
tail -f /tmp/novel-agent-backend.log
tail -f /tmp/novel-agent-frontend.log
```

## IP 地址

- 内网 IP: `hostname -I | awk '{print $1}'`
- 公网 IP: `curl -s ifconfig.me`

## API 测试示例

```bash
# 创建小说
curl -X POST http://localhost:8000/api/novel/create \
  -H "Content-Type: application/json" \
  -d '{"requirement": "都市修仙", "genre": "仙侠", "use_mock": true}'

# 获取小说
curl http://localhost:8000/api/novel/1

# 写章节
curl -X POST http://localhost:8000/api/novel/1/chapter/1/write

# 审核章节
curl -X POST http://localhost:8000/api/novel/1/chapter/1/review
```

## 常见问题

### EADDRINUSE: address already in use
```bash
# 查找占用端口的进程
lsof -i :8080
# 杀掉进程
kill <PID>
```

### ModuleNotFoundError: No module named 'agents'
```bash
# 设置 PYTHONPATH
export PYTHONPATH=/root/.openclaw/workspace/novel-agent
```

### 前端无法访问后端 API
检查后端是否运行:
```bash
curl http://localhost:8000/docs
```

## 项目结构

```
novel-agent/
├── backend/
│   ├── main.py          # FastAPI 主入口
│   ├── websocket.py     # WebSocket 处理
│   ├── response.py     # 响应格式化
│   └── vector_store.py # 向量存储
├── frontend/            # Next.js 前端
│   ├── app/            # 页面组件
│   └── lib/api.ts     # API 客户端
├── agents/             # Agent 核心逻辑
│   ├── writer/         # 写作 Agent
│   ├── reviewer/       # 审核 Agent
│   ├── planner/        # 规划 Agent
│   └── pipeline.py     # 工作流
└── novel_agent.db      # SQLite 数据库
```
