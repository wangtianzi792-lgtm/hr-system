#!/bin/bash
# 每日记忆同步到GitHub
# 由 launchd 每天8:00触发，也可手动调用

REPO="/Users/jiuhua/HR系统"
MEMORY_FILE="记忆/hermes-agent-memories.md"
LOG="/Users/jiuhua/HR系统/记忆/sync.log"

cd "$REPO" || exit 1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查更新..." >> "$LOG"

# 拉取远程最新
git pull origin main --quiet 2>>"$LOG"

# 检查是否有变更
if git diff --quiet && git diff --cached --quiet; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 无变更，跳过" >> "$LOG"
    exit 0
fi

# 提交并推送
git add "$MEMORY_FILE"
git commit -m "记忆同步 $(date '+%Y-%m-%d %H:%M')" 2>>"$LOG"
git push origin main >> "$LOG" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 推送完成" >> "$LOG"
