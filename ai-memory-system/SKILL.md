---
name: ai-memory-system
description: AI 记忆系统。记录对话、每日总结、构建知识大纲。自动记录会话并生成知识库。
---

# AI Memory System

自动记录对话、每日总结、构建知识大纲的系统。

## 系统架构

```
对话输入 → SQLite存储 → 每日总结 → 知识大纲
              ↓
         向量/标签索引
```

## 组件

- `memory_core.py` - 核心数据库操作
- `daily_summarize.py` - 每日总结脚本
- `cron_daily.sh` - 定时任务脚本

## 使用方法

### 1. 初始化数据库
```bash
cd /root/.openclaw/workspace/memory-system
python3 memory_core.py
```

### 2. 记录对话
```python
from memory_core import add_conversation

add_conversation(
    user_msg="用户消息",
    ai_msg="AI回复",
    channel="feishu",
    tags="重要,项目A",
    importance=5
)
```

### 3. 每日总结
```bash
python3 daily_summarize.py
```

### 4. 查看知识大纲
```bash
python3 daily_summarize.py list
```

## 设置每日自动总结

```bash
# 添加定时任务 (每天凌晨1点)
crontab -e
# 添加行: 0 1 * * * /root/.openclaw/workspace/memory-system/cron_daily.sh
```

## 数据位置

- 数据库: `/root/.openclaw/workspace/memory-system/data/conversations.db`
- 日志: `/tmp/memory_cron.log`

## 可扩展

当前使用 SQLite，可升级为:
- ChromaDB (向量存储)
- 接入 LLM 进行智能摘要
- 添加语义搜索
