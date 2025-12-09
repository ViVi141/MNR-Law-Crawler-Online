-- 数据库初始化脚本
-- 创建扩展（用于全文搜索）

-- pg_trgm扩展：模糊匹配和相似度搜索
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

