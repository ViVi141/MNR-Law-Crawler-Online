export interface BackupRecord {
  id: number
  backup_type: string
  file_path: string
  file_size: number
  status: string
  error_message?: string
  created_at: string
  completed_at?: string
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

