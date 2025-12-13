import apiClient from './client'
import type { BackupRecord, BackupListResponse, BackupRestoreRequest } from '../types/backup'

export interface BackupListParams {
  page?: number
  page_size?: number
  backup_type?: string
  status?: string
}

export const backupsApi = {
  // 获取备份列表
  getBackups(params?: BackupListParams): Promise<BackupListResponse> {
    // 转换参数：page -> skip, page_size -> limit
    const queryParams: Record<string, unknown> = {}
    
    if (params) {
      if (params.page !== undefined && params.page_size !== undefined) {
        queryParams.skip = (params.page - 1) * params.page_size
        queryParams.limit = params.page_size
      }
      if (params.backup_type) queryParams.backup_type = params.backup_type
      if (params.status) queryParams.status = params.status
    }
    
    return apiClient.get('/api/backups/', { params: queryParams }).then((res) => {
      const data = res.data
      // 转换响应格式：后端返回 skip/limit，前端期望 page/page_size
      if (data.skip !== undefined && data.limit !== undefined) {
        return {
          ...data,
          page: Math.floor(data.skip / data.limit) + 1,
          page_size: data.limit,
          total_pages: Math.ceil(data.total / data.limit)
        }
      }
      return data
    })
  },

  // 获取备份详情
  getBackupById(id: string): Promise<BackupRecord> {
    return apiClient.get(`/api/backups/${id}`).then((res) => res.data)
  },

  // 创建备份
  createBackup(data?: { backup_type?: string }): Promise<BackupRecord> {
    return apiClient.post('/api/backups/', data || {}).then((res) => res.data)
  },

  // 恢复备份
  restoreBackup(id: string, data?: BackupRestoreRequest): Promise<{ message: string }> {
    return apiClient.post(`/api/backups/${id}/restore`, data || {}).then((res) => res.data)
  },

  // 删除备份
  deleteBackup(id: string): Promise<void> {
    return apiClient.delete(`/api/backups/${id}`).then(() => undefined)
  },

  // 下载备份文件
  downloadBackup(id: string): Promise<Blob> {
    return apiClient
      .get(`/api/backups/${id}/download`, {
        responseType: 'blob',
      })
      .then((res) => res.data)
  },

  // 上传备份文件
  uploadBackup(file: File, backupName?: string): Promise<BackupRecord> {
    const formData = new FormData()
    formData.append('file', file)
    if (backupName) {
      formData.append('backup_name', backupName)
    }

    return apiClient.post('/api/backups/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }).then((res) => res.data)
  },

  // 清理旧备份
  cleanupBackups(data: { keep_count?: number }): Promise<{ deleted_count: number }> {
    return apiClient.post('/api/backups/cleanup', data).then((res) => res.data)
  },
}

