"""
知识图谱模块 - 支持 LLM 自动提取实体和关系
"""
import json
import re
import requests
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("/root/.openclaw/workspace/memory-system/data")
GRAPH_FILE = DATA_DIR / "knowledge_graph.json"

# MiniMax 配置
MINIMAX_BASE_URL = "https://api.minimaxi.com/anthropic/v1"
MODEL = "MiniMax-M2.5"


def get_api_key():
    """获取 API Key"""
    try:
        import os
        key = os.getenv("MINIMAX_API_KEY")
        if key:
            return key
        with open('/root/.openclaw/openclaw.json') as f:
            config = json.load(f)
        return config.get('models', {}).get('providers', {}).get('minimax', {}).get('apiKey', '')
    except:
        return ""


def call_llm(prompt: str) -> str:
    """调用 MiniMax LLM"""
    api_key = get_api_key()
    if not api_key:
        return json.dumps({"error": "No API Key"})
    
    url = f"{MINIMAX_BASE_URL}/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    messages = [{"role": "user", "content": prompt}]
    data = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        result = response.json()
        content = result.get("content", [])
        if content and isinstance(content, list):
            for item in content:
                if item.get("type") == "text":
                    return item.get("text", "")
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})


def extract_entities_and_relations(text: str) -> dict:
    """
    用 LLM 从文本中提取实体和关系
    """
    prompt = f"""从以下文本提取实体和关系。

文本:
{text}

请直接输出JSON，不要其他内容:
{{
    "entities": [
        {{"name": "实体名", "type": "类型"}}
    ],
    "relations": [
        {{"from": "A", "to": "B", "relation": "关系"}}
    ]
}}"""

    result = call_llm(prompt)
    
    # 解析 JSON
    try:
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    
    return {"entities": [], "relations": []}


class KnowledgeGraph:
    """知识图谱"""
    
    def __init__(self):
        self.graph = {
            "nodes": {},
            "edges": []
        }
        self.load()
    
    def load(self):
        if GRAPH_FILE.exists():
            self.graph = json.loads(GRAPH_FILE.read_text())
    
    def save(self):
        GRAPH_FILE.write_text(json.dumps(self.graph, ensure_ascii=False, indent=2))
    
    def add_concept(self, concept: str, concept_type: str = "general", description: str = ""):
        if concept not in self.graph["nodes"]:
            self.graph["nodes"][concept] = {
                "type": concept_type,
                "description": description,
                "count": 0,
                "created": datetime.now().isoformat()
            }
        self.graph["nodes"][concept]["count"] += 1
    
    def add_relation(self, from_concept: str, to_concept: str, relation: str = "related"):
        self.add_concept(from_concept)
        self.add_concept(to_concept)
        
        edge = [from_concept, to_concept, relation]
        if edge not in self.graph["edges"]:
            self.graph["edges"].append(edge)
    
    def build_from_text(self, text: str):
        """从文本自动构建图谱"""
        extraction = extract_entities_and_relations(text)
        
        # 添加实体
        for entity in extraction.get("entities", []):
            self.add_concept(
                entity.get("name", ""),
                entity.get("type", "general"),
                ""
            )
        
        # 添加关系
        for rel in extraction.get("relations", []):
            self.add_relation(
                rel.get("from", ""),
                rel.get("to", ""),
                rel.get("relation", "related")
            )
        
        self.save()
        return extraction
    
    def build_from_learning(self, learned_items: list):
        relations = {
            "skill": {"related_to": ["novel-agent", "AI", "工具"]},
            "novel-agent": {"uses": ["FastAPI", "Next.js", "Python"]},
            "AI": {"includes": ["LLM", "记忆系统", "Agent"]},
            "memory": {"related_to": ["知识图谱", "向量数据库"]},
        }
        
        for item in learned_items:
            source = item.get("source", "")
            
            if source.startswith("skill:"):
                skill_name = source.replace("skill:", "")
                self.add_concept(skill_name, "skill", f"技能: {skill_name}")
                
                for related in relations.get("skill", {}).get("related_to", []):
                    self.add_relation(skill_name, related, "related_to")
            
            elif source.endswith(".py"):
                self.add_concept(source, "code", f"代码文件: {source}")
        
        self.save()
    
    def get_related(self, concept: str) -> list:
        related = []
        for edge in self.graph["edges"]:
            if concept in edge[:2]:
                related.append({
                    "concept": edge[0] if edge[1] == concept else edge[1],
                    "relation": edge[2]
                })
        return related
    
    def get_stats(self) -> dict:
        return {
            "nodes": len(self.graph["nodes"]),
            "edges": len(self.graph["edges"]),
            "top_concepts": sorted(
                [(k, v["count"]) for k, v in self.graph["nodes"].items()],
                key=lambda x: -x[1]
            )[:10]
        }


if __name__ == "__main__":
    print("=== LLM 自动提取测试 ===")
    
    graph = KnowledgeGraph()
    
    # 测试文本
    test_text = "novel-agent 是一个 AI 小说创作系统，使用 FastAPI 后端和 Next.js 前端开发。它使用 ChromaDB 存储向量数据。"
    
    print(f"原文: {test_text}")
    print("\n提取中...")
    
    result = graph.build_from_text(test_text)
    
    print(f"\n提取结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print(f"\n图谱统计: {graph.get_stats()}")
