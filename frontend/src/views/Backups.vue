<template>
  <div class="backups-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>备份管理</h2>
          <div>
            <el-button type="primary" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon>
              创建备份
            </el-button>
            <el-button type="success" @click="showUploadDialog = true">
              <el-icon><Upload /></el-icon>
              上传备份
            </el-button>
            <el-button @click="handleCleanup">
              <el-icon><Delete /></el-icon>
              清理旧备份
            </el-button>
          </div>
        </div>
      </template>

      <!-- 备份列表 -->
      <el-table v-loading="loading" :data="backups" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="backup_type" label="备份类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.backup_type === 'full' ? 'primary' : 'success'">
              {{ row.backup_type === 'full' ? '完整备份' : '增量备份' }}
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
        <el-table-column label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="completed_at" label="完成时间" width="180">
          <template #default="{ row }">
            {{ row.completed_at ? formatDateTime(row.completed_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="file_path" label="文件路径" min-width="300" show-overflow-tooltip />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'completed'"
              link
              type="primary"
              @click="handleRestore(row)"
            >
              恢复
            </el-button>
            <el-button
              v-if="row.status === 'completed'"
              link
              type="success"
              :loading="downloading && downloadingBackup?.id === row.id"
              :disabled="downloading"
              @click="handleDownload(row)"
            >
              <el-icon v-if="!downloading || downloadingBackup?.id !== row.id"><Download /></el-icon>
              {{ downloading && downloadingBackup?.id === row.id ? '下载中...' : '下载' }}
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

    <!-- 创建备份对话框 -->
    <TaskCreationForm
      v-model="showCreateDialog"
      task-type="backup_task"
      :disable-task-type-select="true"
      @submit="handleBackupSubmit"
      @cancel="showCreateDialog = false"
    />

    <!-- 上传备份对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传备份文件" width="500px">
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="100px">
        <el-form-item label="备份文件" prop="file" required>
          <el-upload
            ref="uploadRef"
            v-model:file-list="fileList"
            :auto-upload="false"
            :multiple="false"
            :limit="1"
            accept=".sql"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                请上传 .sql 格式的数据库备份文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="备份名称" prop="backupName">
          <el-input
            v-model="uploadForm.backupName"
            placeholder="可选，为备份文件指定名称"
          />
          <div class="help-text">
            留空将使用文件名作为备份名称
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleUploadCancel">取消</el-button>
        <el-button
          type="primary"
          :loading="uploading"
          @click="handleUploadConfirm"
        >
          上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Upload, Download } from '@element-plus/icons-vue'
import TaskCreationForm from '../components/TaskCreationForm.vue'
import { backupsApi } from '../api/backups'
import type { BackupRecord } from '../types/backup'
import type { ApiError } from '../types/common'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import dayjs from 'dayjs'

const loading = ref(false)
const creating = ref(false)
const uploading = ref(false)
const downloading = ref(false)
const backups = ref<BackupRecord[]>([])
const showCreateDialog = ref(false)
const showUploadDialog = ref(false)
const downloadingBackup = ref<BackupRecord | null>(null)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const uploadForm = reactive({
  file: null as File | null,
  backupName: '',
})

const fileList = ref<UploadFile[]>([])
const uploadFormRef = ref<FormInstance>()

const uploadRules: FormRules = {
  file: [{ required: true, message: '请上传备份文件', trigger: 'change' }],
}

const formatDateTime = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
  }
  return statusMap[status] || status
}

const fetchBackups = async () => {
  loading.value = true
  try {
    const response = await backupsApi.getBackups({
      page: pagination.page,
      page_size: pagination.pageSize,
    })
    backups.value = response.items || response.backups || []
    pagination.total = response.total || 0
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '获取备份列表失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = () => {
  pagination.page = 1
  fetchBackups()
}

const handlePageChange = () => {
  fetchBackups()
}

const handleBackupSubmit = async (formData: any) => {
  creating.value = true
  try {
    // 使用统一的API创建备份任务
    await backupsApi.createBackup(formData.config)
    ElMessage.success('备份任务已创建')
    showCreateDialog.value = false
    await fetchBackups()
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '创建备份失败')
  } finally {
    creating.value = false
  }
}

const handleRestore = async (backup: BackupRecord) => {
  try {
    await ElMessageBox.confirm(
      `确定要恢复备份 ${backup.id} 吗？此操作将覆盖当前数据库！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await backupsApi.restoreBackup(backup.id, { confirm: true })
    ElMessage.success('备份恢复任务已启动')
    await fetchBackups()
  } catch (error) {
    // ElMessageBox.confirm 取消时会抛出 'cancel' 字符串
    if (typeof error === 'string' && error === 'cancel') {
      return
    }
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '恢复备份失败')
  }
}

const handleDelete = async (backup: BackupRecord) => {
  try {
    await ElMessageBox.confirm('确定要删除这个备份吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await backupsApi.deleteBackup(backup.id)
    ElMessage.success('备份已删除')
    await fetchBackups()
  } catch (error) {
    // ElMessageBox.confirm 取消时会抛出 'cancel' 字符串
    if (typeof error === 'string' && error === 'cancel') {
      return
    }
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '删除备份失败')
  }
}

const handleCleanup = async () => {
  try {
    const { value } = await ElMessageBox.prompt(
      '请输入要保留的备份数量',
      '清理旧备份',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /^\d+$/,
        inputErrorMessage: '请输入有效的数字',
      }
    )

    const keepCount = parseInt(value)
    const result = await backupsApi.cleanupBackups({ keep_count: keepCount })
    ElMessage.success(`已清理 ${result.deleted_count} 个旧备份`)
    await fetchBackups()
  } catch (error) {
    // ElMessageBox.prompt 取消时会抛出 'cancel' 字符串
    if (typeof error === 'string' && error === 'cancel') {
      return
    }
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '清理备份失败')
  }
}

// 下载备份文件
const handleDownload = async (backup: BackupRecord) => {
  downloadingBackup.value = backup
  downloading.value = true

  let loadingInstance: ReturnType<typeof ElMessage> | null = null

  try {
    // 显示加载提示
    loadingInstance = ElMessage({
      message: '正在准备下载文件，请稍候...',
      type: 'info',
      duration: 0,
      showClose: false,
    })

    // 调用下载API
    const blob = await backupsApi.downloadBackup(backup.id)

    // 关闭加载提示
    if (loadingInstance) {
      loadingInstance.close()
      loadingInstance = null
    }

    // 检查文件大小
    const fileSize = blob.size
    const fileSizeMB = (fileSize / (1024 * 1024)).toFixed(2)

    if (fileSize === 0) {
      ElMessage.warning('下载的文件为空，可能备份文件有问题')
      return
    }

    // 显示文件大小信息
    ElMessage({
      message: `备份文件准备完成，大小: ${fileSizeMB} MB，开始下载...`,
      type: 'success',
      duration: 3000,
    })

    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    // 生成文件名
    const timestamp = dayjs().format('YYYYMMDD_HHmmss')
    const safeName = (backup.source_name || backup.id).replace(/[<>:"/\\|?*]/g, '_')
    link.download = `${safeName}_${backup.backup_type}_${timestamp}.sql`

    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    // 延迟释放URL对象，确保下载开始
    setTimeout(() => {
      window.URL.revokeObjectURL(url)
    }, 100)

    ElMessage.success('备份文件下载成功')
  } catch (error) {
    // 关闭加载提示
    if (loadingInstance) {
      loadingInstance.close()
      loadingInstance = null
    }

    const apiError = error as ApiError
    const errorMessage = apiError.response?.data?.detail || apiError.message || '下载备份文件失败'
    ElMessage.error(errorMessage)
    console.error('下载备份文件失败:', error)
  } finally {
    downloading.value = false
    downloadingBackup.value = null
  }
}

// 处理文件选择
const handleFileChange = (file: UploadFile) => {
  uploadForm.file = file.raw || null
}

// 处理文件移除
const handleFileRemove = () => {
  uploadForm.file = null
}

// 取消上传
const handleUploadCancel = () => {
  showUploadDialog.value = false
  uploadForm.file = null
  uploadForm.backupName = ''
  fileList.value = []
}

// 确认上传
const handleUploadConfirm = async () => {
  if (!uploadFormRef.value) return

  await uploadFormRef.value.validate(async (valid: boolean) => {
    if (valid && uploadForm.file) {
      uploading.value = true
      try {
        await backupsApi.uploadBackup(
          uploadForm.file,
          uploadForm.backupName || undefined
        )

        ElMessage.success('备份文件上传成功')
        showUploadDialog.value = false

        // 清空表单
        uploadForm.file = null
        uploadForm.backupName = ''
        fileList.value = []

        // 刷新备份列表
        await fetchBackups()
      } catch (error) {
        const apiError = error as ApiError
        ElMessage.error(apiError.response?.data?.detail || '上传备份文件失败')
      } finally {
        uploading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchBackups()
})
</script>

<style lang="scss" scoped>
.backups-page {
  width: 100%;
  min-height: 100%;
  
  :deep(.el-card) {
    height: 100%;
    display: flex;
    flex-direction: column;

    .el-card__body {
      flex: 1;
    }
  }

  .help-text {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }

  :deep(.el-upload__tip) {
    font-size: 12px;
    color: #909399;
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
    
    > div {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
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
  .backups-page {
    .card-header {
      h2 {
        font-size: 18px;
      }
    }
  }
}
</style>

