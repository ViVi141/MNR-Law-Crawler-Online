# PostgreSQL 18
FROM postgres:18-alpine

# 配置 Alpine 镜像源（使用清华大学镜像，加速下载）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

# 安装 Python3 用于生成随机密码
RUN apk add --no-cache python3

# 复制 entrypoint wrapper 脚本
COPY docker-entrypoint-wrapper.sh /usr/local/bin/docker-entrypoint-wrapper.sh

# 设置执行权限并验证文件
RUN chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh && \
    [ -f /usr/local/bin/docker-entrypoint-wrapper.sh ] && \
    [ -x /usr/local/bin/docker-entrypoint-wrapper.sh ] && \
    head -n 1 /usr/local/bin/docker-entrypoint-wrapper.sh | grep -q "#!/bin/sh" && \
    echo "✅ 验证通过: 文件存在且格式正确"

# 最终验证：确保文件在最终镜像中仍然存在
RUN ls -lh /usr/local/bin/docker-entrypoint-wrapper.sh && \
    [ -f /usr/local/bin/docker-entrypoint-wrapper.sh ] || (echo "❌ 最终验证失败: 文件不存在" && exit 1) && \
    [ -x /usr/local/bin/docker-entrypoint-wrapper.sh ] || (echo "❌ 最终验证失败: 文件不可执行" && exit 1) && \
    echo "✅ 最终验证通过"

# 确保扩展目录权限正确
RUN chmod -R 755 /usr/local/share/postgresql/extension 2>/dev/null || true

# 设置 entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]

# 设置健康检查
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
    CMD pg_isready -U ${POSTGRES_USER:-postgres} || exit 1

WORKDIR /
