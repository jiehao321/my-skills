"""
知识图谱模块 - 构建概念关系
"""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DATA_DIR = Path("/root/.openclaw/workspace/memory-system/data")
GRAPH_FILE = DATA_DIR / "knowledge_graph.json"


class KnowledgeGraph:
    """知识图谱"""
    
    def __init__(self):
        self.graph = {
            "nodes": {},  # concept -> {type, description, count}
            "edges": []   # [from, to, relation]
        }
        self.load()
    
    def load(self):
        """加载图谱"""
        if GRAPH_FILE.exists():
            self.graph = json.loads(GRAPH_FILE.read_text())
    
    def save(self):
        """保存图谱"""
        GRAPH_FILE.write_text(json.dumps(self.graph, ensure_ascii=False, indent=2))
    
    def add_concept(self, concept: str, concept_type: str = "general", description: str = ""):
        """添加概念"""
        if concept not in self.graph["nodes"]:
            self.graph["nodes"][concept] = {
                "type": concept_type,
                "description": description,
                "count": 0,
                "created": datetime.now().isoformat()
            }
        self.graph["nodes"][concept]["count"] += 1
    
    def add_relation(self, from_concept: str, to_concept: str, relation: str = "related"):
        """添加关系"""
        # 确保节点存在
        self.add_concept(from_concept)
        self.add_concept(to_concept)
        
        # 添加边
        edge = [from_concept, to_concept, relation]
        if edge not in self.graph["edges"]:
            self.graph["edges"].append(edge)
    
    def build_from_learning(self, learned_items: list):
        """从学习内容构建图谱"""
        # 预定义关系
        relations = {
            "skill": {"related_to": ["novel-agent", "AI", "工具"]},
            "novel-agent": {"uses": ["FastAPI", "Next.js", "Python"]},
            "AI": {"includes": ["LLM", "记忆系统", "Agent"]},
            "memory": {"related_to": ["知识图谱", "向量数据库"]},
        }
        
        for item in learned_items:
            source = item.get("source", "")
            
            # 根据来源添加概念
            if source.startswith("skill:"):
                skill_name = source.replace("skill:", "")
                self.add_concept(skill_name, "skill", f"技能: {skill_name}")
                
                # 添加预定义关系
                for related in relations.get("skill", {}).get("related_to", []):
                    self.add_relation(skill_name, related, "related_to")
            
            elif source.endswith(".py"):
                self.add_concept(source, "code", f"代码文件: {source}")
        
        self.save()
        print(f"✅ 知识图谱已更新: {len(self.graph['nodes'])} 个概念, {len(self.graph['edges'])} 条关系")
    
    def get_related(self, concept: str) -> list:
        """获取相关概念"""
        related = []
        for edge in self.graph["edges"]:
            if concept in edge[:2]:
                related.append({
                    "concept": edge[0] if edge[1] == concept else edge[1],
                    "relation": edge[2]
                })
        return related
    
    def get_stats(self) -> dict:
        """获取图谱统计"""
        return {
            "nodes": len(self.graph["nodes"]),
            "edges": len(self.graph["edges"]),
            "top_concepts": sorted(
                [(k, v["count"]) for k, v in self.graph["nodes"].items()],
                key=lambda x: -x[1]
            )[:10]
        }


if __name__ == "__main__":
    # 测试
    print("=== 知识图谱测试 ===")
    
    graph = KnowledgeGraph()
    
    # 添加测试数据
    graph.add_concept("ai-memory-system", "skill", "AI记忆系统")
    graph.add_concept("novel-agent", "project", "AI小说创作系统")
    graph.add_concept("ChromaDB", "tool", "向量数据库")
    
    graph.add_relation("ai-memory-system", "novel-agent", "used_in")
    graph.add_relation("ai-memory-system", "ChromaDB", "uses")
    
    graph.save()
    
    print(f"图谱统计: {graph.get_stats()}")
    print(f"相关概念: {graph.get_related('ai-memory-system')}")
