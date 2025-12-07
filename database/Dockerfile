# PostgreSQL 18 with zhparser 中文分词支持
FROM postgres:18-alpine

# 安装编译工具和依赖
RUN apk add --no-cache \
    gcc \
    g++ \
    make \
    git \
    postgresql-dev \
    musl-dev \
    linux-headers \
    && rm -rf /var/cache/apk/*

# 下载并编译安装 zhparser
WORKDIR /tmp
RUN git clone --depth 1 https://github.com/amutu/zhparser.git \
    && cd zhparser \
    && make \
    && make install \
    && cd .. \
    && rm -rf zhparser

# 清理编译工具（保留运行时需要的库）
RUN apk del gcc g++ make git linux-headers

# 确保扩展目录权限正确
RUN mkdir -p /usr/local/share/postgresql/extension

WORKDIR /

