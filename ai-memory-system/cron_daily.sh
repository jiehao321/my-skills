#!/bin/bash
# 每日总结定时任务
# 添加到 crontab: 0 1 * * * /root/.openclaw/workspace/memory-system/cron_daily.sh >> /tmp/memory_cron.log 2>&1

cd /root/.openclaw/workspace/memory-system
python3 daily_summarize.py >> /tmp/memory_cron.log 2>&1
echo "$(date): Daily summarize completed" >> /tmp/memory_cron.log
