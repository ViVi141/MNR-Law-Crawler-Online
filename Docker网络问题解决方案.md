# Docker 网络连接问题解决方案

## 问题描述

Docker 无法连接到 Docker Hub (registry-1.docker.io)，导致无法拉取基础镜像。

错误信息：
```
failed to resolve source metadata for docker.io/library/postgres:18-alpine
dial tcp [2a03:2880:f10c:283:face:b00c:0:25de]:443: connectex: A connection attempt failed
```

## 解决方案

### 方案一：配置 Docker 镜像加速器（推荐）

#### Windows Docker Desktop

1. 打开 Docker Desktop
2. 点击右上角的 **设置（Settings）** 图标
3. 进入 **Docker Engine** 设置
4. 在 JSON 配置中添加以下内容：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

5. 点击 **Apply & Restart** 重启 Docker

#### 配置示例（完整配置）

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

### 方案二：配置 HTTPS 代理

如果使用代理，需要在 Docker Desktop 中配置：

1. 打开 Docker Desktop
2. 进入 **Settings** → **Resources** → **Proxies**
3. 启用 **Manual proxy configuration**
4. 填写代理地址和端口
5. 点击 **Apply & Restart**

### 方案三：使用国内镜像源（临时方案）

如果镜像加速器仍然无法使用，可以修改 Dockerfile 使用国内镜像：

#### 修改 database/Dockerfile

```dockerfile
# 使用阿里云镜像
FROM registry.cn-hangzhou.aliyuncs.com/acs/postgres:18-alpine
```

或者使用其他国内镜像源。

### 方案四：手动拉取镜像

在配置镜像加速器后，可以手动拉取所需镜像：

```bash
# 拉取 PostgreSQL 镜像
docker pull postgres:18-alpine

# 拉取 Python 镜像
docker pull python:3.12.10-slim

# 拉取 Node.js 镜像
docker pull node:24-alpine

# 拉取 Nginx 镜像
docker pull nginx:alpine
```

## 验证配置

配置完成后，运行以下命令验证：

```bash
# 测试拉取镜像
docker pull hello-world

# 如果成功，运行测试
docker run hello-world
```

## 推荐的镜像加速器地址

### 国内常用镜像加速器

1. **中科大镜像**：`https://docker.mirrors.ustc.edu.cn`
2. **网易镜像**：`https://hub-mirror.c.163.com`
3. **百度云镜像**：`https://mirror.baidubce.com`
4. **阿里云镜像**：需要登录阿里云获取专属地址
5. **腾讯云镜像**：`https://mirror.ccs.tencentyun.com`

### 获取阿里云专属镜像地址

1. 登录 [阿里云容器镜像服务](https://cr.console.aliyun.com/)
2. 进入 **镜像加速器**
3. 复制专属加速地址
4. 添加到 Docker 配置中

## 常见问题

### Q: 配置后仍然无法连接？

A: 尝试以下步骤：
1. 重启 Docker Desktop
2. 检查网络连接
3. 尝试使用不同的镜像加速器
4. 检查防火墙设置

### Q: 如何查看当前配置？

A: 运行以下命令：
```bash
docker info | grep -A 10 "Registry Mirrors"
```

### Q: 配置多个镜像加速器有用吗？

A: 是的，Docker 会按顺序尝试，如果第一个失败会自动尝试下一个。

## 完成配置后

配置完成后，重新运行：

```bash
docker-compose up -d
```

如果仍有问题，可以尝试：

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```
