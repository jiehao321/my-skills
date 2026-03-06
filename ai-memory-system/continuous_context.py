"""
连续理解模块 - 多轮对话上下文管理
利用 ChromaDB 实现语义级别的上下文追踪
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/memory-system')

import chromadb
from chromadb.config import Settings
from pathlib import Path
import json
from datetime import datetime, timedelta

DATA_DIR = Path("/root/.openclaw/workspace/memory-system/data")
CHROMA_PATH = DATA_DIR / "context_chroma"

# 初始化 ChromaDB
client = chromadb.PersistentClient(path=str(CHROMA_PATH))
context_collection = client.get_or_create_collection(
    name="conversation_context",
    metadata={"description": "对话上下文"}
)


class ConversationContext:
    """连续对话上下文管理器"""
    
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.current_session = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_turn(self, user_msg: str, ai_msg: str):
        """添加一轮对话"""
        turn = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "user": user_msg,
            "ai": ai_msg
        }
        self.current_session.append(turn)
        
        # 存入向量库
        context_text = f"用户: {user_msg}\nAI: {ai_msg}"
        context_collection.add(
            documents=[context_text],
            ids=[f"{self.session_id}_{len(self.current_session)}"],
            metadatas=[{
                "session_id": self.session_id,
                "turn": len(self.current_session),
                "timestamp": turn["timestamp"]
            }]
        )
        
        # 保持最近轮次
        if len(self.current_session) > self.max_turns:
            self.current_session = self.current_session[-self.max_turns:]
    
    def get_related_context(self, query: str, n: int = 5) -> list:
        """获取与当前查询相关的上下文"""
        results = context_collection.query(
            query_texts=[query],
            n_results=n,
            where={"session_id": self.session_id}
        )
        
        context = []
        if results.get("documents") and results["documents"][0]:
            for doc in results["documents"][0]:
                context.append(doc)
        
        return context
    
    def resolve_reference(self, query: str) -> str:
        """解析代词引用（如'它''那个'）"""
        # 简单实现：获取最近对话
        recent = self.current_session[-3:] if self.current_session else []
        
        resolved = ""
        for turn in recent:
            resolved += f"用户: {turn['user']}\nAI: {turn['ai']}\n"
        
        return resolved
    
    def get_topic(self) -> str:
        """获取当前话题"""
        if not self.current_session:
            return ""
        
        # 简单：从最近用户消息提取关键词
        recent_msg = self.current_session[-1].get("user", "")
        
        # 常见话题关键词
        topics = {
            "代码": ["代码", "编程", "Python", "API"],
            "学习": ["学习", "优化", "提升"],
            "项目": ["项目", "novel-agent", "skill"],
            "记忆": ["记忆", "知识", "图谱"]
        }
        
        for topic, keywords in topics.items():
            if any(kw in recent_msg for kw in keywords):
                return topic
        
        return "未知"
    
    def summarize_session(self) -> dict:
        """总结当前会话"""
        if not self.current_session:
            return {"summary": "无对话", "topic": "", "turns": 0}
        
        return {
            "session_id": self.session_id,
            "topic": self.get_topic(),
            "turns": len(self.current_session),
            "first_user_msg": self.current_session[0].get("user", ""),
            "last_user_msg": self.current_session[-1].get("user", ""),
            "start_time": self.current_session[0].get("timestamp", ""),
            "end_time": self.current_session[-1].get("timestamp", "")
        }


# 全局实例
context_manager = ConversationContext()


if __name__ == "__main__":
    print("=== 连续理解测试 ===")
    
    # 模拟对话
    context_manager.add_turn("我想学习怎么做记忆系统", "记忆系统可以用 SQLite + ChromaDB 实现")
    context_manager.add_turn("那如何自动学习呢", "可以设置每日 cron 任务自动执行学习脚本")
    context_manager.add_turn("再接入 LLM 呢", "可以接入 MiniMax API 实现智能总结")
    
    # 测试上下文获取
    print("\n📋 当前会话总结:")
    print(json.dumps(context_manager.summarize_session(), ensure_ascii=False, indent=2))
    
    # 测试上下文检索
    print("\n🔍 搜索相关上下文 (关于 cron):")
    related = context_manager.get_related_context("自动学习 cron")
    for c in related:
        print(f"- {c[:50]}...")
