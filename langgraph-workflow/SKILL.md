---
name: langgraph-workflow
description: LangGraph 工作流编排技能。包含状态管理、节点设计、边控制、异常处理。
---

# LangGraph 工作流编排

## 1. 基础概念

### State 定义
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: list
    context: dict
    next_step: str
```

### 节点函数
```python
def node_function(state: AgentState) -> AgentState:
    # 处理逻辑
    return {"messages": [...], "next_step": "next_node"}
```

### 边定义
```python
from langgraph.graph import add_edge, add_conditional_edges

# 固定边
graph.add_edge("node_a", "node_b")

# 条件边
def should_continue(state):
    if state.get("result"):
        return "end"
    return "continue"

graph.add_conditional_edges(
    "node_a",
    should_continue,
    {"end": END, "continue": "node_b"}
)
```

## 2. 完整示例

### Agent Pipeline
```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

class PipelineState(TypedDict):
    requirement: str
    outline: dict
    content: str
    review_result: dict
    status: str

llm = ChatOpenAI(model="gpt-4")

def planning_node(state: PipelineState) -> PipelineState:
    """规划节点"""
    prompt = f"根据需求创建大纲: {state['requirement']}"
    outline = llm.invoke(prompt)
    return {"outline": outline, "status": "planning"}

def writing_node(state: PipelineState) -> PipelineState:
    """写作节点"""
    prompt = f"根据大纲写作: {state['outline']}"
    content = llm.invoke(prompt)
    return {"content": content, "status": "writing"}

def review_node(state: PipelineState) -> PipelineState:
    """审核节点"""
    prompt = f"审核内容: {state['content']}"
    result = llm.invoke(prompt)
    return {"review_result": result, "status": "reviewing"}

# 构建图
graph = StateGraph(PipelineState)
graph.add_node("planning", planning_node)
graph.add_node("writing", writing_node)
graph.add_node("review", review_node)

graph.set_entry_point("planning")
graph.add_edge("planning", "writing")
graph.add_edge("writing", "review")
graph.add_edge("review", END)

app = graph.compile()
```

## 3. 状态管理

### 持久化状态
```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string(":memory:")
graph = graph.compile(checkpointer=checkpointer)

# 保存检查点
config = {"configurable": {"thread_id": "1"}}
graph.invoke(input, config)
```

### 内存状态
```python
def with_memory(state: AgentState) -> AgentState:
    # 读取历史
    memory = state.get("memory", [])
    # 添加当前
    memory.append(state["current"])
    return {"memory": memory}
```

## 4. 异常处理

### 重试机制
```python
from langgraph.errors import NodeInterrupt

def safe_node(state: AgentState) -> AgentState:
    try:
        return normal_process(state)
    except Exception as e:
        # 记录错误
        state["errors"].append(str(e))
        return {"status": "error", "error": str(e)}
```

### 降级处理
```python
def fallback_node(state: AgentState) -> AgentState:
    """降级处理"""
    return {
        "content": "抱歉，处理失败，请稍后重试",
        "status": "fallback"
    }
```

## 5. 并发处理

### 并行节点
```python
from langgraph.graph import Branch

# 并行执行多个任务
graph.add_node("task_a", task_a_node)
graph.add_node("task_b", task_b_node)

# 收集结果
def collect_results(state: AgentState) -> AgentState:
    return {"results": [state["a"], state["b"]]}

graph.add_node("collect", collect_results)
graph.add_edge("task_a", "collect")
graph.add_edge("task_b", "collect")
```

## 6. 监控调试

### 中间件
```python
class DebugMiddleware:
    def __call__(self, state):
        print(f"Entering: {state}")
        result = self.next(state)
        print(f"Exiting: {result}")
        return result
```

### 可视化
```python
# 生成图片
from langgraph.visualizer import visualize

graph = visualize(app)
graph.draw_mermaid_png()
```
