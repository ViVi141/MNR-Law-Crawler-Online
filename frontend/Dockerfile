# 构建阶段
FROM node:24-alpine AS builder
# 使用Node.js 24 LTS（官方推荐，自动使用最新patch版本，当前为24.11.1），基于Alpine Linux以减小镜像大小

WORKDIR /app

# 复制依赖文件
COPY package.json package-lock.json* ./

# 升级npm到最新版本并安装依赖
RUN npm install -g npm@latest && \
    npm ci --legacy-peer-deps

# 复制源代码
COPY . .

# 构建
RUN npm run build

# 运行阶段
FROM nginx:alpine
# 使用Nginx Alpine（最新稳定版），基于Alpine Linux以减小镜像大小

# 复制构建结果
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

