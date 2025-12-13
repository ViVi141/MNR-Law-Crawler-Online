<template>
  <div class="tasks-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>任务管理</h2>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建任务
          </el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :model="filterForm" inline class="filter-form">
        <el-form-item label="任务类型">
          <el-select v-model="filterForm.task_type" placeholder="全部类型" clearable>
            <el-option label="爬取任务" value="crawl_task" />
            <el-option label="备份任务" value="backup_task" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="待执行" value="pending" />
            <el-option label="运行中" value="running" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchTasks">筛选</el-button>
          <el-button @click="handleResetFilter">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 任务列表 -->
      <el-table v-loading="loading" :data="tasks" stripe style="width: 100%">
        <el-table-column prop="task_name" label="任务名称" min-width="200" />
        <el-table-column prop="task_type" label="任务类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.task_type === 'crawl_task' ? 'primary' : 'success'">
              {{ row.task_type === 'crawl_task' ? '爬取任务' : '备份任务' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="getProgressStatus(row.status)" />
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="180">
          <template #default="{ row }">
            {{ row.started_at ? formatDateTime(row.started_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="completed_at" label="完成时间" width="180">
          <template #default="{ row }">
            {{ row.completed_at ? formatDateTime(row.completed_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleViewDetail(row)">详情</el-button>
            <el-button
              v-if="row.status === 'completed' && row.task_type === 'crawl_task'"
              link
              type="success"
              :loading="downloading && downloadingTask?.id === row.id"
              :disabled="downloading"
              @click="handleDownloadTaskFiles(row)"
            >
              <el-icon v-if="!downloading || downloadingTask?.id !== row.id"><Download /></el-icon>
              {{ downloading && downloadingTask?.id === row.id ? '下载中...' : '下载文件' }}
            </el-button>
            <el-button
              v-if="row.status === 'running'"
              link
              type="warning"
              @click="handlePause(row)"
            >
              暂停
            </el-button>
            <el-button
              v-if="row.status === 'running'"
              link
              type="danger"
              @click="handleCancel(row)"
            >
              取消
            </el-button>
            <el-button
              v-if="row.status === 'paused'"
              link
              type="primary"
              @click="handleResume(row)"
            >
              恢复
            </el-button>
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

    <!-- 下载格式选择对话框 -->
    <el-dialog
      v-model="downloadFormatDialog"
      title="选择下载格式"
      width="400px"
    >
      <el-form label-width="120px">
        <el-form-item label="文件格式">
          <el-select v-model="downloadFormat" style="width: 100%">
            <el-option label="全部格式（Markdown + DOCX）" value="all" />
            <el-option label="仅 Markdown" value="markdown" />
            <el-option label="仅 DOCX" value="docx" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="downloadFormatDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmDownload">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 创建任务对话框 -->
    <TaskCreationForm
      v-model="showCreateDialog"
      :task-type="undefined"
      :disable-task-type-select="false"
      @submit="handleTaskSubmit"
      @cancel="showCreateDialog = false"
    />

    <!-- 任务详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="任务详情" width="900px" @close="stopTaskDetailRefresh">
      <div v-if="currentTask" class="task-detail">
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <el-tab-pane label="基本信息" name="info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="任务名称">{{ currentTask.task_name }}</el-descriptions-item>
              <el-descriptions-item label="任务类型">
                {{ currentTask.task_type === 'crawl_task' ? '爬取任务' : '备份任务' }}
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(currentTask.status)">
                  {{ getStatusText(currentTask.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="进度">
                <el-progress :percentage="currentTask.progress" :status="getProgressStatus(currentTask.status)" />
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">
                {{ currentTask.created_at ? formatDateTime(currentTask.created_at) : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ (currentTask.started_at || currentTask.start_time) ? formatDateTime((currentTask.started_at || currentTask.start_time || '')) : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="完成时间">
                {{ (currentTask.completed_at || currentTask.end_time) ? formatDateTime((currentTask.completed_at || currentTask.end_time || '')) : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="执行时长">
                {{ getDuration(currentTask.started_at || currentTask.start_time, currentTask.completed_at || currentTask.end_time) }}
              </el-descriptions-item>
              <el-descriptions-item v-if="currentTask.task_type === 'crawl_task'" label="统计信息" :span="2">
                <div class="stats">
                  <div class="stat-item">
                    <div class="stat-label">政策总数</div>
                    <div class="stat-value">{{ currentTask.result_json?.policy_count || currentTask.policy_count || 0 }}</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-label">成功保存</div>
                    <div class="stat-value" style="color: #67c23a">{{ currentTask.result_json?.success_count || currentTask.success_count || 0 }}</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-label">失败数量</div>
                    <div class="stat-value" style="color: #f56c6c">{{ currentTask.result_json?.failed_count || currentTask.failed_count || 0 }}</div>
                  </div>
                </div>
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="任务配置" name="config">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="配置信息">
                <pre class="config-json">{{ JSON.stringify(currentTask.config_json, null, 2) }}</pre>
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="执行结果" name="result">
            <div v-if="currentTask.result_json">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="政策总数">
                  {{ currentTask.result_json.policy_count || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="成功保存">
                  <span style="color: #67c23a">{{ currentTask.result_json.success_count || 0 }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="跳过数量">
                  <span style="color: #909399">{{ currentTask.result_json.skipped_count || 0 }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="失败数量">
                  <span style="color: #f56c6c">{{ currentTask.result_json.failed_count || 0 }}</span>
                </el-descriptions-item>
              </el-descriptions>
              <div v-if="currentTask.result_json.message" style="margin-top: 20px">
                <el-alert :title="currentTask.result_json.message" type="info" :closable="false" />
              </div>
            </div>
            <el-empty v-else description="暂无执行结果" />
          </el-tab-pane>
          
          <el-tab-pane v-if="currentTask.status === 'running' || currentTask.progress_message" label="实时进度" name="progress">
            <div class="progress-log-container">
              <div class="progress-log-header">
                <span>任务执行日志</span>
                <div>
                  <el-tag v-if="currentTask.status === 'running'" type="success" size="small">运行中</el-tag>
                  <el-tag v-else-if="currentTask.status === 'completed'" type="success" size="small">已完成</el-tag>
                  <el-tag v-else-if="currentTask.status === 'failed'" type="danger" size="small">失败</el-tag>
                  <el-tag v-else-if="currentTask.status === 'paused'" type="warning" size="small">已暂停</el-tag>
                  <el-tag v-else-if="currentTask.status === 'cancelled'" type="info" size="small">已取消</el-tag>
                </div>
              </div>
              <div class="progress-log-content" ref="progressLogContentRef">
                <pre v-if="currentTask.progress_message" class="progress-log">{{ currentTask.progress_message }}</pre>
                <el-empty v-else description="暂无进度信息" />
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane v-if="currentTask.error_message" label="错误信息" name="error">
            <el-alert type="error" :closable="false">
              <pre class="error-message">{{ currentTask.error_message }}</pre>
            </el-alert>
          </el-tab-pane>
        </el-tabs>
        
        <div class="task-actions" style="margin-top: 20px; text-align: right">
          <el-button v-if="currentTask.status === 'pending'" type="primary" @click="handleStartTask(currentTask)">
            启动任务
          </el-button>
          <el-button v-if="currentTask.status === 'running'" type="warning" @click="handlePause(currentTask)">
            暂停任务
          </el-button>
          <el-button v-if="currentTask.status === 'running'" type="danger" @click="handleCancel(currentTask)">
            取消任务
          </el-button>
          <el-button v-if="currentTask.status === 'paused'" type="primary" @click="handleResume(currentTask)">
            恢复任务
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download } from '@element-plus/icons-vue'
import TaskCreationForm from '../components/TaskCreationForm.vue'
import { tasksApi, type TaskListParams } from '../api/tasks'
import type { Task, TaskCreateRequest } from '../types/task'
import type { TaskConfig } from '../types/common'

// 任务表单数据类型
interface TaskFormData {
  task_type: string
  task_name: string
  config: TaskConfig
  autoStart?: boolean
  [key: string]: unknown
}
import type { ApiError } from '../types/common'
import dayjs from 'dayjs'

const loading = ref(false)
const creating = ref(false)
const tasks = ref<Task[]>([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const currentTask = ref<Task | null>(null)
const activeTab = ref('info')
const progressLogContentRef = ref<HTMLElement | null>(null)
let taskDetailRefreshInterval: ReturnType<typeof setInterval> | null = null

const filterForm = reactive({
  task_type: '',
  status: '',
})

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
    pending: 'info',
    running: 'primary',
    paused: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info',
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待执行',
    running: '运行中',
    paused: '已暂停',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
  }
  return statusMap[status] || status
}

const getProgressStatus = (status: string): 'success' | 'exception' | undefined => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  if (status === 'running') return undefined
  return undefined
}

const fetchTasks = async () => {
  loading.value = true
  try {
    const params: TaskListParams = {
      page: pagination.page,
      page_size: pagination.pageSize,
    }
    if (filterForm.task_type) params.task_type = filterForm.task_type
    if (filterForm.status) params.status = filterForm.status

    const response = await tasksApi.getTasks(params)
    tasks.value = response.items
    pagination.total = response.total
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '获取任务列表失败')
  } finally {
    loading.value = false
  }
}

const handleResetFilter = () => {
  filterForm.task_type = ''
  filterForm.status = ''
  fetchTasks()
}

const handleSizeChange = () => {
  fetchTasks()
}

const handlePageChange = () => {
  fetchTasks()
}

const handleTaskSubmit = async (formData: TaskFormData) => {
  creating.value = true
  try {
    const request: TaskCreateRequest = {
      task_type: formData.task_type,
      task_name: formData.task_name,
      config: formData.config,
    }

    await tasksApi.createTask(request, formData.autoStart)
    ElMessage.success('任务创建成功')
    showCreateDialog.value = false
    fetchTasks()
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '创建任务失败')
  } finally {
    creating.value = false
  }
}

const handleViewDetail = async (task: Task) => {
  try {
    currentTask.value = await tasksApi.getTaskById(task.id)
    showDetailDialog.value = true
    
    // 如果任务正在运行，自动切换到进度标签页并开始刷新
    if (task.status === 'running') {
      activeTab.value = 'progress'
      startTaskDetailRefresh(task.id)
    } else {
      activeTab.value = 'info'
    }
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '获取任务详情失败')
  }
}

const handleTabChange = (tabName: string) => {
  // 切换到进度标签页时，如果是运行中的任务，确保开始刷新
  if (tabName === 'progress' && currentTask.value?.status === 'running') {
    if (currentTask.value) {
      startTaskDetailRefresh(currentTask.value.id)
      // 滚动到底部显示最新进度
      scrollToBottom()
    }
  }
}

const scrollToBottom = () => {
  // 自动滚动进度日志到底部
  nextTick(() => {
    if (progressLogContentRef.value) {
      progressLogContentRef.value.scrollTop = progressLogContentRef.value.scrollHeight
    }
  })
}

const startTaskDetailRefresh = (taskId: number) => {
  stopTaskDetailRefresh()
  taskDetailRefreshInterval = setInterval(async () => {
    try {
      const updated = await tasksApi.getTaskById(taskId)
      if (currentTask.value) {
        const oldProgressMessage = currentTask.value.progress_message
        Object.assign(currentTask.value, updated)
        // 如果进度消息有更新且正在查看进度标签页，滚动到底部
        if (updated.progress_message && updated.progress_message !== oldProgressMessage && activeTab.value === 'progress') {
          scrollToBottom()
        }
        // 如果任务已完成或失败，停止刷新
        if (updated.status === 'completed' || updated.status === 'failed' || updated.status === 'cancelled' || updated.status === 'paused') {
          stopTaskDetailRefresh()
        }
      }
    } catch (error) {
      console.error('刷新任务详情失败:', error)
      stopTaskDetailRefresh()
    }
  }, 2000)
}

// 监听进度消息变化，自动滚动到底部
watch(() => currentTask.value?.progress_message, () => {
  if (activeTab.value === 'progress') {
    scrollToBottom()
  }
})

const stopTaskDetailRefresh = () => {
  if (taskDetailRefreshInterval) {
    clearInterval(taskDetailRefreshInterval)
    taskDetailRefreshInterval = null
  }
}

const handleStartTask = async (task: Task) => {
  try {
    await tasksApi.startTask(task.id)
    ElMessage.success('任务已启动')
    await handleViewDetail(task)
    fetchTasks()
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '启动任务失败')
  }
}

const getDuration = (start: string | undefined, end: string | undefined) => {
  if (!start) return '-'
  const endTime = end ? dayjs(end) : dayjs()
  const duration = endTime.diff(dayjs(start), 'second')
  if (duration < 60) return `${duration}秒`
  if (duration < 3600) return `${Math.floor(duration / 60)}分${duration % 60}秒`
  return `${Math.floor(duration / 3600)}小时${Math.floor((duration % 3600) / 60)}分`
}

const handlePause = async (task: Task) => {
  try {
    await ElMessageBox.confirm('确定要暂停这个任务吗？暂停后可以恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await tasksApi.pauseTask(task.id)
    ElMessage.success('任务已暂停')
    if (currentTask.value && currentTask.value.id === task.id) {
      await handleViewDetail(task)
    }
    fetchTasks()
  } catch (error) {
    if (typeof error === 'string' && error === 'cancel') {
      return
    }
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '暂停任务失败')
  }
}

const handleResume = async (task: Task) => {
  try {
    await tasksApi.resumeTask(task.id)
    ElMessage.success('任务已恢复')
    if (currentTask.value && currentTask.value.id === task.id) {
      await handleViewDetail(task)
    }
    fetchTasks()
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '恢复任务失败')
  }
}

const handleCancel = async (task: Task) => {
  try {
    await ElMessageBox.confirm('确定要取消这个任务吗？取消后将无法恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await tasksApi.stopTask(task.id)
    ElMessage.success('任务已取消')
    if (currentTask.value && currentTask.value.id === task.id) {
      await handleViewDetail(task)
    }
    fetchTasks()
  } catch (error) {
    if (typeof error === 'string' && error === 'cancel') {
      return
    }
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '取消任务失败')
  }
}

const downloadFormatDialog = ref(false)
const downloadFormat = ref<'all' | 'markdown' | 'docx'>('all')
const downloadingTask = ref<Task | null>(null)
const downloading = ref(false)

const handleDownloadTaskFiles = async (task: Task) => {
  // 显示格式选择对话框
  downloadingTask.value = task
  downloadFormat.value = 'all'
  downloadFormatDialog.value = true
}

const confirmDownload = async () => {
  if (!downloadingTask.value) {
    return
  }
  
  downloadFormatDialog.value = false
  downloading.value = true
  
  let loadingInstance: ReturnType<typeof ElMessage> | null = null
  
  try {
    // 显示加载提示
    loadingInstance = ElMessage({
      message: '正在打包文件，请稍候...',
      type: 'info',
      duration: 0, // 不自动关闭
      showClose: false,
    })
    
    // 调用下载API
    const blob = await tasksApi.downloadTaskFiles(downloadingTask.value.id, downloadFormat.value)
    
    // 关闭加载提示
    if (loadingInstance) {
      loadingInstance.close()
      loadingInstance = null
    }
    
    // 检查文件大小
    const fileSize = blob.size
    const fileSizeMB = (fileSize / (1024 * 1024)).toFixed(2)
    
    if (fileSize === 0) {
      ElMessage.warning('下载的文件为空，可能没有可用的文件')
      return
    }
    
    // 显示文件大小信息
    ElMessage({
      message: `文件打包完成，大小: ${fileSizeMB} MB，开始下载...`,
      type: 'success',
      duration: 3000,
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 生成文件名（清理特殊字符）
    const timestamp = dayjs().format('YYYYMMDD_HHmmss')
    const formatSuffix = downloadFormat.value === 'all' ? 'all' : downloadFormat.value
    const safeTaskName = downloadingTask.value.task_name
      .replace(/[<>:"/\\|?*]/g, '_')
      .replace(/\s+/g, '_')
      .substring(0, 50)
    link.download = `${safeTaskName}_${formatSuffix}_${timestamp}.zip`
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    // 延迟释放URL对象，确保下载开始
    setTimeout(() => {
      window.URL.revokeObjectURL(url)
    }, 100)
    
    ElMessage.success('文件下载成功')
  } catch (error) {
    // 关闭加载提示
    if (loadingInstance) {
      loadingInstance.close()
      loadingInstance = null
    }
    
    const apiError = error as ApiError
    const errorMessage = apiError.response?.data?.detail || apiError.message || '下载文件失败'
    ElMessage.error(errorMessage)
    console.error('下载文件失败:', error)
  } finally {
    downloading.value = false
    downloadingTask.value = null
  }
}

const handleDelete = async (task: Task) => {
  try {
    const message = task.status === 'running' 
      ? '任务正在运行中，删除前将自动停止。确定要删除这个任务吗？' 
      : '确定要删除这个任务吗？删除后将无法恢复。'
    
    await ElMessageBox.confirm(message, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await tasksApi.deleteTask(task.id)
    ElMessage.success('任务已删除')
    if (showDetailDialog.value && currentTask.value?.id === task.id) {
      showDetailDialog.value = false
    }
    fetchTasks()
  } catch (error) {
    if (typeof error === 'string' && error === 'cancel') {
      return
    }
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '删除任务失败')
  }
}

let refreshInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  fetchTasks()
  // 定时刷新任务列表
  refreshInterval = setInterval(() => {
    fetchTasks()
  }, 5000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  stopTaskDetailRefresh()
})
</script>

<style lang="scss" scoped>
.tasks-page {
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

  .filter-form {
    margin-bottom: 20px;
    padding: 20px;
    background-color: #f5f7fa;
    border-radius: 4px;

    :deep(.el-form-item) {
      margin-bottom: 10px;
    }

    // 修复筛选框过小的问题
    :deep(.el-select) {
      min-width: 160px;

      // 确保下拉选项也能正常显示
      .el-select__tags {
        max-width: 120px;
      }
    }

    // 任务类型和状态筛选框特殊处理
    :deep(.el-form-item:nth-child(1) .el-select),
    :deep(.el-form-item:nth-child(2) .el-select) {
      min-width: 180px;
    }
  }

  pre {
    background-color: #f5f7fa;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
    max-height: 300px;
    overflow-y: auto;
    word-wrap: break-word;
    white-space: pre-wrap;
  }
  
  .task-detail {
    .stats {
      display: flex;
      gap: 30px;
      margin-top: 10px;
      padding: 15px;
      background-color: #f5f7fa;
      border-radius: 4px;
      
      .stat-item {
        text-align: center;
        
        .stat-label {
          font-size: 12px;
          color: #909399;
          margin-bottom: 8px;
        }
        
        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: #303133;
        }
      }
    }
    
    .config-json {
      background-color: #f5f7fa;
      padding: 15px;
      border-radius: 4px;
      overflow-x: auto;
      max-height: 400px;
      overflow-y: auto;
      font-size: 12px;
      line-height: 1.6;
    }
    
    .error-message {
      margin: 0;
      white-space: pre-wrap;
      word-wrap: break-word;
    }
    
    .help-text {
      margin-left: 10px;
      font-size: 12px;
      color: #909399;
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
}

// 响应式设计
@media (max-width: 768px) {
  .tasks-page {
    .filter-form {
      padding: 15px;
      
      :deep(.el-form-item) {
        width: 100%;
        margin-right: 0;
      }
    }
    
    .card-header {
      h2 {
        font-size: 18px;
      }
    }
  }
}
</style>

