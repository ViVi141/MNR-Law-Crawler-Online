# PostgreSQL 18
FROM postgres:18-alpine

# 配置 Alpine 镜像源（使用清华大学镜像，加速下载）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

# 安装 Python3 用于生成随机密码
RUN apk add --no-cache python3

# 复制包装脚本并设置为 entrypoint
# 注意：构建上下文是 ./database，所以这里直接使用文件名
COPY docker-entrypoint-wrapper.sh /usr/local/bin/docker-entrypoint-wrapper.sh

# 设置执行权限并验证文件（简化验证逻辑，避免 Alpine 中缺少命令导致失败）
RUN chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh && \
    [ -f /usr/local/bin/docker-entrypoint-wrapper.sh ] && \
    [ -x /usr/local/bin/docker-entrypoint-wrapper.sh ] && \
    head -n 1 /usr/local/bin/docker-entrypoint-wrapper.sh | grep -q "#!/bin/sh" && \
    echo "✅ 验证通过: 文件存在且格式正确"

# 确保扩展目录权限正确
RUN chmod -R 755 /usr/local/share/postgresql/extension 2>/dev/null || true

# 设置 entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]

# 设置健康检查
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
    CMD pg_isready -U ${POSTGRES_USER:-postgres} || exit 1

WORKDIR /
