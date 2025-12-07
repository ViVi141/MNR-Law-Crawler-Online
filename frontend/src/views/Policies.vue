<template>
  <div class="policies-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>政策列表</h2>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="任务筛选" required>
          <el-select
            v-model="selectedTaskId"
            placeholder="请选择任务"
            clearable
            style="width: 280px"
            @change="handleTaskChange"
          >
            <el-option
              v-for="task in completedTasks"
              :key="task.id"
              :label="`${task.task_name} (${formatTaskDate(task.created_at)})`"
              :value="task.id"
            />
          </el-select>
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            <span v-if="selectedTaskId">当前显示该任务爬取的政策</span>
            <span v-else style="color: #f56c6c;">请先选择任务以查看政策</span>
          </div>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索政策标题或内容"
            clearable
            style="width: 300px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="数据源">
          <el-select
            v-model="searchForm.source_name"
            placeholder="全部数据源"
            clearable
            style="width: 180px"
            @change="handleDataSourceChange"
          >
            <el-option
              v-for="source in availableSourceNames"
              :key="source"
              :label="source"
              :value="source"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            v-model="searchForm.category"
            placeholder="全部分类"
            clearable
            style="width: 150px"
            :disabled="!searchForm.source_name && availableSourceNames.length > 0"
          >
            <el-option
              v-for="category in availableCategories"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
          <div v-if="!searchForm.source_name && availableSourceNames.length > 0" style="font-size: 12px; color: #909399; margin-top: 5px;">
            请先选择数据源以查看对应分类
          </div>
        </el-form-item>
        <el-form-item label="发布机构">
          <el-input
            v-model="searchForm.publisher"
            placeholder="发布机构"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="发布日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="handleDateRangeChange"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 政策列表 -->
      <el-table
        v-loading="loading"
        :data="policies"
        stripe
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column prop="title" label="标题" min-width="300" show-overflow-tooltip />
        <el-table-column prop="category_display" label="数据源-分类" width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.category_display">{{ row.category_display }}</span>
            <span v-else-if="row.source_name && row.category">
              {{ row.category === '全部' ? row.source_name : `${row.source_name}-${row.category}` }}
            </span>
            <span v-else-if="row.category">{{ row.category }}</span>
            <span v-else-if="row.source_name">{{ row.source_name }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="publisher" label="发布机构" width="150" show-overflow-tooltip />
        <el-table-column prop="doc_number" label="文号" width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.doc_number">{{ row.doc_number }}</span>
            <span v-else style="color: #c0c4cc;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="publish_date" label="发布日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.publish_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="law_type" label="效力级别" width="140" show-overflow-tooltip />
        <el-table-column prop="validity" label="有效性" width="140" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag v-if="row.validity" size="small" type="info">{{ row.validity }}</el-tag>
            <span v-else style="color: #c0c4cc;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="handleViewDetail(row)">
              查看详情
            </el-button>
            <el-dropdown @command="(cmd: string) => handleDownload(row, cmd)">
              <el-button link type="primary">
                下载 <el-icon><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="markdown">Markdown</el-dropdown-item>
                  <el-dropdown-item command="json">JSON</el-dropdown-item>
                  <el-dropdown-item command="docx">DOCX</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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

    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="showCreateTaskDialog"
      title="创建爬取任务"
      width="600px"
      @close="Object.assign(taskForm, { task_name: '', keywords: '', date_range: null })"
    >
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务名称" required>
          <el-input v-model="taskForm.task_name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="taskForm.keywords"
            type="textarea"
            :rows="3"
            placeholder="多个关键词用逗号分隔，留空表示爬取全部"
          />
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="taskForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateTaskDialog = false">取消</el-button>
        <el-button type="primary" :loading="taskCreating" @click="handleCreateTask">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, ArrowDown } from '@element-plus/icons-vue'
import { policiesApi } from '../api/policies'
import { tasksApi } from '../api/tasks'
import type { Policy, PolicySearchParams } from '../types/policy'
import type { TaskCreateRequest } from '../types/task'
import type { ApiError } from '../types/common'
import type { CrawlTaskConfig } from '../types/common'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const policies = ref<Policy[]>([])
const availableSourceNames = ref<string[]>([])
const availableCategories = ref<string[]>([])
const completedTasks = ref<Array<{ id: number; task_name: string; created_at: string }>>([])
const selectedTaskId = ref<number | null>(null)
const tasksLoading = ref(false)

const searchForm = reactive<PolicySearchParams>({
  keyword: '',
  category: '',
  publisher: '',
  start_date: '',
  end_date: '',
  source_name: '',
  task_id: undefined,
})

const dateRange = ref<[string, string] | null>(null)
const showCreateTaskDialog = ref(false)
const taskCreating = ref(false)

const taskForm = reactive<{
  task_name: string
  keywords: string
  date_range: [string, string] | null
}>({
  task_name: '',
  keywords: '',
  date_range: null,
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const handleDateRangeChange = (value: [string, string] | null) => {
  if (value) {
    searchForm.start_date = value[0]
    searchForm.end_date = value[1]
  } else {
    searchForm.start_date = ''
    searchForm.end_date = ''
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchPolicies()
}

const handleReset = () => {
  Object.assign(searchForm, {
    keyword: '',
    category: '',
    publisher: '',
    start_date: '',
    end_date: '',
    source_name: '',
  })
  dateRange.value = null
  handleSearch()
}

const fetchPolicies = async () => {
  // 如果没有选择任务，不获取政策列表
  if (!selectedTaskId.value) {
    policies.value = []
    pagination.total = 0
    return
  }
  
  loading.value = true
  try {
    const params: PolicySearchParams = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm,
      task_id: selectedTaskId.value,
    }
    const response = await policiesApi.getPolicies(params)
    policies.value = response.items
    pagination.total = response.total
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '获取政策列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCompletedTasks = async () => {
  tasksLoading.value = true
  try {
    const response = await tasksApi.getTasks({
      page: 1,
      page_size: 50,
      completed_only: true,
    })
    completedTasks.value = response.items.map(task => ({
      id: task.id,
      task_name: task.task_name,
      created_at: task.created_at,
    }))
    
    // 默认选择最近的任务
    if (completedTasks.value.length > 0 && !selectedTaskId.value) {
      selectedTaskId.value = completedTasks.value[0].id
      searchForm.task_id = completedTasks.value[0].id
      fetchPolicies()
    }
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.warning(apiError.response?.data?.detail || '获取任务列表失败')
  } finally {
    tasksLoading.value = false
  }
}

const handleTaskChange = (taskId: number | null) => {
  if (taskId) {
    searchForm.task_id = taskId
    pagination.page = 1
    fetchPolicies()
  } else {
    searchForm.task_id = undefined
    policies.value = []
    pagination.total = 0
  }
}

const formatTaskDate = (dateStr: string) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

const handleRowClick = (row: Policy) => {
  router.push(`/policies/${row.id}`)
}

const handleViewDetail = (row: Policy) => {
  router.push(`/policies/${row.id}`)
}

const handleDownload = async (row: Policy, fileType: string) => {
  try {
    const blob = await policiesApi.downloadPolicy(row.id, fileType)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${row.title}.${fileType}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载开始')
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '下载失败')
  }
}

const handleSizeChange = () => {
  fetchPolicies()
}

const handlePageChange = () => {
  fetchPolicies()
}

const handleCreateTask = async () => {
  if (!taskForm.task_name.trim()) {
    ElMessage.warning('请输入任务名称')
    return
  }

  taskCreating.value = true
  try {
    const config: CrawlTaskConfig = {}
    if (taskForm.keywords.trim()) {
      config.keywords = taskForm.keywords.split(',').map((k) => k.trim()).filter(Boolean)
    }
    if (taskForm.date_range) {
      config.date_range = {
        start: taskForm.date_range[0],
        end: taskForm.date_range[1],
      }
    }

    const request: TaskCreateRequest = {
      task_type: 'crawl_task',
      task_name: taskForm.task_name,
      config,
    }

    await tasksApi.createTask(request)
    ElMessage.success('任务创建成功')
    showCreateTaskDialog.value = false
    taskForm.task_name = ''
    taskForm.keywords = ''
    taskForm.date_range = null
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '创建任务失败')
  } finally {
    taskCreating.value = false
  }
}

const loadSourceNames = async () => {
  try {
    availableSourceNames.value = await policiesApi.getSourceNames()
  } catch (error) {
    console.error('获取数据源列表失败:', error)
  }
}

const loadCategories = async (sourceName?: string) => {
  try {
    availableCategories.value = await policiesApi.getCategories(sourceName)
  } catch (error) {
    console.error('获取分类列表失败:', error)
    availableCategories.value = []
  }
}

const handleDataSourceChange = (sourceName: string | null) => {
  // 当数据源改变时，重新加载分类列表
  if (sourceName) {
    loadCategories(sourceName)
    // 清空之前选择的分类（因为不同数据源的分类不同）
    searchForm.category = ''
  } else {
    // 如果清空数据源，也清空分类
    availableCategories.value = []
    searchForm.category = ''
  }
}

onMounted(() => {
  // 先加载已完成的任务列表，然后自动选择最近的任务并加载政策列表
  fetchCompletedTasks()
  loadSourceNames()
  // 初始加载所有分类（如果没有选择数据源）
  if (!searchForm.source_name) {
    loadCategories()
  }
})
</script>

<style lang="scss" scoped>
.policies-page {
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

  .search-form {
    margin-bottom: 20px;
    padding: 20px;
    background-color: #f5f7fa;
    border-radius: 4px;
    
    // 响应式表单
    :deep(.el-form-item) {
      margin-bottom: 10px;
    }
  }
  
  // 响应式表格
  :deep(.el-table) {
    .el-table__body-wrapper {
      overflow-x: auto;
    }
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
  .policies-page {
    .search-form {
      padding: 15px;
      
      :deep(.el-form-item) {
        width: 100%;
        margin-right: 0;
        
        .el-form-item__content {
          width: 100%;
          
          .el-input,
          .el-select,
          .el-date-picker {
            width: 100% !important;
          }
        }
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

