import apiClient from './client'
import type { Task, TaskCreateRequest, TaskListResponse } from '../types/task'

export interface TaskListParams {
  page?: number
  page_size?: number
  task_type?: string
  status?: string
  completed_only?: boolean
}

export const tasksApi = {
  // 获取任务列表
  getTasks(params?: TaskListParams): Promise<TaskListResponse> {
    return apiClient.get('/api/tasks/', { params }).then((res) => res.data)
  },

  // 获取任务详情
  getTaskById(id: number): Promise<Task> {
    return apiClient.get(`/api/tasks/${id}`).then((res) => res.data)
  },

  // 创建任务
  createTask(data: TaskCreateRequest, autoStart: boolean = true): Promise<Task> {
    return apiClient.post(`/api/tasks/?auto_start=${autoStart}`, data).then((res) => res.data)
  },

  // 启动任务
  startTask(id: number): Promise<Task> {
    return apiClient.post(`/api/tasks/${id}/start`).then((res) => res.data)
  },

  // 停止任务（取消任务）
  stopTask(id: number): Promise<Task> {
    return apiClient.post(`/api/tasks/${id}/stop`).then((res) => res.data)
  },

  // 取消任务（别名）
  cancelTask(id: number): Promise<Task> {
    return apiClient.post(`/api/tasks/${id}/stop`).then((res) => res.data)
  },

  // 暂停任务
  pauseTask(id: number): Promise<Task> {
    return apiClient.post(`/api/tasks/${id}/pause`).then((res) => res.data)
  },

  // 恢复任务
  resumeTask(id: number): Promise<Task> {
    return apiClient.post(`/api/tasks/${id}/resume`).then((res) => res.data)
  },

  // 删除任务
  deleteTask(id: number): Promise<void> {
    return apiClient.delete(`/api/tasks/${id}`).then(() => undefined)
  },

  // 下载任务文件（打包成zip）
  downloadTaskFiles(
    id: number,
    fileFormat: 'all' | 'markdown' | 'docx' = 'all'
  ): Promise<Blob> {
    return apiClient
      .get(`/api/tasks/${id}/download`, {
        params: { file_format: fileFormat },
        responseType: 'blob',
      })
      .then((res) => res.data)
  },
}

