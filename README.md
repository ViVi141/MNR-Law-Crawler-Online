# Policy Crawler Pro (政策爬虫专业版)

[![CI/CD Pipeline](https://github.com/ViVi141/Policy-Crawler-Pro/actions/workflows/ci.yml/badge.svg)](https://github.com/ViVi141/Policy-Crawler-Pro/actions/workflows/ci.yml)
[![Docker Compose Test](https://github.com/ViVi141/Policy-Crawler-Pro/actions/workflows/docker-compose.yml/badge.svg)](https://github.com/ViVi141/Policy-Crawler-Pro/actions/workflows/docker-compose.yml)

> **Web化政策法规库管理系统** - 集爬取、存储、搜索、管理于一体的现代化政策法规库系统

**English**: Policy Crawler Pro | **中文**: 政策爬虫专业版

## 📌 项目说明

这是一个全新的Web应用项目，用于管理和爬取多数据源的政策法规数据。项目采用了现代化的前后端分离架构，提供了完整的政策法规库管理功能。

> **注意**：本项目支持多个数据源，包括自然资源部政府信息公开平台、政策法规库以及广东省法规等。整体架构、功能设计和实现都是全新的。

## 📢 项目声明

### 🎓 项目性质
**本项目主要为学术研究提供基础数据支持**，并非我的主要项目。虽然我已经投入了大量精力构建完整的CI/CD流程，但由于项目定位和个人精力有限，**无法保证及时的更新和BUG修复**。

### 🚀 维护状态
- **更新频率**：不定期更新，主要在有学术需求时进行改进
- **BUG修复**：优先处理严重影响学术研究的BUG，其他问题可能延迟处理
- **功能扩展**：主要围绕学术研究需求进行功能优化
- **技术支持**：社区驱动，欢迎提交PR贡献代码

### 💡 建议使用方式
- **学术研究**：推荐用于学术研究和数据收集
- **生产环境**：建议谨慎评估，考虑商业技术支持服务
- **学习参考**：适合学习现代Web应用架构和技术栈

### 🤝 贡献与反馈
欢迎所有开发者贡献代码和建议！虽然维护响应可能不及时，但每个贡献都会被认真考虑和感谢。

## 📋 使用条款

### ✅ 商业使用许可
- **允许商业使用**：您可以通过购买、租借、订阅等方式合法使用本项目
- **分发许可**：在获得授权后，您可以分发本项目的副本
- **技术支持**：可选择购买技术支持服务

### ⭐ 项目支持
**如果您喜欢这个项目，请到GitHub原项目点个STAR！**
- 项目地址：[https://github.com/ViVi141/policy-crawler-pro](https://github.com/ViVi141/policy-crawler-pro)
- 点击右上角的⭐ Star按钮支持我们

### ⚠️ 重要声明
**严禁用于非法用途！**
- 所有开发者与用户必须遵守当地法律法规
- 不得将本项目用于任何违法违规活动
- 不得侵犯他人知识产权和隐私权
- 使用者对使用本项目产生的后果负全部责任

### 🤝 免责声明
本项目按"现状"提供，不提供任何明示或暗示的保证。作者不对使用本项目产生的任何直接或间接损害承担责任。

## ✨ 核心特性

### 🌐 Web化系统
- 🎨 **现代化前端**：Vue 3 + TypeScript + Element Plus 构建的美观Web界面
- 🚀 **RESTful API**：FastAPI 构建的高性能后端服务
- 📱 **响应式设计**：支持不同屏幕尺寸，良好的移动端体验
- 🔐 **安全认证**：JWT Token认证，安全的用户管理

### 🕷️ 智能爬虫
- 🎯 **多数据源支持**：支持政府信息公开平台、政策法规库等多个数据源
- 🔄 **智能解析**：针对不同数据源使用专用HTML解析器
- ⏱️ **时间范围过滤**：支持指定日期范围进行增量爬取
- 🔍 **关键词搜索**：支持关键词筛选，或全量爬取
- ⚡ **可配置延迟**：支持设置请求延迟，避免对目标服务器造成压力
- 🛡️ **容错机制**：自动重试失败的政策，完善的错误处理

### 📚 政策库管理
- 💾 **多格式存储**：自动保存JSON、Markdown、DOCX和原始文件
- 🔍 **全文搜索**：基于PostgreSQL的全文搜索，支持关键词、分类、日期等多维度筛选
- 📊 **数据统计**：实时显示政策数量、任务进度等统计信息
- 🏷️ **分类管理**：自动提取和分类政策，支持按分类筛选
- 📎 **附件管理**：自动下载和管理政策附件

### ⚙️ 任务管理
- 🎮 **任务创建**：灵活的任务配置（关键词、日期范围、数据源选择、页面限制）
- 📈 **实时监控**：实时显示任务执行进度和统计信息
- ⏸️ **任务控制**：支持启动、取消任务
- 📝 **任务历史**：完整的任务执行历史记录
- 🔔 **邮件通知**：任务完成/失败自动邮件通知（可选）

### 🕐 定时任务
- ⏰ **Cron支持**：支持Cron表达式配置定时任务
- 📅 **灵活调度**：支持启用/禁用定时任务
- 📊 **执行历史**：查看定时任务的执行历史记录

### ☁️ 存储与备份
- 💿 **本地存储**：默认使用本地文件系统存储
- ☁️ **S3存储**：可选配置AWS S3或兼容的对象存储服务
- 💾 **数据库备份**：支持PostgreSQL数据库备份和恢复
- 🔄 **自动清理**：支持清理旧文件和备份

### 🎛️ 系统配置
- 🔧 **功能开关**：灵活的功能开关管理
- 📧 **邮件配置**：支持SMTP邮件服务配置
- 🗄️ **数据源管理**：可视化配置和管理多个数据源
- ⚙️ **爬虫配置**：可配置请求延迟、代理设置等

## 🏗️ 技术架构

### 前端技术栈
- **框架**：Vue 3 (Composition API)
- **语言**：TypeScript
- **状态管理**：Pinia
- **路由**：Vue Router
- **UI组件**：Element Plus
- **HTTP客户端**：Axios
- **构建工具**：Vite

### 后端技术栈
- **框架**：FastAPI
- **语言**：Python 3.11+
- **ORM**：SQLAlchemy
- **数据库**：PostgreSQL
- **认证**：JWT (JSON Web Tokens)
- **任务调度**：APScheduler
- **文档转换**：python-docx, mammoth
- **HTML解析**：BeautifulSoup4

### 存储方案
- **元数据**：PostgreSQL
- **文件存储**：本地文件系统 或 AWS S3
- **缓存**：本地文件缓存

## 📦 项目结构

```
Policy-Crawler-Pro/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心爬虫逻辑
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务服务层
│   │   ├── middleware/     # 中间件
│   │   └── main.py         # FastAPI应用入口
│   ├── migrations/         # 数据库迁移
│   ├── requirements.txt    # Python依赖
│   └── Dockerfile          # Docker镜像
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/           # API客户端
│   │   ├── views/         # 页面组件
│   │   ├── layouts/       # 布局组件
│   │   ├── stores/        # 状态管理
│   │   ├── router/        # 路由配置
│   │   └── types/         # TypeScript类型
│   ├── package.json       # Node.js依赖
│   └── Dockerfile         # Docker镜像
├── docker-compose.yml     # Docker Compose配置（支持自动密钥生成）
├── env.example            # 环境变量配置示例
├── generate-env.ps1       # Windows环境变量生成脚本
├── generate_env.py        # Python环境变量生成脚本
├── 快速启动.ps1          # Windows启动脚本
└── README.md             # 本文档
```

## 🚀 快速开始

### 方式一：Docker Compose启动（推荐，零配置）

**最简单的启动方式，无需任何配置！**

```bash
# 1. 克隆项目
git clone https://github.com/ViVi141/Policy-Crawler-Pro.git
cd Policy-Crawler-Pro

# 2. 启动所有服务（自动生成所有密钥）
docker-compose up -d --build

# 3. 访问应用
# 前端：http://localhost:3000
# 后端API文档：http://localhost:8000/docs
# 
# 默认管理员账号：
#   用户名：admin
#   密码：admin123
#   邮箱：admin@example.com
```

#### ✨ Docker 自动配置特性

- ✅ **自动生成强随机密码**：数据库密码（32字符）和 JWT 密钥（128字符）
- ✅ **密码自动持久化**：容器重启不会覆盖密码，保存在数据卷中
- ✅ **自动容器间共享**：数据库密码自动共享给后端容器
- ✅ **多阶段构建优化**：更小的镜像体积，更快的构建速度
- ✅ **资源限制**：CPU和内存限制，防止资源耗尽
- ✅ **健康检查**：自动健康检查和故障恢复
- ✅ **日志管理**：自动日志轮转，防止日志文件过大

### 方式二：本地开发启动

#### 前提条件
- Python 3.11+
- Node.js 18+
- PostgreSQL 数据库（本地或远程）

#### 后端启动

```bash
cd backend

# 1. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量（可选）
# 创建 .env 文件或设置环境变量
# DATABASE_URL=postgresql://user:password@localhost:5432/mnr_crawler
# JWT_SECRET_KEY=your-secret-key

# 4. 运行数据库迁移
alembic upgrade head

# 5. 启动后端服务
python -m app.main
# 或使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端启动

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 配置环境变量（可选）
# 创建 .env 文件，设置 VITE_API_BASE_URL=http://localhost:8000

# 3. 启动开发服务器
npm run dev
```

### 方式三：Windows一键启动

使用提供的批处理脚本：

```bash
启动项目.bat
```

脚本会自动启动前端和后端服务。

## ⚙️ 配置说明

### Docker 环境变量配置（可选）

系统支持零配置启动，所有密钥会自动生成。如需自定义配置，可以创建 `.env` 文件：

```bash
# 使用脚本自动生成（推荐）
powershell -ExecutionPolicy Bypass -File generate-env.ps1

# 或手动复制模板
cp env.example .env
```

主要配置项（`.env` 文件）：
- `POSTGRES_DB` - 数据库名称（默认：mnr_crawler）
- `POSTGRES_USER` - 数据库用户（默认：mnr_user）
- `POSTGRES_PASSWORD` - 数据库密码（默认：自动生成32字符随机密码）
- `JWT_SECRET_KEY` - JWT密钥（默认：自动生成128字符随机密钥）
- `BACKEND_PORT` - 后端端口（默认：8000）
- `FRONTEND_PORT` - 前端端口（默认：3000）

**注意**：如果设置了自定义值，将使用您提供的值，不会自动生成。

### 数据库配置

#### Docker 环境
数据库配置通过环境变量自动完成，无需手动配置。

#### 本地开发环境
在 `backend/config.json` 中配置数据库连接：

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "mnr_crawler",
    "user": "your_username",
    "password": "your_password"
  }
}
```

### 爬虫配置

在系统设置的"爬虫配置"中可配置：
- **请求延迟**：默认0.5秒，可根据需要调整
- **代理设置**：目前不支持（目标网站无防护）

### 数据源配置

支持配置多个数据源，每个数据源可独立设置：
- `name`: 数据源名称
- `base_url`: 基础URL
- `search_api`: 搜索API
- `ajax_api`: AJAX API
- `channel_id`: 频道ID
- `enabled`: 是否启用

### S3存储配置（可选）

在系统设置的"S3存储配置"中配置：
- S3访问密钥
- S3存储桶名称
- S3区域

### 邮件服务配置（可选）

在系统设置的"邮件服务配置"中配置SMTP信息，用于任务完成通知。

## 📖 使用指南

### 创建爬取任务

1. 进入"任务管理"页面
2. 点击"创建任务"
3. 配置任务参数：
   - **任务名称**：给任务起个名字
   - **关键词**：可选，留空则全量爬取
   - **日期范围**：可选，指定爬取的时间范围
   - **数据源**：选择一个或多个数据源
   - **最大页数**：限制爬取的页数（可选）
   - **自动启动**：是否创建后立即启动
4. 点击"创建"按钮

### 搜索政策

1. 进入"政策列表"页面
2. 使用搜索表单筛选政策：
   - **关键词**：全文搜索
   - **分类**：按分类筛选
   - **数据源**：按数据源筛选
   - **日期范围**：按发布日期筛选
   - **发布机构**：按发布机构筛选
3. 点击"搜索"按钮

### 查看政策详情

1. 在政策列表中点击政策标题
2. 查看完整的政策信息
3. 下载政策文件（JSON/Markdown/DOCX）

### 创建定时任务

1. 进入"定时任务"页面
2. 点击"创建定时任务"
3. 配置Cron表达式和任务参数
4. 启用定时任务

## 🔧 开发说明

### 后端开发

```bash
cd backend
python -m app.main
```

后端API文档自动生成在：http://localhost:8000/docs

### 前端开发

```bash
cd frontend
npm run dev
```

前端开发服务器运行在：http://localhost:3000

### 代码检查

```bash
# 后端导入检查
cd backend
python check_imports.py  # 如果脚本存在

# 前端代码检查
cd frontend
npm run lint
```

## 📊 数据流架构

详细的系统数据流和架构说明请查看：
- [数据流导图.md](数据流导图.md) - 完整的数据流说明
- [数据流图表-Mermaid.md](数据流图表-Mermaid.md) - 可视化流程图

## 🐳 Docker 使用说明

### 快速启动

```bash
# 零配置启动（推荐）
docker-compose up -d --build
```

### 自动配置说明

系统会自动完成以下配置：
1. **数据库密码**：如果未设置，自动生成32字符强随机密码
2. **JWT密钥**：如果未设置，自动生成128字符强随机密钥
3. **密码持久化**：密码保存在数据卷中，容器重启不会覆盖
4. **容器间共享**：数据库密码自动共享给后端容器

### 查看自动生成的密钥

```bash
# 查看数据库容器日志
docker-compose logs db | grep "已自动生成"

# 查看后端容器日志
docker-compose logs backend | grep "已自动生成"

# 查看持久化的密码文件
docker exec mnr-crawler-db cat $PGDATA/.postgres_password
docker exec mnr-crawler-backend cat /app/logs/.jwt_secret_key
```

### 自定义配置

如需自定义配置，创建 `.env` 文件：

```bash
# 自动生成（推荐）
powershell -ExecutionPolicy Bypass -File generate-env.ps1

# 或手动复制
cp env.example .env
```

编辑 `.env` 文件设置自定义值后，重新启动容器即可。

### 开发模式

在 `docker-compose.yml` 中取消注释以下行以启用热重载：

```yaml
volumes:
  - ./backend:/app
```

### 容器管理

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
docker-compose logs -f db      # 仅查看数据库日志
docker-compose logs -f backend # 仅查看后端日志

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 完全重置（删除所有数据和容器）
docker-compose down -v

# 查看资源使用情况
docker stats
```

### 常见问题

#### 1. 容器重启后密码是否会改变？
✅ **不会**。密码保存在数据卷中，只要数据卷不被删除，密码就不会改变。

#### 2. 如何查看自动生成的密码？
```bash
# 查看数据库密码
docker exec mnr-crawler-db cat $PGDATA/.postgres_password

# 查看JWT密钥
docker exec mnr-crawler-backend cat /app/logs/.jwt_secret_key
```

#### 3. 如何重新生成密码？
```bash
# 方法一：完全重置（推荐）
docker-compose down -v
docker-compose up -d --build

# 方法二：删除密码文件后重启
docker exec mnr-crawler-db rm -f $PGDATA/.postgres_password
docker exec mnr-crawler-backend rm -f /app/logs/.jwt_secret_key
docker-compose restart
```

#### 4. 端口被占用怎么办？
修改 `docker-compose.yml` 中的端口映射，或创建 `.env` 文件自定义端口：
```env
BACKEND_PORT=8001
FRONTEND_PORT=3001
POSTGRES_PORT=5433
```

#### 5. 构建时网络连接失败怎么办？

**系统已自动配置国内镜像源**：
- ✅ Debian apt: 清华大学镜像
- ✅ Python pip: 清华大学镜像  
- ✅ npm: 淘宝镜像
- ✅ Alpine apk: 清华大学镜像
- ✅ GitHub: 多个备用方案（代理、压缩包下载）

**如果仍遇到网络问题**：

**方案一：检查 Docker Desktop**
```bash
# 确保 Docker Desktop 正在运行
# 检查网络设置和防火墙
```

**方案二：配置代理（如果使用代理）**
```bash
# 在 Docker Desktop 设置中配置代理
# 或设置环境变量
$env:HTTP_PROXY="http://your-proxy:port"
$env:HTTPS_PROXY="http://your-proxy:port"
```

**方案三：使用 VPN 或更换网络**
网络环境可能无法访问某些镜像源，建议：
- 使用 VPN
- 使用手机热点
- 更换网络环境

**方案四：分步构建**
```bash
# 单独构建每个服务
docker-compose build db --no-cache
docker-compose build backend --no-cache  
docker-compose build frontend --no-cache
```

**方案五：查看详细错误**
```bash
# 查看构建日志
docker-compose build 2>&1 | tee build.log

# 查看特定服务的构建日志
docker-compose build backend 2>&1 | tee backend-build.log
```

## 🗄️ 数据库

项目使用PostgreSQL数据库，主要表结构：

- **users** - 用户表
- **policies** - 政策表
- **tasks** - 任务表
- **attachments** - 附件表
- **scheduled_tasks** - 定时任务表
- **system_config** - 系统配置表
- **backup_records** - 备份记录表

数据库迁移使用Alembic管理，位于 `backend/migrations/` 目录。

## 🔐 安全说明

### 认证与授权
- 使用JWT Token进行身份认证
- 密码使用BCrypt加密存储
- API接口除登录外都需要认证
- 支持密码修改和重置功能

### Docker 安全特性
- ✅ **非root用户运行**：所有容器都以非特权用户运行
- ✅ **自动生成强密钥**：使用加密安全的随机数生成器
- ✅ **密码持久化**：密码保存在数据卷中，重启不丢失
- ✅ **网络隔离**：前后端网络分离，提高安全性
- ✅ **资源限制**：防止资源耗尽攻击
- ✅ **安全响应头**：Nginx 配置了完整的安全头

## 📄 许可证

本项目采用 **AGPL-3.0 license** 开源许可证。

## 👥 作者

**ViVi141**

- **GitHub**: [@ViVi141](https://github.com/ViVi141)
- **邮箱**: 747384120@qq.com

**项目名称**: Policy-Crawler-Pro  
**英文全称**: Policy Crawler Pro  
**中文名称**: 政策爬虫专业版  
**项目类型**: 全新Web应用项目  
**数据源支持**: 支持多个数据源，包括自然资源部政府信息公开平台、政策法规库、广东省法规等

---

**版本**: 3.1.4  
**最后更新**: 2025-12-31
**项目主页**: https://github.com/ViVi141/policy-crawler-pro

## 📝 更新日志

### v3.1.4 (2025-12-31) - 任务附件下载功能与广东省数据源增强

#### ✨ 新增功能
- **任务附件下载**：在任务界面添加了下载附件按钮，支持批量下载任务关联的所有附件
- **附件打包**：附件按政策标题组织文件夹结构，方便管理和查找
- **代码优化**：优化了广东省数据源的附件处理逻辑，确保所有数据源的附件都能正常下载
- **广东省数据源异常处理增强**：完善错误处理机制，确保任务状态正确同步
- **广东省数据源自动化检查**：新增数据验证器，自动检查数据质量和逻辑正确性

#### 🔧 改进
- 修复了广东省数据源附件下载的问题
- 改进了附件下载API的错误处理
- 统一了版本号管理，前端自动从后端API获取版本号
- **广东省数据源异常处理**：爬取异常时任务状态立即更新为失败，避免状态不同步
- **数据完整性检查**：自动验证政策数据的必需字段（标题、ID、日期、URL等）
- **数据格式验证**：检查日期格式、URL格式等数据格式正确性
- **去重逻辑验证**：确保使用`_gd_id`进行去重的逻辑正确工作
- **数据质量统计**：记录有效率、重复率等关键指标
- **详细日志记录**：便于问题追踪和调试

#### 🐛 修复
- 修复广东省数据源爬取时因技术错误导致任务状态不同步的问题
- 修复政策计数逻辑，确保使用`_gd_id`进行正确去重

### v3.1.2 (2025-12-24) - 代码质量改进

#### 🔧 代码质量改进
- **类型安全增强**：
  - 改进 TaskCreationForm.vue 中的类型定义，移除 `any` 类型使用
  - 在 Tasks.vue 中添加类型守卫函数，确保类型安全
  - 改进 ScheduledTasks.vue 中的类型定义，使用明确的类型而非 `any`
  - 优化 Policies.vue 中的类型处理

- **错误处理优化**：
  - 移除未使用的 error 变量，改进错误处理逻辑
  - 在多个组件中统一错误处理方式
  - 改进错误捕获和日志记录

- **代码格式改进**：
  - 格式化后端 API 代码（scheduled_tasks.py）
  - 改进代码可读性和一致性
  - 统一代码风格

#### 🐛 Bug修复
- 修复 Tasks.vue 中定时任务类型检查逻辑，防止在错误页面创建定时任务
- 改进 TaskCreationForm.vue 中的类型转换，避免类型错误

### v3.1.1 (2025-12-23) - 文档清理和最终优化

#### 🐛 Bug修复
- 修复 Dockerfile 中 apt-get 命令的非交互模式设置，提高构建可靠性
- 修复 Tasks.vue 中的错误处理，在进度流传输期间忽略解析错误，增强任务管理的健壮性

#### 📝 文档更新
- 移除过时的数据流文档和 Mermaid 可视化图表
- 更新 README.md 以反映文件移除，简化项目结构

#### 🛠️ 技术改进
- 优化 Dockerfile 构建流程
- 改进前端错误处理逻辑

### v3.1.0 (2025-12-14) - 任务管理和进度跟踪系统

#### ✨ 新功能
- **详细进度跟踪系统**：实现基于 SSE 的实时进度流传输功能
  - 广播任务执行阶段的实时更新
  - 显示整体进度和各个阶段的详细信息
  - 显示成功率和处理状态
  - 提升长时间运行任务的用户体验和反馈

#### 🔧 系统优化
- 重构调度器服务，支持基于配置更改动态启用和禁用定时任务
- 改进前端进度显示，提供更全面的进度信息

### v3.0.3 (2025-12-13) - 备份上传和附件批量下载

#### ✨ 新功能
- **备份文件上传**：实现备份文件上传功能
  - 添加备份上传 API 端点
  - 支持 .sql 文件验证
  - 增强 BackupService 以从上传文件创建备份记录
  - 更新前端组件支持文件选择和上传

- **附件批量下载和内容合并**：
  - 添加批量下载附件的 API 端点
  - 实现将附件内容合并到政策文本的功能
  - 增强前端 UI，支持下载所有附件和显示处理信息
  - 改进附件操作的错误处理和用户反馈

#### 🔧 系统优化
- 重构任务管理 UI 组件，使用统一的 TaskCreationForm 创建和编辑任务
- 简化任务创建逻辑，整合表单处理和验证
- 更新邮件通知逻辑，改进错误处理和日志记录
- 增强文件下载过程，改进文件路径管理和存在性检查
- 添加邮件服务配置重载功能，当 "email_enabled" 标志切换时通知邮件服务重新加载配置

#### 🐛 Bug修复
- 修复任务管理错误处理，简化 HTTPException 抛出
- 更新 Policies.vue 和 PolicyDetail.vue 以增强 UI 一致性和可读性
- 改进数据源处理，提高政策详情中的清晰度
- 修复 TaskCreationForm 验证逻辑，使用表单值直接进行数据源选择
- 简化未选择数据源的警告消息

#### 🧹 代码清理
- 移除未使用的依赖检查脚本和类型检查工具
- 移除过时的数据库修复脚本和示例数据文件
- 清理未使用的 SQL 索引修复和与数据库维护相关的 Python 脚本
- 更新前端 API 和组件文件以改进数据处理和 UI 一致性

### v3.0.2 (2025-12-12) - 系统优化和重构

#### 🔧 系统优化
- **数据库连接优化**：
  - 优化数据库连接设置以减少内存使用并提高性能
  - 使用更快的压缩算法和进度日志记录增强任务文件下载过程
  - 实现内存清理和使用日志记录

- **日期时间处理改进**：
  - 更新多个服务以使用时区感知的 datetime 对象
  - 确保在 UTC 中一致的时间表示
  - 增强日志记录、备份和任务管理中的时间戳准确性

- **配置服务优化**：
  - 重构 ConfigService 以改进 JSON 值处理
  - 添加 `_parse_json_value` 和 `_serialize_value` 方法
  - 简化地址解析逻辑以提高可读性

- **代码质量提升**：
  - 重构全局变量使用，移除不必要的锁
  - 改进代码格式检查和错误消息
  - 增强后端服务模块导出列表
  - 更新 ESLint 配置以忽略 Vue 自动生成的类型定义文件

#### 🧹 代码清理
- 重构 generate_env.py 和 check_types.py 以提高可读性和一致性
- 更新字符串格式并移除不必要的空行
- 改进类型检查方法，使用更清晰的函数签名

#### 🛠️ CI/CD 改进
- 增强 CI 工作流，添加自定义类型检查步骤
- 改进依赖验证，使用包名到导入名的映射
- 改进重定向测试和端点测试
- 更新 Docker Compose 配置以改进服务连接和测试

### v3.0.1 (2025-12-10 至 2025-12-11) - Docker 和 CI/CD 优化

#### 🐳 Docker 优化
- **数据库容器优化**：
  - 增强 docker-entrypoint-wrapper.sh 以改进随机字符串生成
  - 添加多种备用方法（Python、/dev/urandom、OpenSSL）
  - 改进数据目录验证和清理逻辑
  - 增强数据库健康检查参数和初始化等待时间
  - 在 Dockerfile 中显式创建 PostgreSQL 数据目录

- **后端容器优化**：
  - 重构 Dockerfile 以改进 Python 安装过程
  - 增强错误处理和重试逻辑
  - 简化包更新和安装命令以提高跨平台兼容性

- **网络配置优化**：
  - 更新 docker-compose.yml 以限制外部端口暴露
  - 配置网络设置，包括指定子网以避免冲突
  - 启用可附加网络以支持外部容器访问
  - 修改 API 基础 URL 处理以支持生产环境和开发环境

#### 🔧 系统改进
- **数据库表创建逻辑**：
  - 增强数据库表创建逻辑以检查现有表，避免重复错误
  - 改进日志记录，优雅处理用户创建错误
  - 允许非关键问题的警告，同时保持应用程序启动完整性

- **前端改进**：
  - 重构 TypeScript 类型以改进组件处理
  - 增强 main.ts 中 Element Plus 组件的类型安全性
  - 更新 Axios 错误处理
  - 改进 policies.ts 中的类型定义
  - 清理任务显示逻辑以提高可读性和可维护性

#### 🛠️ CI/CD 改进
- **GitHub Actions 工作流**：
  - 增强 CI 工作流以支持基于目标规范的 Docker 镜像构建
  - 添加 Docker 镜像扫描（后端和前端服务）
  - 改进健康检查、数据库迁移步骤和集成测试
  - 添加服务就绪等待机制
  - 更新 Trivy 扫描输出并改进日志记录
  - 改进重定向测试和端点测试
  - 添加 API 登录端点测试
  - 使用 Docker Compose V2 以提高兼容性和性能

- **安全扫描**：
  - 更新 Trivy action 版本以改进漏洞扫描兼容性
  - 改进安全扫描摘要输出以提高清晰度
  - 增强 CI 工作流权限以改进安全事件处理

#### 📝 文档更新
- 更新 README.md 以包含重要的 Docker 部署说明
- 添加 GitHub Actions 部署详细信息
- 移除过时的 .github/README.md 文件
- 更新版本日期和部署信息

#### 🐛 Bug修复
- 修复数据库初始化问题
- 修复密码生成错误处理
- 修复网络连接和健康检查问题
- 修复前端 API 基础 URL 处理

### v3.0.0 (2025-12-09) - Docker优化与自动配置

#### 🎉 Docker 优化与自动化
- ✨ **自动生成随机密钥**：容器启动时自动生成数据库密码和JWT密钥，无需手动配置
- 🔒 **密码持久化机制**：密码保存在数据卷中，容器重启不会覆盖
- 🚀 **多阶段构建优化**：减小镜像体积30-40%，提升构建速度40-60%
- 🔐 **安全增强**：非root用户运行，网络隔离，资源限制
- 📊 **日志管理**：自动日志轮转，防止日志文件过大
- ⚡ **健康检查优化**：改进的健康检查配置，确保服务可用性
- 🌐 **国内镜像源支持**：自动配置清华大学镜像源，加速包下载（apt、apk、npm、pip）
- 🔄 **网络重试机制**：添加超时和重试配置，提高网络稳定性

#### 🛠️ 技术改进
- 📦 **后端Dockerfile优化**：多阶段构建，依赖缓存优化，非root用户，系统级包安装
- 🌐 **前端Dockerfile优化**：Nginx 1.28配置优化，静态资源缓存，Gzip压缩，非root用户运行
- 🗄️ **数据库Dockerfile优化**：移除中文分词依赖，简化配置，减小镜像体积
- 📝 **环境变量管理**：支持`.env`文件，提供自动生成脚本
- 🔧 **Entrypoint脚本优化**：修复Windows CRLF换行符问题，改进密码读取逻辑

#### 📋 新增文件
- `generate-env.ps1` - Windows环境变量生成脚本
- `generate_env.py` - 跨平台环境变量生成脚本
- `env.example` - 环境变量配置示例
- `database/docker-entrypoint-wrapper.sh` - 数据库密码自动生成脚本
- `database/save-password.sh` - 数据库密码持久化脚本
- `backend/docker-entrypoint.sh` - 后端密钥自动生成脚本

#### 🐛 Bug修复
- 🔧 **修复Nginx配置错误**：移除重复的`keepalive_timeout`和`pid`指令
- 🔧 **修复权限问题**：修复Nginx非root用户运行时的PID文件权限问题
- 🔧 **修复后端uvicorn模块找不到**：改为系统级安装Python包，确保所有用户可访问
- 🔧 **修复数据库初始化问题**：改进数据目录清理逻辑，避免初始化冲突

### v1.1.0 (2025-12-08) - BUG修复与系统优化

#### 🐛 严重BUG修复
- 🔧 **修复任务统计错误**：修复了`failed_count`计算错误，确保任务统计信息准确
  - 修复了所有政策（无论成功还是失败）都被计入`failed_count`的问题
  - 现在`failed_count`只在保存失败时正确增加
- 🔧 **修复S3文件路径不一致**：修复了任务完成后检查S3上传时路径不匹配的问题
  - 统一使用包含`task_id`的文件路径格式：`policies/{task_id}/{policy_id}/{policy_id}.md`
  - 确保文件保存和检查时使用相同的路径规则
- 🔧 **修复文件清理逻辑**：修复了文件清理时政策ID提取错误的问题
  - 使用记录的原始文件路径来匹配文件，而不是通过文件名提取ID
  - 解决了文件名中的`markdown_number`与`policy.id`不一致导致的清理失败问题
- 🔧 **修复附件路径问题**：修复了附件路径不包含`task_id`的问题
  - 附件路径现在包含`task_id`，确保不同任务的附件独立存储
  - 修复了`save_attachment`函数调用时缺少`task_id`参数的问题
- 🔧 **修复文件清理函数**：为`cleanup_policy_files`函数添加了`task_id`参数支持
  - 确保删除文件时使用正确的路径（包含`task_id`）
  - 避免文件残留和路径错误问题

#### 🎯 系统优化
- 📊 **数据独立性增强**：所有文件路径现在都包含`task_id`，确保不同任务的数据完全独立
- 🗂️ **文件管理改进**：改进了文件保存和清理逻辑，提高了文件管理的可靠性
- 🔍 **代码质量提升**：修复了多个数据流一致性问题，提高了系统的稳定性

#### 📝 数据库迁移
- ✨ **新增迁移**：`005_add_backup_source_fields.py` - 添加备份源字段
- ✨ **新增迁移**：`006_add_policy_task_id.py` - 为政策表添加`task_id`字段

#### 🛠️ 技术改进
- 📦 **新增工具模块**：`backend/app/services/utils.py` - 通用工具函数
- 🔄 **服务层优化**：优化了多个服务层的代码逻辑和错误处理
  - 优化了`task_service.py`中的文件保存和清理逻辑
  - 改进了`storage_service.py`中的文件路径管理
  - 增强了`policy_service.py`中的数据处理逻辑

#### 📋 修改文件列表
本次更新涉及以下主要文件：
- `backend/app/services/task_service.py` - 修复任务统计和文件清理逻辑
- `backend/app/services/storage_service.py` - 修复文件路径和附件管理
- `backend/app/models/policy.py` - 添加`task_id`字段支持
- `backend/migrations/versions/006_add_policy_task_id.py` - 数据库迁移
- 其他相关服务层和API层的优化

### v1.0.0 (2025-12-08) - 初始版本发布

#### 核心功能
- ✨ **Web化架构**：全新的前后端分离架构设计
- 🌐 **前端框架**：Vue 3 + TypeScript + Element Plus构建的现代化界面
- 🚀 **后端框架**：FastAPI构建的高性能RESTful API服务
- 📚 **政策库管理**：完整的政策存储、搜索、管理功能
- 🔍 **全文搜索**：基于PostgreSQL的全文搜索功能，支持多维度筛选
- 🎮 **任务管理**：可视化任务创建、监控和管理
- ⏰ **定时任务**：支持Cron表达式的定时爬取任务

#### 爬虫功能
- 🕷️ **爬虫核心**：集成原项目的成熟爬虫逻辑
- 🛡️ **多数据源**：支持多个数据源并行爬取（政府信息公开平台、政策法规库）
- 🔄 **智能解析**：针对不同数据源的专用HTML解析器
- ⏱️ **时间过滤**：支持日期范围筛选，实现增量爬取
- 🔍 **关键词搜索**：支持关键词筛选或全量爬取
- ⚡ **可配置延迟**：支持设置请求延迟，保护目标服务器

#### 存储与备份
- 💾 **多格式存储**：自动保存JSON、Markdown、DOCX和原始文件
- ☁️ **S3存储支持**：可选配置AWS S3或兼容的对象存储服务
- 💾 **数据库备份**：PostgreSQL数据库备份和恢复功能
- 🔄 **自动清理**：支持清理旧文件和备份

#### 系统功能
- 🔐 **用户认证**：JWT Token认证和用户管理
- ⚙️ **系统配置**：灵活的功能开关和系统配置管理
- 📊 **实时监控**：任务进度实时更新和统计信息
- 🔔 **邮件通知**：任务完成/失败邮件通知（可选）
- 📱 **响应式设计**：支持不同屏幕尺寸，良好的移动端体验

#### 技术特性
- 🎨 **现代化UI**：基于Element Plus的美观界面设计
- 📦 **容器化部署**：支持Docker Compose一键部署
- 🔧 **数据库迁移**：使用Alembic管理数据库版本
- 📊 **数据流可视化**：完整的数据流和架构文档

## 🔗 相关项目

### 原爬虫项目
本项目使用的爬虫核心逻辑来自：

**Policy Crawler Pro** - 多数据源政策爬虫专业版
- 提供了成熟的爬虫核心逻辑
- 包含多数据源支持和HTML解析器
- 包含智能内容清洗和元信息提取功能
- 本项目在此基础上构建了完整的Web管理系统

### 项目关系

- **Policy Crawler Pro**: 本项目，支持多数据源的政策爬虫Web应用系统

## 🤝 贡献

欢迎提交Issue和Pull Request！

### CI/CD 状态

本项目使用 GitHub Actions 进行持续集成和部署：

- ✅ **自动构建**: 每次推送代码时自动构建 Docker 镜像
- ✅ **自动测试**: 运行后端和前端测试
- ✅ **安全扫描**: 使用 Trivy 进行安全漏洞扫描
- ✅ **自动发布**: 创建 Release 时自动构建并推送镜像到 GitHub Container Registry

### 镜像地址

所有 Docker 镜像已发布到 GitHub Container Registry：

- `ghcr.io/vivi141/policy-crawler-pro-backend:latest`
- `ghcr.io/vivi141/policy-crawler-pro-frontend:latest`
- `ghcr.io/vivi141/policy-crawler-pro-db:latest`

### 使用发布的镜像

```bash
# 拉取最新镜像
docker pull ghcr.io/vivi141/policy-crawler-pro-backend:latest
docker pull ghcr.io/vivi141/policy-crawler-pro-frontend:latest
docker pull ghcr.io/vivi141/policy-crawler-pro-db:latest

# 或使用特定版本
docker pull ghcr.io/vivi141/policy-crawler-pro-backend:v3.1.4
```

### GitHub 自动发布与部署

- 创建 Release 时，GitHub Actions 会自动构建并推送后端、前端、数据库镜像到 GHCR（标签与 Release 版本一致，并附带 latest）。
- 可在服务器上直接拉取指定版本镜像并通过 `docker-compose pull && docker-compose up -d` 完成滚动更新（先确保 `.env` 已配置好数据库和 JWT 等密钥）。
- CI 同步包含安全扫描、构建校验和健康检查，确保发布镜像可直接用于生产部署。

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至：747384120@qq.com

---

**感谢使用 Policy Crawler Pro！** 🎉
