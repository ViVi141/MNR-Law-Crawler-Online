import type { TaskConfig } from './common'

export interface ScheduledTaskListItem {
  id: number
  task_type: string
  task_name: string
  cron_expression: string
  is_enabled: boolean
  next_run_time?: string
  last_run_time?: string
  last_run_status?: string
  created_at: string
}

export interface ScheduledTask extends ScheduledTaskListItem {
  config_json?: TaskConfig
  updated_at?: string
}

export interface ScheduledTaskCreateRequest {
  task_type: string
  task_name: string
  cron_expression: string
  config: TaskConfig  // 后端要求必需，不能为可选
  is_enabled?: boolean
}

export interface ScheduledTaskListResponse {
  items: ScheduledTaskListItem[]
  total: number
  skip: number
  limit: number
}
