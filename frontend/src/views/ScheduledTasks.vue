<template>
  <div class="scheduled-tasks-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>定时任务管理</h2>
          <el-button
            type="primary"
            :disabled="!schedulerEnabled"
            @click="showCreateDialog = true"
          >
            <el-icon><Plus /></el-icon>
            新建定时任务
          </el-button>
        </div>
      </template>

      <!-- 调度器状态提示 -->
      <el-alert
        v-if="!schedulerEnabled"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <template #title>
          <span>定时任务功能未启用</span>
        </template>
        <template #default>
          <span>
            定时任务功能当前未启用，无法创建和管理定时任务。请在
            <router-link to="/settings">系统设置</router-link>
            中启用定时任务功能。
          </span>
        </template>
      </el-alert>

      <!-- 任务列表 -->
      <el-table v-loading="loading" :data="scheduledTasks" stripe style="width: 100%">
        <el-table-column prop="task_name" label="任务名称" min-width="200" />
        <el-table-column prop="task_type" label="任务类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.task_type === 'crawl_task' ? 'primary' : 'success'">
              {{ row.task_type === 'crawl_task' ? '爬取任务' : '备份任务' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cron_expression" label="Cron表达式" width="150" />
        <el-table-column prop="is_enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_enabled"
              :loading="row._toggling"
              @change="handleToggle(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="next_run_time" label="下次运行时间" width="180">
          <template #default="{ row }">
            {{ row.next_run_time ? formatDateTime(row.next_run_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="last_run_time" label="上次运行时间" width="180">
          <template #default="{ row }">
            {{ row.last_run_time ? formatDateTime(row.last_run_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="last_run_status" label="上次运行状态" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.last_run_status" :type="getStatusType(row.last_run_status)">
              {{ getStatusText(row.last_run_status) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <TaskCreationForm
      v-model="showCreateDialog"
      :mode="editingTask ? 'edit' : 'create'"
      task-type="scheduled_task"
      :disable-task-type-select="false"
      :edit-data="editingTask"
      @submit="handleScheduledTaskSubmit"
      @cancel="handleCancelDialog"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import TaskCreationForm from '../components/TaskCreationForm.vue'
import { scheduledTasksApi } from '../api/scheduledTasks'
import type {
  ScheduledTask,
  ScheduledTaskCreateRequest,
  ScheduledTaskListItem,
} from '../types/scheduledTask'
import type { TaskConfig } from '../types/common'

// 定时任务表单数据类型
interface ScheduledTaskFormData {
  scheduled_task_type: string
  task_name: string
  cron_expression: string
  config: TaskConfig
  is_enabled: boolean
  [key: string]: unknown
}
import type { ApiError } from '../types/common'
import dayjs from 'dayjs'

const loading = ref(false)
const saving = ref(false)
const scheduledTasks = ref<ScheduledTask[]>([])
const showCreateDialog = ref(false)
const editingTask = ref<ScheduledTask | undefined>(undefined)
const schedulerEnabled = ref(false)
const schedulerRunning = ref(false)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const formatDateTime = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    success: 'success',
    failed: 'danger',
    running: 'warning',
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    success: '成功',
    failed: '失败',
    running: '运行中',
  }
  return statusMap[status] || status
}


const fetchTasks = async () => {
  loading.value = true
  try {
    const response = await scheduledTasksApi.getScheduledTasks({
      page: pagination.page,
      page_size: pagination.pageSize,
    })
    // 将ScheduledTaskListItem转换为ScheduledTask格式
    scheduledTasks.value = response.items.map((task: ScheduledTaskListItem) => ({
      ...task,
      config_json: (task as ScheduledTask).config_json || {},
      _toggling: false,
    }))
    pagination.total = response.total || 0
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '获取定时任务列表失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = () => {
  pagination.page = 1
  fetchTasks()
}

const handlePageChange = () => {
  fetchTasks()
}

const handleToggle = async (task: ScheduledTask & { _toggling: boolean }) => {
  task._toggling = true
  const oldEnabled = task.is_enabled
  try {
    await scheduledTasksApi.toggleScheduledTask(task.id, task.is_enabled)
    ElMessage.success(task.is_enabled ? '任务已启用' : '任务已禁用')
    // 重新获取任务列表以同步状态
    await fetchTasks()
    // 如果启用了任务但调度器未启用，更新调度器状态提示
    if (task.is_enabled && !schedulerEnabled.value) {
      await checkSchedulerStatus(false)
    }
  } catch (error) {
    // 操作失败，恢复原状态
    task.is_enabled = oldEnabled
    const apiError = error as ApiError
    const errorMessage = apiError.response?.data?.detail || '操作失败'
    ElMessage.error(errorMessage)
    // 如果是调度器未启用的错误，更新状态提示
    if (errorMessage.includes('定时任务功能未启用')) {
      await checkSchedulerStatus(false)
    }
  } finally {
    task._toggling = false
  }
}

const handleEdit = (task: ScheduledTask) => {
  editingTask.value = task
  showCreateDialog.value = true
}

const handleDelete = async (task: ScheduledTask) => {
  try {
    await ElMessageBox.confirm('确定要删除这个定时任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await scheduledTasksApi.deleteScheduledTask(task.id)
    ElMessage.success('任务已删除')
    await fetchTasks()
  } catch (error) {
    // ElMessageBox.confirm 取消时会抛出 'cancel' 字符串
    if (typeof error === 'string' && error === 'cancel') {
      return
    }
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '删除任务失败')
  }
}

const handleCancelDialog = () => {
  showCreateDialog.value = false
  editingTask.value = undefined
}

const handleScheduledTaskSubmit = async (formData: ScheduledTaskFormData) => {
  // 防止重复提交
  if (saving.value) {
    return
  }
  
  saving.value = true
  try {
    if (editingTask.value) {
      // 更新定时任务
      const updateRequest: ScheduledTaskCreateRequest = {
        task_type: formData.scheduled_task_type,
        task_name: formData.task_name,
        cron_expression: formData.cron_expression,
        config: formData.config,
        is_enabled: formData.is_enabled,
      }
      await scheduledTasksApi.updateScheduledTask(editingTask.value.id, updateRequest)
      ElMessage.success('任务已更新')
    } else {
      // 创建定时任务
      const createRequest: ScheduledTaskCreateRequest = {
        task_type: formData.scheduled_task_type,
        task_name: formData.task_name,
        cron_expression: formData.cron_expression,
        config: formData.config,
        is_enabled: formData.is_enabled,
      }
      await scheduledTasksApi.createScheduledTask(createRequest)
      ElMessage.success('任务已创建')
    }

    handleCancelDialog()
    // 重新获取任务列表和调度器状态
    await Promise.all([fetchTasks(), checkSchedulerStatus(false)])
  } catch (error) {
    const apiError = error as ApiError
    
    // 处理验证错误（422）
    if (apiError.response?.status === 422) {
      const validationErrors = apiError.response?.data?.detail
      if (Array.isArray(validationErrors)) {
        const errorMessages = validationErrors.map((err: any) => {
          const loc = Array.isArray(err.loc) ? err.loc.join('.') : err.loc
          return `${loc}: ${err.msg}`
        }).join('\n')
        ElMessage.error(`验证失败:\n${errorMessages}`)
      } else if (typeof validationErrors === 'string') {
        ElMessage.error(validationErrors)
      } else {
        ElMessage.error(JSON.stringify(validationErrors) || '请求数据验证失败')
      }
    } else {
      const errorMessage = apiError.response?.data?.detail || apiError.message || '保存失败'
      ElMessage.error(errorMessage)
      // 如果是调度器未启用的错误，更新状态提示
      if (errorMessage.includes('定时任务功能未启用')) {
        await checkSchedulerStatus(false)
      }
    }
  } finally {
    saving.value = false
  }
}

let statusCheckInProgress = false
let lastStatusCheckTime = 0
const STATUS_CHECK_INTERVAL = 2000 // 2秒内只检查一次

const checkSchedulerStatus = async (force = false) => {
  // 防止频繁检查
  const now = Date.now()
  if (!force && (statusCheckInProgress || (now - lastStatusCheckTime < STATUS_CHECK_INTERVAL))) {
    return
  }
  
  statusCheckInProgress = true
  lastStatusCheckTime = now
  
  try {
    const status = await scheduledTasksApi.getSchedulerStatus()
    schedulerEnabled.value = status.enabled
    schedulerRunning.value = status.running
  } catch (error) {
    // 获取失败时保持现有状态，避免误判为未启用
  } finally {
    statusCheckInProgress = false
  }
}

onMounted(() => {
  // 初始化时强制检查状态
  checkSchedulerStatus(true)
  fetchTasks()
})
</script>

<style lang="scss" scoped>
.scheduled-tasks-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin: 0;
      font-size: 20px;
    }
  }

}

.scheduled-tasks-page {
  width: 100%;
  min-height: 100%;
  
  :deep(.el-card) {
    height: 100%;
    display: flex;
    flex-direction: column;
    
    .el-card__body {
      flex: 1;
      overflow-y: auto;
      min-height: 0;
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    
    h2 {
      margin: 0;
      font-size: 20px;
    }
  }
  
  // 响应式表格
  :deep(.el-table) {
    .el-table__body-wrapper {
      overflow-x: auto;
    }
  }
  
  // 对话框内容滚动
  :deep(.el-dialog__body) {
    max-height: 70vh;
    overflow-y: auto;
  }
  
  // 分页器
  :deep(.el-pagination) {
    margin-top: 20px;
    justify-content: flex-end;
    flex-wrap: wrap;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .scheduled-tasks-page {
    .card-header {
      h2 {
        font-size: 18px;
      }
    }
  }
}
</style>

