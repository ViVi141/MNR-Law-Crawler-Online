export interface BackupRecord {
  id: string
  backup_type: string
  s3_key?: string
  local_path?: string
  file_size?: number
  status: string
  start_time?: string
  end_time?: string
  error_message?: string
  created_at: string
  // 新增字段：备份来源信息
  source_type?: string // manual/task/scheduled
  source_id?: string // 关联的任务ID或定时任务ID
  source_name?: string // 备份时保存的任务名称
  source_deleted?: boolean // 来源是否已删除
  backup_strategy?: string // 备份策略
}

export interface BackupListResponse {
  items: BackupRecord[]
  backups?: BackupRecord[] // 向后兼容
  total: number
  skip: number
  limit: number
  page?: number
  page_size?: number
  total_pages?: number
}

export interface BackupRestoreRequest {
  confirm?: boolean
}

