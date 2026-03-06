"""
自我反思模块 - 分析回答质量
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/memory-system')

from memory_core import get_recent_conversations
import json
from datetime import datetime

# 回答质量评估
class ResponseQualityAnalyzer:
    """回答质量分析器"""
    
    def __init__(self):
        self.criteria = {
            "helpfulness": {"weight": 0.3, "keywords": ["帮你", "可以", "需要"]},
            "clarity": {"weight": 0.2, "keywords": ["1.", "2.", "首先", "其次"]},
            "accuracy": {"weight": 0.3, "keywords": ["正确", "是的", "没问题"]},
            "completeness": {"weight": 0.2, "keywords": ["还有", "另外", "补充"]},
        }
    
    def analyze_response(self, user_msg: str, ai_msg: str) -> dict:
        """分析单条回答质量"""
        scores = {}
        
        # 帮助性检测
        helpfulness = sum(1 for kw in self.criteria["helpfulness"]["keywords"] if kw in ai_msg)
        scores["helpfulness"] = min(helpfulness * 0.3, 1.0)
        
        # 清晰度检测
        clarity = sum(1 for kw in self.criteria["clarity"]["keywords"] if kw in ai_msg)
        scores["clarity"] = min(clarity * 0.3, 1.0)
        
        # 完整性检测
        completeness = sum(1 for kw in self.criteria["completeness"]["keywords"] if kw in ai_msg)
        scores["completeness"] = min(completeness * 0.3, 1.0)
        
        # 计算总分
        total = sum(
            scores[k] * self.criteria[k]["weight"] 
            for k in scores
        )
        
        return {
            "scores": scores,
            "total_score": round(total, 2),
            "length": len(ai_msg),
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_recent_responses(self, days: int = 1) -> dict:
        """分析最近回答"""
        conversations = get_recent_conversations(days=days)
        
        if not conversations:
            return {"summary": "无对话", "avg_score": 0}
        
        results = []
        for c in conversations:
            if c[2]:  # AI response
                result = self.analyze_response(c[1] or "", c[2])
                results.append(result)
        
        if not results:
            return {"summary": "无回答", "avg_score": 0}
        
        avg_score = sum(r["total_score"] for r in results) / len(results)
        
        # 分析改进点
        low_scores = [r for r in results if r["total_score"] < 0.5]
        
        return {
            "total_responses": len(results),
            "avg_score": round(avg_score, 2),
            "high_quality": len([r for r in results if r["total_score"] >= 0.7]),
            "needs_improvement": len(low_scores),
            "improvement_areas": self._get_improvement_suggestions(results),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_improvement_suggestions(self, results: list) -> list:
        """获取改进建议"""
        suggestions = []
        
        avg_helpfulness = sum(r["scores"]["helpfulness"] for r in results) / len(results)
        avg_clarity = sum(r["scores"]["clarity"] for r in results) / len(results)
        
        if avg_helpfulness < 0.5:
            suggestions.append("增加主动帮助性表达")
        if avg_clarity < 0.5:
            suggestions.append("使用更清晰的结构")
        
        return suggestions


def self_reflect():
    """执行自我反思"""
    analyzer = ResponseQualityAnalyzer()
    result = analyzer.analyze_recent_responses(days=1)
    
    print("=== 自我反思报告 ===")
    print(f"总回答数: {result.get('total_responses', 0)}")
    print(f"平均质量分: {result.get('avg_score', 0)}")
    print(f"高质量回答: {result.get('high_quality', 0)}")
    print(f"需改进: {result.get('needs_improvement', 0)}")
    
    if result.get("improvement_areas"):
        print(f"改进建议: {result['improvement_areas']}")
    
    return result


if __name__ == "__main__":
    self_reflect()
