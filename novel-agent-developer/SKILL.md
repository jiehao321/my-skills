---
name: novel-agent-developer
description: Novel Agent 项目开发技能。包含项目结构、代码规范、优化建议、常见问题解决。
---

# Novel Agent Developer

开发和管理 Novel Agent 项目的技能。

## 项目结构

```
novel-agent/
├── agents/              # Agent 核心
│   ├── base.py        # Agent 基类
│   ├── pipeline.py    # 工作流
│   ├── llm_client.py  # LLM 调用
│   ├── prompts.py     # Prompt 模板
│   ├── retry.py       # 重试机制
│   ├── planner/       # 10 个规划 Agent
│   ├── writer/        # 10 个写作 Agent
│   ├── reviewer/      # 10 个审核 Agent
│   └── memory/        # 记忆层
├── backend/           # FastAPI 后端
├── frontend/          # Next.js 前端
└── requirements.txt   # Python 依赖
```

## 常用命令

### 启动后端
```bash
cd novel-agent
PYTHONPATH=. python3 backend/main.py
# 或
python -m uvicorn backend.main:app --reload --port 8000
```

### 启动前端
```bash
cd novel-agent/frontend
npm run dev
```

### 安装依赖
```bash
pip install -r requirements.txt
cd frontend && npm install
```

## Agent 设计模式

### 1. BaseAgent 基类
```python
from agents.base import BaseAgent, AgentConfig, AgentResponse

class MyAgent(BaseAgent):
    def run(self, input_data, context) -> AgentResponse:
        # 实现逻辑
        return AgentResponse(success=True, data={})
```

### 2. LLM 调用
```python
from agents.llm_client import LLMClient

llm = LLMClient(provider="openai", model="gpt-4")
response = llm.chat(prompt)
```

### 3. Pipeline 工作流
```python
from agents.pipeline import NovelAgentPipeline

pipeline = NovelAgentPipeline(use_mock=True)
novel = pipeline.create_novel("需求", "都市")
```

## 优化建议

### 1. 健康检查增强
```python
@app.get("/health")
async def health():
    import psutil
    return {
        "status": "healthy",
        "memory": psutil.virtual_memory().percent
    }
```

### 2. 添加日志
```python
from loguru import logger
logger.info("Action performed")
```

### 3. 添加监控
```python
# 使用 prometheus_client
from prometheus_client import Counter, Histogram
request_count = Counter('requests_total', 'Total requests')
```

## 常见问题

### ModuleNotFoundError
```bash
# 设置 PYTHONPATH
export PYTHONPATH=/path/to/novel-agent
```

### 前端无法连接后端
```bash
# 检查 CORS 配置
# backend/main.py 中已配置允许所有 origins
```

### 数据库锁定
```bash
# SQLite 并发写入问题
# 建议生产环境使用 PostgreSQL
```
