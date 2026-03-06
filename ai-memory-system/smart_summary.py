"""
智能总结模块 - 接入 MiniMax LLM
"""
import os
import json
import requests
import re
from memory_core import get_recent_conversations

# MiniMax API 配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimaxi.com/anthropic/v1"
MODEL = "MiniMax-M2.5"


def call_minimax(prompt: str) -> str:
    """调用 MiniMax LLM"""
    api_key = MINIMAX_API_KEY
    
    if not api_key:
        try:
            with open('/root/.openclaw/openclaw.json') as f:
                config = json.load(f)
            api_key = config.get('models',{}).get('providers',{}).get('minimax',{}).get('apiKey','')
        except:
            pass
    
    if not api_key:
        return json.dumps({"error": "未配置 API Key"})
    
    url = f"{MINIMAX_BASE_URL}/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    data = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        result = response.json()
        
        # 提取文本内容
        content = result.get("content", [])
        if content and isinstance(content, list):
            for item in content:
                if item.get("type") == "text":
                    text = item.get("text", "")
                    # 尝试提取 JSON
                    json_match = re.search(r'\{[\s\S]*\}', text)
                    if json_match:
                        return json_match.group()
                    return text
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})


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
    
    prompt = f"""分析以下中文对话，提取关键信息。

对话:
{dialog_text}

直接输出JSON，不要其他内容:
{{"summary":"一句话总结","topics":["话题1"],"decisions":["决定1"],"todos":["待办1"]}}"""

    llm_result = call_minimax(prompt)
    
    # 解析 JSON
    try:
        result = json.loads(llm_result)
    except:
        result = {"summary": llm_result[:100], "topics": [], "decisions": [], "todos": []}
    
    result["conversation_count"] = len(conversations)
    return result


def generate_knowledge_from_conversations(days: int = 7) -> list:
    """从对话中提取知识"""
    conversations = get_recent_conversations(days=days)
    
    knowledge_items = []
    seen_topics = set()
    
    for c in conversations:
        if c[4] and c[4] > 5:
            topic = c[1][:50] if c[1] else ""
            if topic and topic not in seen_topics:
                seen_topics.add(topic)
                knowledge_items.append({
                    "topic": topic,
                    "content": c[2][:200] if c[2] else ""
                })
    
    return knowledge_items


if __name__ == "__main__":
    print("=== MiniMax 智能总结测试 ===")
    result = summarize_conversations(days=1)
    print(f"\n总结结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
