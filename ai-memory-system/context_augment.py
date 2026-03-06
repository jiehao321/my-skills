"""
上下文增强 - 回答前自动搜索记忆
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/memory-system')

from semantic_search import search_knowledge, search_conversations
from memory_core import get_recent_conversations
import json

# 记忆上下文缓存
CONTEXT_CACHE = {
    "last_query": "",
    "last_result": {}
}


def augment_context(user_message: str) -> str:
    """
    为回答增强上下文
    搜索相关记忆并返回上下文提示
    """
    # 1. 搜索知识库
    knowledge_results = search_knowledge(user_message, n_results=3)
    
    # 2. 搜索对话历史
    conversation_results = search_conversations(user_message, n_results=3)
    
    # 3. 构建上下文
    context_parts = []
    
    if knowledge_results.get("documents") and knowledge_results["documents"][0]:
        context_parts.append("【相关知识】")
        for i, doc in enumerate(knowledge_results["documents"][0]):
            context_parts.append(f"- {doc[:100]}")
    
    if conversation_results.get("documents") and conversation_results["documents"][0]:
        context_parts.append("【相关对话】")
        for i, doc in enumerate(conversation_results["documents"][0][:2]):
            context_parts.append(f"- {doc[:80]}")
    
    if context_parts:
        context = "\n".join(context_parts)
        print(f"🔍 上下文增强: 找到 {len(context_parts)} 条相关信息")
        return context
    
    return ""


def get_recent_context_summary() -> str:
    """获取最近对话摘要"""
    recent = get_recent_conversations(days=1, limit=5)
    
    if not recent:
        return "无最近对话"
    
    summary = "【今日对话】\n"
    for c in recent:
        summary += f"- 用户: {c[1][:50]}...\n"
    
    return summary


def suggest_skills(user_message: str) -> list:
    """
    根据用户消息推荐相关 skills
    """
    # 关键词匹配
    keywords_to_skills = {
        "代码": ["code-review-assistant", "novel-agent-manager"],
        "api": ["api-tester", "novel-agent-manager"],
        "测试": ["api-tester"],
        "管理": ["novel-agent-manager"],
        "写作": ["novel-writer", "chinese-novelist"],
        "学习": ["ai-memory-system"],
        "记忆": ["ai-memory-system"],
        "GitHub": ["github"],
        "部署": ["tencentcloud-lighthouse-skill"],
    }
    
    suggestions = []
    msg_lower = user_message.lower()
    
    for keyword, skills in keywords_to_skills.items():
        if keyword in msg_lower:
            suggestions.extend(skills)
    
    # 去重
    return list(set(suggestions))[:3]


if __name__ == "__main__":
    # 测试
    print("=== 上下文增强测试 ===")
    
    # 测试搜索
    context = augment_context("我想管理 novel-agent 服务")
    print(f"\n上下文:\n{context}")
    
    # 测试技能推荐
    skills = suggest_skills("我想测试API")
    print(f"\n推荐技能: {skills}")
