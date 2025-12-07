-- 修复数据库：删除有问题的全文搜索索引
-- 这个索引会导致"index row size exceeds btree version 4 maximum"错误

-- 删除有问题的索引（如果存在）
DROP INDEX IF EXISTS idx_policies_fts;

-- 注意：全文搜索应该使用PostgreSQL的GIN索引和tsvector
-- 全文搜索功能在search_service中使用tsvector实现，不需要这个btree索引

