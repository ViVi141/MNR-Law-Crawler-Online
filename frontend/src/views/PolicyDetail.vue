<template>
  <div class="policy-detail-page">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-button @click="router.back()">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <div class="header-actions">
            <el-button
              v-if="policy?.sourceUrl"
              type="primary"
              @click="handleViewSource"
            >
              原文链接 <el-icon><Link /></el-icon>
            </el-button>
            <el-dropdown @command="handleDownload">
              <el-button type="primary">
                下载 <el-icon><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="markdown">Markdown</el-dropdown-item>
                  <el-dropdown-item command="docx">DOCX</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>

      <div v-if="policy" class="policy-content">
        <h1 class="policy-title">{{ policy.title }}</h1>

        <el-descriptions :column="2" border class="policy-meta">
          <el-descriptions-item label="分类">{{ policy.category === '全部' ? policy.source_name : `${policy.source_name}-${policy.category}` }}</el-descriptions-item>
          <el-descriptions-item label="发布机构">{{ policy.publisher || policy.lawLevel || '-' }}</el-descriptions-item>
          <el-descriptions-item label="发布日期">
            {{ formatDate(policy.publishDate || '') }}
          </el-descriptions-item>
          <el-descriptions-item label="生效日期">
            {{ formatDate(policy.effectiveDate || '') }}
          </el-descriptions-item>
          <el-descriptions-item label="文号">{{ policy.docNumber || '-' }}</el-descriptions-item>
          <el-descriptions-item label="效力级别">{{ policy.lawLevel || '-' }}</el-descriptions-item>
          <el-descriptions-item label="有效性">{{ policy.validity || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ policy.status || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(policy.createdAt || '') }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="policy.keywords && policy.keywords.length > 0" class="keywords-section">
          <el-tag
            v-for="keyword in policy.keywords"
            :key="keyword"
            style="margin-right: 8px; margin-bottom: 8px"
          >
            {{ keyword }}
          </el-tag>
        </div>

        <div v-if="policy.summary" class="summary-section">
          <h3>摘要</h3>
          <p>{{ policy.summary }}</p>
        </div>

        <div v-if="policy.content" class="content-section">
          <h3>内容</h3>
          <div class="content-body" v-html="formatContent(policy.content)"></div>
        </div>

        <div v-if="policy.attachments && policy.attachments.length > 0" class="attachments-section">
          <h3>附件</h3>
          <el-table :data="policy.attachments" stripe>
            <el-table-column prop="filename" label="文件名" />
            <el-table-column prop="file_type" label="类型" width="100" />
            <el-table-column label="大小" width="120">
              <template #default="{ row }">
                {{ formatFileSize(row.file_size) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" @click="downloadAttachment(row)">
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowDown, Link } from '@element-plus/icons-vue'
import { policiesApi } from '../api/policies'
import type { Policy } from '../types/policy'
import type { ApiError } from '../types/common'
import type { Attachment } from '../types/common'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const policy = ref<Policy | null>(null)

const formatDate = (date: string) => {
  if (!date || date === '') {
    return '-'
  }
  const parsed = dayjs(date)
  if (!parsed.isValid()) {
    return 'Invalid Date'
  }
  return parsed.format('YYYY-MM-DD')
}

const formatDateTime = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const formatContent = (content: string) => {
  // HTML内容格式化：智能处理换行和分段，修复常见的分段错误
  if (!content) return ''

  // 先转义HTML特殊字符
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

  // 1. 修复被错误拆分的年份（如 \n2022\n、\n2022年\n）
  formatted = formatted.replace(/\n+(\d{4})(年?)\s*\n+/g, '$1$2')

  // 2. 修复被错误拆分的序号和条款（如 \n第1条\n、\n第一款\n）
  formatted = formatted.replace(/\n+(第?[一二三四五六七八九十\d]+[号条款项节章款])(?:\s*\n+)?/g, '$1')

  // 3. 修复被错误拆分的括号内容（如 \n(1)\n、\n（一）\n）
  formatted = formatted.replace(/\n+(\([一二三四五六七八九十\d]+\))\s*\n+/g, '$1')
  formatted = formatted.replace(/\n+(（[一二三四五六七八九十\d]+）)\s*\n+/g, '$1')

  // 4. 修复标点符号前的错误换行（如 \n。\n、\n，\n）
  formatted = formatted.replace(/\n+([。？！，、；：])\s*\n+/g, '$1')

  // 5. 修复引号和书名号前的错误换行（如 \n《\n、\n》\n）
  formatted = formatted.replace(/\n+([\'"《》【】「」『』])\s*\n+/g, '$1')

  // 6. 清理多余的连续换行符
  formatted = formatted.replace(/\n{4,}/g, '\n\n\n')

  // 7. 将换行符转换为HTML换行，但保留段落结构
  // 三个连续换行符视为段落分隔
  formatted = formatted.replace(/\n{3}/g, '\n\n')
  // 两个连续换行符保留为双换行
  formatted = formatted.replace(/\n{2}/g, '\n\n')
  // 单个换行符转换为<br/>
  formatted = formatted.replace(/\n/g, '<br/>')

  // 8. 清理多余的连续<br/>标签（最多保留两个）
  formatted = formatted.replace(/(<br\/>\s*){3,}/g, '<br/><br/>')

  return formatted
}

const fetchPolicy = async () => {
  const id = parseInt(route.params.id as string)
  if (!id) {
    ElMessage.error('无效的政策ID')
    router.push('/policies')
    return
  }

  loading.value = true
  try {
    policy.value = await policiesApi.getPolicyById(id)
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '获取政策详情失败')
    router.push('/policies')
  } finally {
    loading.value = false
  }
}

const handleViewSource = () => {
  if (policy.value?.sourceUrl) {
    window.open(policy.value.sourceUrl, '_blank')
  }
}

const handleDownload = async (fileType: string) => {
  if (!policy.value) return

  try {
    const blob = await policiesApi.downloadPolicy(policy.value.id, fileType)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    // 将文件类型转换为实际扩展名（markdown -> md）
    const fileExt = fileType === 'markdown' ? 'md' : fileType
    a.download = `${policy.value.title}.${fileExt}`
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

const downloadAttachment = async (attachment: Attachment) => {
  if (!policy.value) return

  try {
    const blob = await policiesApi.downloadAttachment(policy.value.id, attachment.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = attachment.filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载开始')
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '下载附件失败')
  }
}

onMounted(() => {
  fetchPolicy()
})
</script>

<style lang="scss" scoped>
.policy-detail-page {
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
    
    .header-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
  }

  .policy-content {
    width: 100%;
    
    .policy-title {
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 20px;
      color: #303133;
      word-wrap: break-word;
      line-height: 1.5;
    }

    .policy-meta {
      margin-bottom: 20px;
      
      :deep(.el-descriptions) {
        .el-descriptions__label {
          font-weight: 500;
        }
      }
    }

    .keywords-section {
      margin-bottom: 20px;
      padding: 15px;
      background-color: #f5f7fa;
      border-radius: 4px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .summary-section,
    .content-section,
    .attachments-section {
      margin-top: 30px;

      h3 {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 15px;
        color: #303133;
      }

      p {
        line-height: 1.8;
        color: #606266;
        word-wrap: break-word;
      }
    }

    .content-body {
      line-height: 1.8;
      color: #606266;
      padding: 20px;
      background-color: #fafafa;
      border-radius: 4px;
      white-space: pre-wrap;
      word-wrap: break-word;
      overflow-x: auto;
      max-width: 100%;
    }
    
    // 附件表格
    :deep(.attachments-section) {
      .el-table {
        .el-table__body-wrapper {
          overflow-x: auto;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .policy-detail-page {
    .policy-content {
      .policy-title {
        font-size: 20px;
      }
      
      .policy-meta {
        :deep(.el-descriptions) {
          .el-descriptions__table {
            .el-descriptions__label,
            .el-descriptions__content {
              display: block;
              width: 100%;
              padding: 8px 0;
            }
          }
        }
      }
      
      .content-body {
        padding: 15px;
        font-size: 14px;
      }
    }
  }
}
</style>

