import type { Attachment } from './common'

export interface Policy {
  id: number
  title: string
  category: string
  publish_date: string
  effective_date?: string
  publisher: string
  doc_number?: string
  law_type?: string
  status?: string
  summary?: string
  content?: string
  keywords?: string[]
  attachments?: Attachment[]
  source_name?: string  // 数据源名称
  created_at: string
  updated_at: string
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

