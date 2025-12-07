-- 数据库初始化脚本
-- 创建扩展（用于全文搜索）

-- 1. pg_trgm扩展：模糊匹配和相似度搜索
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 2. zhparser扩展：中文分词支持
CREATE EXTENSION IF NOT EXISTS zhparser;

-- 3. 创建中文全文搜索配置
-- 使用jiebacfg作为配置名称（基于jieba分词）
CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS jiebacfg (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION jiebacfg ADD MAPPING FOR n,v,a,i,e,l WITH simple;

-- 验证中文分词是否正常工作（可选，用于测试）
-- SELECT ts_parse('zhparser', '自然资源管理政策法规');

