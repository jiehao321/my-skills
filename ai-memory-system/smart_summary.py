"""
智能总结模块 - 接入 LLM 自动分析对话
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/memory-system')

from memory_core import get_recent_conversations
import json

# 模拟 LLM 调用 (实际需要接入真实 LLM)
def call_llm(prompt: str) -> str:
    """
    调用 LLM 生成总结
    这里用模板模拟，实际可接入 OpenAI / Claude / MiniMax 等
    """
    # 实际项目可以用 OpenAI API:
    # import openai
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": prompt}]
    # )
    # return response.choices[0].message.content
    
    # 简单模拟返回
    return f"【智能总结】{prompt[:50]}..."


def summarize_conversations(days: int = 1) -> dict:
    """智能总结最近对话"""
    conversations = get_recent_conversations(days=days)
    
    if not conversations:
        return {"summary": "无对话", "topics": [], "insights": []}
    
    # 构建对话摘要
    dialog_text = "\n".join([
        f"用户: {c[1][:100]}\nAI: {c[2][:100]}..." 
        for c in conversations[:10]
    ])
    
    prompt = f"""请分析以下对话，提取:
1. 主要话题
2. 关键决策
3. 待办事项
4. 重要知识点

对话内容:
{dialog_text}

请用中文总结:"""

    # 调用 LLM
    llm_summary = call_llm(prompt)
    
    # 简单解析 (实际用 LLM 返回结构化 JSON)
    topics = []
    decisions = []
    todos = []
    
    for c in conversations:
        msg = c[1] or ""
        if any(kw in msg for kw in ["记住", "重要", "学习"]):
            topics.append(msg[:30])
        if any(kw in msg for kw in ["去做", "完成", "TODO"]):
            todos.append(msg[:30])
    
    return {
        "summary": llm_summary,
        "topics": topics,
        "decisions": decisions,
        "todos": todos,
        "conversation_count": len(conversations)
    }


def generate_knowledge_from_conversations(days: int = 7) -> list:
    """从对话中提取知识"""
    conversations = get_recent_conversations(days=days)
    
    knowledge_items = []
    seen_topics = set()
    
    for c in conversations:
        # importance > 5 的是重要对话
        if c[4] and c[4] > 5:
            topic = c[1][:50] if c[1] else ""  # 用户消息作为主题
            if topic and topic not in seen_topics:
                seen_topics.add(topic)
                knowledge_items.append({
                    "topic": topic,
                    "content": c[2][:200] if c[2] else ""  # AI 回答作为内容
                })
    
    return knowledge_items


if __name__ == "__main__":
    print("=== 智能总结测试 ===")
    result = summarize_conversations(days=1)
    print(f"总结: {result}")
