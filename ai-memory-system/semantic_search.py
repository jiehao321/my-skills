"""
语义搜索模块 - 基于 ChromaDB 向量存储
支持语义相似度搜索
"""
import chromadb
from chromadb.config import Settings
from pathlib import Path
import os

# 初始化 ChromaDB
DATA_DIR = Path(__file__).parent / "data"
CHROMA_PATH = DATA_DIR / "chroma_db"

# 持久化客户端
client = chromadb.PersistentClient(path=str(CHROMA_PATH))

# 对话集合
conversations_collection = client.get_or_create_collection(
    name="conversations",
    metadata={"description": "AI 对话记录"}
)

# 知识库集合
knowledge_collection = client.get_or_create_collection(
    name="knowledge",
    metadata={"description": "知识大纲"}
)


def add_conversation_embedding(conversation_id: int, user_msg: str, ai_msg: str):
    """添加对话到向量库"""
    text = f"用户: {user_msg}\nAI: {ai_msg}"
    conversations_collection.add(
        documents=[text],
        ids=[f"conv_{conversation_id}"],
        metadatas=[{"conversation_id": conversation_id}]
    )


def search_conversations(query: str, n_results: int = 5):
    """语义搜索对话"""
    results = conversations_collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results


def add_knowledge(topic: str, content: str):
    """添加知识到向量库"""
    knowledge_collection.add(
        documents=[content],
        ids=[f"topic_{topic.replace(' ', '_')}"],
        metadatas=[{"topic": topic}]
    )


def search_knowledge(query: str, n_results: int = 3):
    """语义搜索知识"""
    results = knowledge_collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results


def get_all_knowledge():
    """获取所有知识"""
    return knowledge_collection.get()


if __name__ == "__main__":
    # 测试
    print("=== 语义搜索测试 ===")
    
    # 添加测试知识
    add_knowledge(
        "GitHub账号",
        "用户名 jiehao321, Token [已隐藏]"
    )
    add_knowledge(
        "项目 novel-agent",
        "AI小说创作系统，包含后端 FastAPI 和前端 Next.js"
    )
    
    # 搜索
    results = search_knowledge("GitHub")
    print(f"搜索 'GitHub': {results}")
    
    print("✅ ChromaDB 语义搜索初始化完成")
