"""
Memory System - 对话记忆与知识管理
自动记录对话、生成摘要、构建知识大纲
"""
import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "conversations.db"

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            channel TEXT,
            user_message TEXT,
            ai_response TEXT,
            tags TEXT,
            importance INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            summary TEXT,
            key_topics TEXT,
            decisions TEXT,
            created_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS knowledge大纲 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            content TEXT,
            source_date TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_conversation(user_msg: str, ai_msg: str, channel: str = "feishu", tags: str = "", importance: int = 0):
    """记录对话"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO conversations (timestamp, channel, user_message, ai_response, tags, importance)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), channel, user_msg, ai_msg, tags, importance))
    conn.commit()
    conn.close()

def get_recent_conversations(days: int = 7, limit: int = 100):
    """获取最近对话"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    since = (datetime.now() - timedelta(days=days)).isoformat()
    c.execute('''
        SELECT timestamp, user_message, ai_response, tags, importance
        FROM conversations
        WHERE timestamp > ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (since, limit))
    results = c.fetchall()
    conn.close()
    return results

def add_daily_summary(date: str, summary: str, key_topics: str = "", decisions: str = ""):
    """添加每日总结"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO daily_summaries (date, summary, key_topics, decisions, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, summary, key_topics, decisions, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_knowledge_topics():
    """获取知识大纲主题"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT topic, content, updated_at FROM knowledge大纲 ORDER BY updated_at DESC')
    results = c.fetchall()
    conn.close()
    return results

def update_knowledge_topic(topic: str, content: str):
    """更新知识主题"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO knowledge大纲 (topic, content, updated_at)
        VALUES (?, ?, ?)
    ''', (topic, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def generate_daily_summary(days: int = 1) -> str:
    """生成每日摘要（可接入 LLM 扩展）"""
    conversations = get_recent_conversations(days=days)
    if not conversations:
        return "无对话记录"
    
    user_msgs = [c[1] for c in conversations if c[1]]
    important = [c for c in conversations if c[4] > 5]  # importance > 5
    
    summary = f"过去{days}天共 {len(conversations)} 条对话"
    if important:
        summary += f"，其中 {len(important)} 条重要对话"
    
    return summary

if __name__ == "__main__":
    init_db()
    print(f"Memory System 初始化完成: {DB_PATH}")
