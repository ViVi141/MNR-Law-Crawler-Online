#!/bin/sh
# 在 PostgreSQL 初始化完成后保存密码到持久化文件
# 这个脚本会被 docker-entrypoint-initdb.d/ 执行

PGDATA_DIR="${PGDATA:-/var/lib/postgresql/data}"
PASSWORD_FILE="/var/lib/postgresql/.postgres_password"

if [ -n "$POSTGRES_PASSWORD" ] && [ "$POSTGRES_PASSWORD" != "mnr_password" ]; then
    if echo "$POSTGRES_PASSWORD" > "$PASSWORD_FILE" 2>/dev/null; then
        chmod 600 "$PASSWORD_FILE" 2>/dev/null || true
        echo "✅ [数据库] 已将密码保存到持久化文件: $PASSWORD_FILE" >&2
    fi
fi
