#!/usr/bin/env python3
"""
每日总结脚本
自动总结对话、更新知识大纲
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/memory-system')

from memory_core import (
    init_db, get_recent_conversations, add_daily_summary, 
    get_knowledge_topics, update_knowledge_topic, generate_daily_summary
)
from datetime import datetime, timedelta
import json

def daily_summarize():
    """执行每日总结"""
    init_db()
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 获取昨天的对话
    conversations = get_recent_conversations(days=1)
    
    if not conversations:
        print("昨日无对话")
        return
    
    # 简单摘要生成（实际可接入 LLM）
    important_msgs = [c for c in conversations if c[4] > 3]
    topics = set()
    
    for c in conversations:
        if c[3]:  # tags
            for tag in c[3].split(','):
                topics.add(tag.strip())
    
    summary = f"共 {len(conversations)} 条对话"
    if important_msgs:
        summary += f"，{len(important_msgs)} 条重要"
    
    key_topics = ",".join(topics) if topics else "常规对话"
    
    # 保存每日总结
    add_daily_summary(yesterday, summary, key_topics, "")
    
    # 更新知识大纲
    update_knowledge_topic(
        f"对话记录_{yesterday}",
        summary + f"\n主题: {key_topics}"
    )
    
    print(f"✅ 每日总结完成: {yesterday}")
    print(f"   对话数: {len(conversations)}")
    print(f"   主题: {key_topics}")

def list_knowledge():
    """列出知识大纲"""
    init_db()
    topics = get_knowledge_topics()
    print("=== 知识大纲 ===")
    for topic, content, updated in topics:
        print(f"- {topic}: {content[:50]}...")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_knowledge()
    else:
        daily_summarize()
