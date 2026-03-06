---
name: novel-agent-optimization
description: Novel Agent 项目性能优化技能。包含数据库优化、缓存策略、并发处理、监控告警。
---

# Novel Agent 性能优化

## 1. 数据库优化

### SQLite 优化
```python
# 启用 WAL 模式
conn.execute("PRAGMA journal_mode=WAL")

# 同步设置
conn.execute("PRAGMA synchronous=NORMAL")

# 缓存大小
conn.execute("PRAGMA cache_size=10000")
```

### 添加索引
```sql
CREATE INDEX idx_chapters_novel ON chapters(novel_id);
CREATE INDEX idx_chapters_num ON chapters(chapter_num);
```

## 2. 缓存策略

### 内存缓存
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_novel(novel_id):
    return db.query(novel_id)
```

### Redis 缓存
```python
import redis
cache = redis.Redis()

def get_with_cache(key, fn):
    result = cache.get(key)
    if not result:
        result = fn()
        cache.setex(key, 3600, result)
    return result
```

## 3. 并发处理

### 线程池
```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def process_chapters(chapters):
    futures = [executor.submit(write_chapter, c) for c in chapters]
    return [f.result() for f in futures]
```

### 异步队列
```python
import asyncio
from collections import deque

class TaskQueue:
    def __init__(self):
        self.queue = deque()
    
    async def put(self, task):
        self.queue.append(task)
    
    async def get(self):
        return self.queue.popleft()
```

## 4. 监控告警

### 基础指标
```python
import time
from functools import wraps

def metrics(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        duration = time.time() - start
        print(f"{fn.__name__} took {duration:.2f}s")
        return result
    return wrapper
```

### 健康检查增强
```python
@app.get("/health")
async def health():
    import psutil
    return {
        "status": "healthy",
        "memory_percent": psutil.virtual_memory().percent,
        "cpu_percent": psutil.cpu_percent(),
        "disk_percent": psutil.disk_usage('/').percent
    }
```

## 5. 日志优化

### 结构化日志
```python
from loguru import logger
import json

class StructuredLogger:
    def log(self, level, action, **kwargs):
        logger.bind(level=level, action=action, **kwargs).log(level, json.dumps(kwargs))
```

## 6. 性能问题排查

### 慢查询
```sql
EXPLAIN QUERY PLAN SELECT * FROM chapters WHERE novel_id = 1;
```

### 内存分析
```python
import tracemalloc
tracemalloc.start()
# ... code ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
```
