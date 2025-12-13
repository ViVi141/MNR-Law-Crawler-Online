import type { Attachment } from './common'

export interface Policy {
  id: number
  title: string
  category: string
  publishDate: string  // 对应后端pub_date，更清晰的字段名
  effectiveDate?: string  // 对应后端effective_date
  publisher?: string  // 可选字段，因为某些数据源可能为空
  docNumber?: string  // 对应后端doc_number，更清晰的字段名
  lawLevel?: string  // 对应后端level，效力级别
  validity?: string  // 有效性（如：部门规范性文件、行政法规等）
  status?: string
  summary?: string
  content?: string
  keywords?: string[]
  attachments?: Attachment[]
  sourceName?: string  // 数据源名称，对应后端source_name
  sourceUrl?: string  // 数据源URL，对应后端source_url
  createdAt: string  // 对应后端created_at
  updatedAt: string  // 对应后端updated_at
  // 向后兼容字段
  publish_date?: string  // 兼容旧字段名
  effective_date?: string  // 兼容旧字段名
  doc_number?: string  // 兼容旧字段名
  law_type?: string  // 兼容旧字段名
  source_name?: string  // 兼容旧字段名
  source_url?: string  // 兼容旧字段名
  created_at?: string  // 兼容旧字段名
  updated_at?: string  // 兼容旧字段名
}

// Attachment类型已移到common.ts

export interface PolicySearchParams {
  page?: number
  page_size?: number
  keyword?: string
  category?: string
  publisher?: string
  level?: string  // 效力级别
  start_date?: string
  end_date?: string
  law_type?: string
  status?: string
  source_name?: string  // 数据源名称
  task_id?: number  // 任务ID筛选
}

export interface PolicyListResponse {
  items: Policy[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

