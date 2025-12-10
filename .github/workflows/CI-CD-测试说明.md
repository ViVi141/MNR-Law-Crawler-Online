# CI/CD 测试说明

## 📋 测试工作流概览

本项目包含以下 CI/CD 工作流：

### 1. **CI/CD Pipeline** (`.github/workflows/ci.yml`)
- **触发时机**: Push 到 main/master/develop，PR，Release
- **功能**:
  - 构建并推送 Docker 镜像到 GHCR
  - 后端单元测试
  - 前端构建测试
  - 代码质量检查
  - 安全扫描

### 2. **Docker Compose Build Test** (`.github/workflows/docker-compose.yml`)
- **触发时机**: Push 到 main/master/develop，PR
- **功能**:
  - 构建所有 Docker 服务
  - 启动完整服务栈
  - 健康检查
  - 集成测试

### 3. **Integration Tests** (`.github/workflows/integration-test.yml`)
- **触发时机**: Push 到 main/master/develop，PR，手动触发
- **功能**:
  - 完整的 Docker Compose 集成测试
  - 网络隔离验证
  - 端口暴露验证
  - API 测试
  - 数据库连接测试

### 4. **Deploy** (`.github/workflows/deploy.yml`)
- **触发时机**: CI 完成后，手动触发
- **功能**:
  - 自动部署到服务器
  - 部署后健康检查

### 5. **Release** (`.github/workflows/release.yml`)
- **触发时机**: 发布 Release
- **功能**:
  - 构建并推送带版本标签的镜像

## 🔍 测试覆盖

### 后端测试
- ✅ 数据库连接测试
- ✅ 数据库迁移测试
- ✅ 应用导入测试
- ✅ 单元测试（如果存在）
- ✅ 代码质量检查（flake8, black, mypy）

### 前端测试
- ✅ 依赖安装测试
- ✅ Linter 检查
- ✅ 构建测试
- ✅ 构建产物验证

### Docker 测试
- ✅ 镜像构建测试
- ✅ 多平台构建（amd64, arm64）
- ✅ Docker Compose 启动测试
- ✅ 容器健康检查
- ✅ 网络隔离验证
- ✅ 端口暴露验证

### 集成测试
- ✅ 服务间通信测试
- ✅ API 端点测试
- ✅ 前端代理后端测试
- ✅ 数据库连接测试

### 安全测试
- ✅ 文件系统漏洞扫描（Trivy）
- ✅ Docker 镜像漏洞扫描
- ✅ 关键漏洞检测

## 🚀 测试执行流程

### 推送代码时
```
1. CI/CD Pipeline 启动
   ├─→ 构建 Docker 镜像
   ├─→ 后端测试
   ├─→ 前端测试
   └─→ 安全扫描

2. Docker Compose Build Test 启动
   ├─→ 构建服务
   ├─→ 启动服务
   ├─→ 健康检查
   └─→ 集成测试

3. Integration Tests 启动（可选）
   ├─→ 完整集成测试
   └─→ 网络和端口验证
```

### 创建 PR 时
- 所有测试工作流都会运行
- 必须通过所有测试才能合并

### 发布 Release 时
- 构建并推送带版本标签的镜像
- 自动生成 Release 说明

## 🔧 测试配置说明

### 端口配置
根据新的安全配置：
- **数据库**: 不暴露端口（仅内部网络）
- **后端**: 不暴露端口（仅内部网络）
- **前端**: 绑定到 `127.0.0.1:3000`（仅本地访问）

### 健康检查方式
1. **数据库**: 通过 Docker Compose 健康检查
2. **后端**: 通过容器内部访问 `http://localhost:8000/api/health`
3. **前端**: 通过 `http://127.0.0.1:3000/health`
4. **API 代理**: 通过 `http://127.0.0.1:3000/api/health`

### 网络验证
- 所有容器应在同一网络 (`app-network`)
- 数据库和后端端口不应暴露
- 前端端口应绑定到 localhost

## 📊 测试结果查看

### GitHub Actions
1. 进入仓库的 `Actions` 标签页
2. 查看各个工作流的运行状态
3. 点击具体运行查看详细日志

### 安全扫描结果
1. 进入仓库的 `Security` 标签页
2. 查看 `Code scanning alerts`
3. 查看 Trivy 扫描结果

## ⚠️ 常见问题

### Q: 测试失败怎么办？
A: 
1. 查看 GitHub Actions 日志
2. 检查错误信息
3. 本地运行相同测试：`docker-compose up -d && docker-compose ps`

### Q: 为什么后端端口无法访问？
A: 这是**正常的安全配置**。后端端口不暴露给主机，只能通过：
- 前端 Nginx 代理：`http://127.0.0.1:3000/api/xxx`
- 容器内部：`http://backend:8000/api/xxx`

### Q: 如何本地运行测试？
A:
```bash
# 运行 Docker Compose 测试
docker-compose up -d
docker-compose ps

# 运行后端测试
cd backend
pip install -r requirements.txt
pytest

# 运行前端测试
cd frontend
npm install
npm run lint
npm run build
```

### Q: 如何跳过某些测试？
A: 在提交信息中添加：
- `[skip ci]` - 跳过所有 CI
- `[skip tests]` - 跳过测试（需要配置）

## 🔄 持续改进

### 待添加的测试
- [ ] E2E 测试（Playwright/Cypress）
- [ ] 性能测试
- [ ] 负载测试
- [ ] 数据库迁移回滚测试
- [ ] 多环境测试（staging, production）

### 优化建议
- [ ] 并行运行测试以提高速度
- [ ] 添加测试覆盖率报告
- [ ] 添加性能基准测试
- [ ] 添加依赖更新自动化

---

**最后更新**: 2025-12-10

