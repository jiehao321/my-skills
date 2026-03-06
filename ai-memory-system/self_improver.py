"""
自我改进模块 - 基于 LLM 的回答质量分析与自动改进
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/memory-system')

import json
import requests
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DATA_DIR = Path("/root/.openclaw/workspace/memory-system/data")
QUALITY_FILE = DATA_DIR / "quality_analysis.json"
IMPROVEMENTS_FILE = DATA_DIR / "improvements.json"

# MiniMax 配置
MINIMAX_BASE_URL = "https://api.minimaxi.com/anthropic/v1"
MODEL = "MiniMax-M2.5"


def get_api_key():
    try:
        with open('/root/.openclaw/openclaw.json') as f:
            config = json.load(f)
        return config.get('models', {}).get('providers', {}).get('minimax', {}).get('apiKey', '')
    except:
        return ""


def call_llm(prompt: str) -> str:
    api_key = get_api_key()
    if not api_key:
        return json.dumps({"error": "No API Key"})
    
    url = f"{MINIMAX_BASE_URL}/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    try:
        response = requests.post(url, headers=headers, json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800
        }, timeout=60)
        result = response.json()
        content = result.get("content", [])
        if content:
            for item in content:
                if item.get("type") == "text":
                    return item.get("text", "")
    except Exception as e:
        return f"Error: {e}"
    return ""


class SelfImprover:
    """自我改进器"""
    
    def __init__(self):
        self.quality_history = []
        self.patterns = defaultdict(int)  # 回答模式统计
        self.improvements = []
        self.load()
    
    def load(self):
        if QUALITY_FILE.exists():
            self.quality_history = json.loads(QUALITY_FILE.read_text())
        if IMPROVEMENTS_FILE.exists():
            self.improvements = json.loads(IMPROVEMENTS_FILE.read_text())
    
    def save(self):
        QUALITY_FILE.write_text(json.dumps(self.quality_history[-100:], ensure_ascii=False))
        IMPROVEMENTS_FILE.write_text(json.dumps(self.improvements, ensure_ascii=False, indent=2))
    
    def analyze_with_llm(self, user_msg: str, ai_msg: str) -> dict:
        """用 LLM 分析回答质量"""
        prompt = f"""分析以下 AI 回答的质量。

用户问题: {user_msg}
AI回答: {ai_msg}

请从以下维度打分 (0-10) 并给出改进建议:
1. 准确性 - 回答是否正确
2. 完整性 - 是否覆盖所有要点
3. 清晰度 - 是否易于理解
4. 有用性 - 是否真正帮助用户

直接输出JSON:
{{
    "accuracy": 分数,
    "completeness": 分数,
    "clarity": 分数,
    "helpfulness": 分数,
    "total_score": 平均分,
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"]
}}"""

        result = call_llm(prompt)
        
        # 解析 JSON
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"total_score": 5, "issues": ["解析失败"], "suggestions": []}
    
    def analyze_with_rules(self, user_msg: str, ai_msg: str) -> dict:
        """基于规则的分析（快速）"""
        score = 5  # 基础分
        
        # 加分项
        if any(kw in ai_msg for kw in ["帮你", "可以", "没问题", "当然"]):
            score += 1
        if any(kw in ai_msg for kw in ["1.", "2.", "首先", "其次"]):
            score += 1
        if len(ai_msg) > 100:
            score += 1
        
        # 减分项
        if "不知道" in ai_msg or "不清楚" in ai_msg:
            score -= 1
        if len(ai_msg) < 20:
            score -= 1
        
        issues = []
        suggestions = []
        
        if score < 5:
            issues.append("回答可能不够有帮助")
            suggestions.append("增加更详细的解释")
        if len(ai_msg) < 50:
            issues.append("回答太简短")
            suggestions.append("提供更多细节")
        
        return {
            "accuracy": min(score / 10, 1),
            "completeness": min(score / 10, 1),
            "clarity": min(score / 10, 1),
            "helpfulness": min(score / 10, 1),
            "total_score": score / 10,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def record(self, user_msg: str, ai_msg: str, feedback: str = None):
        """记录并分析回答"""
        # 快速规则分析
        analysis = self.analyze_with_rules(user_msg, ai_msg)
        
        # 更新模式统计
        if any(kw in ai_msg for kw in ["1.", "2.", "3."]):
            self.patterns["structured"] += 1
        if any(kw in ai_msg for kw in ["代码", "python", "import"]):
            self.patterns["code"] += 1
        if any(kw in ai_msg for kw in ["帮你", "可以"]):
            self.patterns["helpful"] += 1
        
        # 整合分析结果
        record = {
            "timestamp": datetime.now().isoformat(),
            "user_msg": user_msg[:100],
            "ai_msg": ai_msg[:200],
            "analysis": analysis,
            "feedback": feedback
        }
        
        self.quality_history.append(record)
        
        # 提取改进建议
        for suggestion in analysis.get("suggestions", []):
            if suggestion not in self.improvements:
                self.improvements.append(suggestion)
        
        self.save()
        
        return analysis
    
    def get_stats(self) -> dict:
        """获取质量统计"""
        if not self.quality_history:
            return {"total": 0, "avg_score": 0}
        
        scores = [r["analysis"]["total_score"] for r in self.quality_history]
        avg_score = sum(scores) / len(scores)
        
        return {
            "total_responses": len(self.quality_history),
            "avg_score": round(avg_score, 2),
            "high_quality": len([s for s in scores if s >= 0.8]),
            "low_quality": len([s for s in scores if s < 0.5]),
            "patterns": dict(self.patterns),
            "improvements": self.improvements[-5:]
        }
    
    def generate_report(self) -> str:
        """生成改进报告"""
        stats = self.get_stats()
        
        report = f"""=== 自我改进报告 ===
        
总回答数: {stats.get('total_responses', 0)}
平均质量分: {stats.get('avg_score', 0)}
高质量回答: {stats.get('high_quality', 0)}
需改进回答: {stats.get('low_quality', 0)}

常用模式: {stats.get('patterns', {})}

改进建议: {stats.get('improvements', [])}
"""
        return report


# 全局实例
improver = SelfImprover()


if __name__ == "__main__":
    print("=== 自我改进测试 ===")
    
    # 模拟分析
    improver.record("如何学习编程", "建议你先学 Python，从基础语法开始。")
    improver.record("有什么项目推荐", "可以做一个博客系统，用 FastAPI + Vue。")
    
    print(improver.generate_report())
