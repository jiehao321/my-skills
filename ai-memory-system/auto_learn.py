"""
自动学习模块 - 每天自动学习新知识
"""
import os
import requests
from pathlib import Path
from datetime import datetime

# 学习配置
LEARNING_DIR = Path("/root/.openclaw/workspace")
DATA_DIR = Path("/root/.openclaw/workspace/memory-system/data")

# 自动学习源
LEARNING_SOURCES = [
    # GitHub 项目
    {"type": "github", "repo": "jiehao321/novel-agent", "path": "agents"},
    {"type": "github", "repo": "jiehao321/my-skills", "path": ""},
    # 技术博客 (可添加更多)
    {"type": "local", "path": "/root/.openclaw/workspace/skills"},
]


def learn_from_local_skills():
    """从本地 skills 学习"""
    skills_dir = LEARNING_DIR / "skills"
    if not skills_dir.exists():
        return []
    
    learned = []
    for skill_path in skills_dir.iterdir():
        if skill_path.is_dir():
            skill_name = skill_path.name
            readme = skill_path / "SKILL.md"
            if readme.exists():
                content = readme.read_text()[:500]  # 取前500字
                learned.append({
                    "source": f"skill:{skill_name}",
                    "content": content,
                    "date": datetime.now().isoformat()
                })
    return learned


def learn_from_project(project_dir: str):
    """从项目学习"""
    path = Path(project_dir)
    if not path.exists():
        return []
    
    learned = []
    # 读取主要 Python 文件
    for py_file in path.rglob("*.py"):
        if "node_modules" in str(py_file) or "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text()[:300]
            learned.append({
                "source": str(py_file.relative_to(path)),
                "content": content,
                "date": datetime.now().isoformat()
            })
        except:
            pass
    return learned


def daily_learning():
    """每日学习任务"""
    print("=== 开始每日学习 ===")
    
    all_learned = []
    
    # 1. 从 skills 学习
    print("📚 学习 skills...")
    skills_content = learn_from_local_skills()
    all_learned.extend(skills_content)
    print(f"   学了 {len(skills_content)} 个 skills")
    
    # 2. 从 novel-agent 学习
    print("📚 学习 novel-agent...")
    project_content = learn_from_project("/root/.openclaw/workspace/novel-agent")
    all_learned.extend(project_content[:10])  # 限制数量
    print(f"   学了 {len(project_content[:10])} 个项目文件")
    
    # 保存学习记录
    learning_log = DATA_DIR / "learning_log.json"
    import json
    existing = []
    if learning_log.exists():
        existing = json.loads(learning_log.read_text())
    
    existing.extend(all_learned)
    learning_log.write_text(json.dumps(existing[-100:], ensure_ascii=False, indent=2))
    
    print(f"✅ 今日学习完成，共 {len(all_learned)} 条")
    return all_learned


if __name__ == "__main__":
    daily_learning()
