import type { TaskConfig, TaskResult } from './common'

export interface Task {
  id: number
  task_type: string
  task_name: string
  status: string
  progress: number
  config_json?: TaskConfig
  result_json?: TaskResult
  error_message?: string
  progress_message?: string  // 实时进度消息
  started_at?: string
  start_time?: string
  completed_at?: string
  end_time?: string
  created_at: string
  updated_at?: string
  policy_count?: number
  success_count?: number
  failed_count?: number
}

export interface TaskCreateRequest {
  task_type: string
  task_name: string
  config?: TaskConfig
}

export interface TaskListResponse {
  items: Task[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

