"""
初始化知识库 - 将重要信息导入向量库
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/memory-system')

from semantic_search import add_knowledge

# 重要知识
knowledge_items = [
    ("GitHub账号", "用户名 jiehao321, Token [已隐藏]"),
    ("项目 novel-agent", "AI小说创作系统，包含后端 FastAPI 和前端 Next.js"),
    ("AI记忆系统", "自动记录对话、每日总结、构建知识大纲的系统，包含 SQLite 存储和 ChromaDB 向量搜索"),
    ("Skills", "自主生成的技能：novel-agent-manager, api-tester, code-review-assistant, ai-memory-system"),
    ("用户偏好", "喜欢主动学习的AI，重视记忆系统优化，偏好程序编码方向"),
    ("学习方向", "程序编码：Python, JavaScript, AI/ML，学习优秀架构模式"),
]

print("=== 初始化知识库 ===")
for topic, content in knowledge_items:
    add_knowledge(topic, content)
    print(f"✅ 添加: {topic}")

print(f"\n共添加 {len(knowledge_items)} 条知识")
