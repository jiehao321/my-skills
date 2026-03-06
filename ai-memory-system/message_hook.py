"""
消息 Hook - 自动记录对话
拦截发送的消息并存储到数据库
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/memory-system')

from memory_core import add_conversation
from datetime import datetime

# 简易 Hook 实现
class MessageHook:
    def __init__(self):
        self.last_user_msg = ""
        self.enabled = True
    
    def on_user_message(self, message: str):
        """用户消息 hook"""
        self.last_user_msg = message
    
    def on_ai_response(self, response: str, channel: str = "feishu"):
        """AI 回复 hook - 自动记录对话"""
        if not self.enabled:
            return
        
        if self.last_user_msg and response:
            # 简单判断重要性
            importance = 5
            if any(kw in response for kw in ["记住", "重要", "学习", "优化"]):
                importance = 8
            
            add_conversation(
                user_msg=self.last_user_msg,
                ai_msg=response,
                channel=channel,
                importance=importance
            )
            print(f"✅ 对话已记录: {self.last_user_msg[:30]}...")
            
            # 清空缓存
            self.last_user_msg = ""

# 全局 hook 实例
message_hook = MessageHook()

# 便捷函数
def record_user_msg(message: str):
    """记录用户消息"""
    message_hook.on_user_message(message)

def record_ai_response(response: str, channel: str = "feishu"):
    """记录 AI 回复"""
    message_hook.on_ai_response(response, channel)
