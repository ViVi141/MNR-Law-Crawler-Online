# MNR Law Crawler - 前端项目

## 项目简介

这是MNR法规爬虫系统的Vue 3前端应用，提供了政策管理、任务管理、配置管理等功能的Web界面。

## 技术栈

- Vue 3 (Composition API)
- TypeScript
- Pinia (状态管理)
- Vue Router (路由)
- Element Plus (UI组件库)
- Axios (HTTP客户端)
- Vite (构建工具)

## 开发环境设置

### 前置要求

- Node.js >= 16.x
- npm 或 yarn

### 安装依赖

```bash
cd frontend
npm install
```

### 环境变量配置

创建 `.env` 文件（参考 `.env.example`）：

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/src/
├── api/              # API客户端封装
│   ├── auth.ts      # 认证API
│   ├── policies.ts  # 政策API
│   ├── tasks.ts     # 任务API
│   ├── config.ts    # 配置API
│   └── client.ts    # Axios实例和拦截器
├── layouts/         # 布局组件
│   └── MainLayout.vue
├── router/          # 路由配置
│   └── index.ts
├── stores/          # Pinia状态管理
│   └── auth.ts
├── styles/          # 全局样式
│   └── main.scss
├── types/           # TypeScript类型定义
├── views/           # 页面组件
│   ├── Login.vue
│   ├── Policies.vue
│   ├── PolicyDetail.vue
│   ├── Tasks.vue
│   ├── ScheduledTasks.vue
│   ├── Settings.vue
│   └── Backups.vue
├── App.vue          # 根组件
└── main.ts          # 入口文件
```

## 功能模块

### 认证模块
- 用户登录
- JWT Token管理
- 路由守卫

### 政策管理
- 政策列表展示
- 政策搜索和筛选
- 政策详情查看
- 政策文件下载（Markdown/JSON/DOCX）

### 任务管理
- 创建爬取任务
- 任务列表和状态监控
- 任务取消和删除
- 实时进度显示

### 定时任务管理
- 创建/编辑定时任务
- Cron表达式配置
- 任务启用/禁用
- 运行历史查看

### 系统设置
- 功能开关管理
- S3存储配置
- 邮件服务配置
- 配置测试功能

### 备份管理
- 备份列表
- 创建备份
- 恢复备份
- 清理旧备份

## 开发注意事项

1. **API调用**: 所有API调用都通过 `src/api/` 目录下的封装函数进行
2. **类型安全**: 使用TypeScript确保类型安全，类型定义在 `src/types/` 目录
3. **状态管理**: 使用Pinia管理全局状态（如用户认证信息）
4. **路由守卫**: 在 `router/index.ts` 中配置了认证路由守卫
5. **错误处理**: API错误统一在 `api/client.ts` 的响应拦截器中处理

## 代码规范

- 使用TypeScript严格模式
- 使用ESLint进行代码检查
- 遵循Vue 3 Composition API最佳实践
- 组件使用 `<script setup>` 语法

## 常见问题

### 1. API连接失败

检查：
- 后端服务是否已启动
- `.env` 文件中的 `VITE_API_BASE_URL` 配置是否正确
- 后端CORS配置是否允许前端域名

### 2. 登录后跳转问题

- 确保token已正确保存到localStorage
- 检查路由守卫逻辑是否正确

### 3. 类型错误

- 确保所有API响应的类型定义与后端一致
- 检查 `src/types/` 目录中的类型定义

## 许可证

与主项目保持一致

