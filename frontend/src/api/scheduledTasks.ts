import apiClient from './client'
import type {
  ScheduledTask,
  ScheduledTaskCreateRequest,
  ScheduledTaskListResponse,
} from '../types/scheduledTask'

export interface ScheduledTaskListParams {
  page?: number
  page_size?: number
  task_type?: string
  is_enabled?: boolean
}

export const scheduledTasksApi = {
  // 获取定时任务列表
  getScheduledTasks(params?: ScheduledTaskListParams): Promise<ScheduledTaskListResponse> {
    // 转换参数：page -> skip, page_size -> limit
    const queryParams: Record<string, unknown> = {}
    
    if (params) {
      if (params.page !== undefined && params.page_size !== undefined) {
        queryParams.skip = (params.page - 1) * params.page_size
        queryParams.limit = params.page_size
      }
      if (params.task_type) queryParams.task_type = params.task_type
      if (params.is_enabled !== undefined) queryParams.is_enabled = params.is_enabled
    }
    
    return apiClient.get('/api/scheduled-tasks/', { params: queryParams }).then((res) => {
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

  // 获取定时任务详情
  getScheduledTaskById(id: number): Promise<ScheduledTask> {
    return apiClient.get(`/api/scheduled-tasks/${id}`).then((res) => res.data)
  },

  // 创建定时任务
  createScheduledTask(data: ScheduledTaskCreateRequest): Promise<ScheduledTask> {
    return apiClient.post('/api/scheduled-tasks/', data).then((res) => res.data)
  },

  // 更新定时任务
  updateScheduledTask(
    id: number,
    data: Partial<ScheduledTaskCreateRequest>
  ): Promise<ScheduledTask> {
    return apiClient.put(`/api/scheduled-tasks/${id}`, data).then((res) => res.data)
  },

  // 删除定时任务
  deleteScheduledTask(id: number): Promise<void> {
    return apiClient.delete(`/api/scheduled-tasks/${id}`).then(() => undefined)
  },

  // 启用/禁用定时任务
  toggleScheduledTask(id: number, isEnabled: boolean): Promise<ScheduledTask> {
    if (isEnabled) {
      return apiClient
        .put(`/api/scheduled-tasks/${id}/enable`)
        .then((res) => res.data)
    } else {
      return apiClient
        .put(`/api/scheduled-tasks/${id}/disable`)
        .then((res) => res.data)
    }
  },

  // 获取调度器状态
  getSchedulerStatus(): Promise<{ enabled: boolean; running: boolean; message: string }> {
    return apiClient.get('/api/scheduled-tasks/status').then((res) => res.data)
  },
}

