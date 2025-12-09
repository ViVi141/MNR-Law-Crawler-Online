# PostgreSQL 18 with zhparser 中文分词支持
FROM postgres:18-alpine

# 配置 Alpine 镜像源（使用清华大学镜像，加速下载）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

# 安装编译工具和依赖（单层RUN以减小镜像层，添加 wget 用于备用下载）
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    g++ \
    make \
    git \
    wget \
    tar \
    autoconf \
    automake \
    libtool \
    postgresql-dev \
    musl-dev \
    linux-headers \
    && mkdir -p /usr/local/share/postgresql/extension

# 配置 git 使用代理或镜像（如果需要）
# 设置更长的超时时间
RUN git config --global http.postBuffer 524288000 || true && \
    git config --global http.lowSpeedLimit 0 || true && \
    git config --global http.lowSpeedTime 999999 || true

# 先下载并编译安装 scws（zhparser 的依赖）
WORKDIR /tmp
RUN set -e; \
    echo "========== 开始下载 scws =========="; \
    SCWS_DOWNLOADED=0; \
    # 方法1: 尝试使用 GitHub 代理下载压缩包 \
    echo "[1/4] 尝试方法1: 使用 GitHub 代理下载 scws 压缩包..."; \
    if wget -q --timeout=30 --tries=2 -O scws.tar.gz "https://ghproxy.com/https://github.com/hightman/scws/archive/refs/heads/master.tar.gz" 2>&1; then \
        echo "✓ 方法1成功：使用 GitHub 代理下载 scws 压缩包"; \
        tar -xzf scws.tar.gz && mv scws-master scws && rm -f scws.tar.gz && SCWS_DOWNLOADED=1; \
    # 方法2: 直接从 GitHub 下载压缩包 \
    elif wget -q --timeout=30 --tries=2 -O scws.tar.gz "https://github.com/hightman/scws/archive/refs/heads/master.tar.gz" 2>&1; then \
        echo "✓ 方法2成功：直接从 GitHub 下载 scws 压缩包"; \
        tar -xzf scws.tar.gz && mv scws-master scws && rm -f scws.tar.gz && SCWS_DOWNLOADED=1; \
    # 方法3: 使用 GitHub 代理克隆 \
    elif git clone --depth 1 --branch master "https://ghproxy.com/https://github.com/hightman/scws.git" 2>&1; then \
        echo "✓ 方法3成功：使用 GitHub 代理克隆 scws"; \
        SCWS_DOWNLOADED=1; \
    # 方法4: 直接从 GitHub 克隆 \
    elif git clone --depth 1 --branch master https://github.com/hightman/scws.git 2>&1; then \
        echo "✓ 方法4成功：直接从 GitHub 克隆 scws"; \
        SCWS_DOWNLOADED=1; \
    fi; \
    # 验证下载结果 \
    if [ "$SCWS_DOWNLOADED" != "1" ] || [ ! -d "scws" ]; then \
        echo "❌ 错误: 无法下载 scws"; \
        echo "请检查网络连接，或使用 VPN/代理"; \
        exit 1; \
    fi; \
    echo "========== 开始编译 scws =========="; \
    cd scws && \
    # 检查源码结构 \
    echo "scws 源码目录结构:" && \
    ls -la && \
    echo "检查头文件位置:" && \
    find . -name "*.h" 2>/dev/null | head -5 && \
    ./autogen.sh || (echo "❌ autogen.sh 失败" && exit 1) && \
    ./configure --prefix=/usr/local || (echo "❌ configure 失败" && exit 1) && \
    make || (echo "❌ make 失败" && exit 1) && \
    # 安装前检查构建产物 \
    echo "构建产物检查:" && \
    find . -name "libscws*" -o -name "*.h" 2>/dev/null | head -10 && \
    make install || (echo "❌ make install 失败" && exit 1) && \
    cd /tmp && \
    # 更新动态库缓存 \
    ldconfig /usr/local/lib 2>/dev/null || true && \
    echo "" && \
    echo "========== 验证 scws 安装 ==========" && \
    echo "查找所有 scws 相关文件 (包括子目录):" && \
    find /usr/local -name "*scws*" -o -path "*/scws/*" 2>/dev/null | head -20 || echo "未找到文件" && \
    echo "" && \
    echo "查找 scws 头文件 (所有位置):" && \
    find /usr/local/include -type f -name "*scws*.h" 2>/dev/null || echo "未找到头文件" && \
    find /usr/local/include -type d -name "*scws*" 2>/dev/null || echo "未找到头文件目录" && \
    echo "" && \
    echo "查找 scws 库文件:" && \
    find /usr/local/lib -name "*scws*" 2>/dev/null || echo "未找到库文件" && \
    echo "" && \
    echo "检查 /usr/local/include 目录内容:" && \
    ls -la /usr/local/include/ 2>/dev/null | head -10 || true && \
    echo "" && \
    # 查找 scws.h 的实际位置（可能在多个位置） \
    SCWS_H_FILE=$(find /usr/local/include -type f -name "scws.h" 2>/dev/null | head -1) && \
    if [ -z "$SCWS_H_FILE" ]; then \
        # 尝试查找 scws 目录下的头文件 \
        SCWS_DIR=$(find /usr/local/include -type d -name "scws" 2>/dev/null | head -1) && \
        if [ -n "$SCWS_DIR" ] && [ -f "$SCWS_DIR/scws.h" ]; then \
            SCWS_H_FILE="$SCWS_DIR/scws.h"; \
            echo "在子目录找到: $SCWS_H_FILE"; \
        fi; \
    fi && \
    if [ -z "$SCWS_H_FILE" ]; then \
        echo "❌ 错误: 未找到 scws.h 头文件，scws 安装失败"; \
        echo "检查 /usr/local 目录结构:"; \
        ls -la /usr/local/ 2>/dev/null || true; \
        ls -la /usr/local/include/ 2>/dev/null || true; \
        exit 1; \
    else \
        echo "✓ 找到 scws.h: $SCWS_H_FILE"; \
        # 如果不在根目录，创建符号链接 \
        if [ "$SCWS_H_FILE" != "/usr/local/include/scws.h" ]; then \
            echo "创建符号链接: $SCWS_H_FILE -> /usr/local/include/scws.h"; \
            ln -sf "$SCWS_H_FILE" /usr/local/include/scws.h; \
        fi; \
        # 验证符号链接或文件是否存在 \
        if [ -f /usr/local/include/scws.h ] || [ -L /usr/local/include/scws.h ]; then \
            echo "✓ scws.h 在 /usr/local/include/scws.h 可用"; \
        else \
            echo "❌ 错误: scws.h 符号链接创建失败"; \
            exit 1; \
        fi; \
    fi && \
    # 验证 scws 库文件 \
    SCWS_LIB=$(find /usr/local/lib -name "libscws.so*" -o -name "libscws.a" 2>/dev/null | head -1) && \
    if [ -z "$SCWS_LIB" ]; then \
        echo "❌ 错误: 未找到 scws 库文件，scws 安装失败"; \
        exit 1; \
    else \
        echo "✓ 找到 scws 库: $SCWS_LIB"; \
    fi && \
    echo "========== scws 安装完成 ==========" && \
    rm -rf scws

# 下载并编译安装 zhparser（使用多个备用方案，按优先级尝试）
RUN set -e; \
    echo "========== 开始下载 zhparser =========="; \
    DOWNLOADED=0; \
    # 方法1: 尝试使用 GitHub 代理下载压缩包（最快） \
    echo "[1/5] 尝试方法1: 使用 GitHub 代理下载压缩包..."; \
    if wget -q --timeout=30 --tries=2 -O zhparser.tar.gz "https://ghproxy.com/https://github.com/amutu/zhparser/archive/refs/heads/master.tar.gz" 2>&1; then \
        echo "✓ 方法1成功：使用 GitHub 代理下载压缩包"; \
        tar -xzf zhparser.tar.gz && mv zhparser-master zhparser && rm -f zhparser.tar.gz && DOWNLOADED=1; \
    # 方法2: 尝试直接从 GitHub 下载压缩包 \
    elif wget -q --timeout=30 --tries=2 -O zhparser.tar.gz "https://github.com/amutu/zhparser/archive/refs/heads/master.tar.gz" 2>&1; then \
        echo "✓ 方法2成功：直接从 GitHub 下载压缩包"; \
        tar -xzf zhparser.tar.gz && mv zhparser-master zhparser && rm -f zhparser.tar.gz && DOWNLOADED=1; \
    # 方法3: 尝试使用 GitHub 代理克隆 \
    elif git clone --depth 1 --branch master "https://ghproxy.com/https://github.com/amutu/zhparser.git" 2>&1; then \
        echo "✓ 方法3成功：使用 GitHub 代理克隆"; \
        DOWNLOADED=1; \
    # 方法4: 尝试直接从 GitHub 克隆 \
    elif git clone --depth 1 --branch master https://github.com/amutu/zhparser.git 2>&1; then \
        echo "✓ 方法4成功：直接从 GitHub 克隆"; \
        DOWNLOADED=1; \
    # 方法5: 最后重试（等待后） \
    else \
        echo "[5/5] 所有方法失败，等待15秒后重试..."; \
        sleep 15; \
        if wget -q --timeout=60 --tries=3 -O zhparser.tar.gz "https://ghproxy.com/https://github.com/amutu/zhparser/archive/refs/heads/master.tar.gz" 2>&1; then \
            echo "✓ 重试成功：使用 GitHub 代理下载压缩包"; \
            tar -xzf zhparser.tar.gz && mv zhparser-master zhparser && rm -f zhparser.tar.gz && DOWNLOADED=1; \
        elif git clone --depth 1 --branch master https://github.com/amutu/zhparser.git 2>&1; then \
            echo "✓ 重试成功：直接从 GitHub 克隆"; \
            DOWNLOADED=1; \
        fi; \
    fi; \
    # 验证下载结果 \
    if [ "$DOWNLOADED" != "1" ] || [ ! -d "zhparser" ]; then \
        echo "❌ 错误: 无法下载 zhparser"; \
        echo "请检查网络连接，或使用 VPN/代理"; \
        echo "您也可以手动下载并放入构建上下文"; \
        exit 1; \
    fi; \
    echo "========== 开始编译 zhparser =========="; \
    cd zhparser && \
    # 确保能找到 scws 的头文件和库文件（在同一shell会话中） \
    export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH && \
    export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH && \
    # scws 头文件可能在子目录中，添加多个可能的路径 \
    export C_INCLUDE_PATH=/usr/local/include:/usr/local/include/scws:$C_INCLUDE_PATH && \
    export CPLUS_INCLUDE_PATH=/usr/local/include:/usr/local/include/scws:$CPLUS_INCLUDE_PATH && \
    # 验证 scws 文件位置 \
    echo "库路径: $LD_LIBRARY_PATH" && \
    echo "头文件路径: $C_INCLUDE_PATH" && \
    echo "查找 scws 头文件:" && \
    find /usr/local/include -name "*scws*.h" 2>/dev/null | head -3 && \
    echo "查找 scws 库文件:" && \
    find /usr/local/lib -name "*scws*" 2>/dev/null | head -3 && \
    # 如果 scws.h 在子目录中，创建符号链接 \
    if [ ! -f /usr/local/include/scws.h ]; then \
        SCWS_H=$(find /usr/local/include -name "scws.h" 2>/dev/null | head -1); \
        if [ -n "$SCWS_H" ]; then \
            echo "创建符号链接: $SCWS_H -> /usr/local/include/scws.h"; \
            ln -sf "$SCWS_H" /usr/local/include/scws.h; \
        fi; \
    fi && \
    # 验证 scws.h 是否存在 \
    if [ ! -f /usr/local/include/scws.h ]; then \
        echo "错误: 无法找到 scws.h 头文件"; \
        exit 1; \
    fi && \
    echo "确认 scws.h 存在: /usr/local/include/scws.h" && \
    # 编译 zhparser \
    make PG_CONFIG=/usr/local/bin/pg_config && \
    make install PG_CONFIG=/usr/local/bin/pg_config && \
    cd /tmp && \
    rm -rf zhparser && \
    echo "========== zhparser 安装完成 =========="

# 清理编译工具和缓存（减小镜像大小）
RUN apk del .build-deps \
    && rm -rf /var/cache/apk/* /tmp/* \
    && find /usr/local -name "*.a" -delete \
    && find /usr/local -name "*.la" -delete

# 安装 Python3 用于生成随机密码
RUN apk add --no-cache python3

# 复制包装脚本并设置为 entrypoint
COPY docker-entrypoint-wrapper.sh /usr/local/bin/docker-entrypoint-wrapper.sh
RUN chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh

# 确保扩展目录权限正确
RUN chmod -R 755 /usr/local/share/postgresql/extension

# 设置 entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]

# 设置健康检查
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
    CMD pg_isready -U ${POSTGRES_USER:-postgres} || exit 1

WORKDIR /

