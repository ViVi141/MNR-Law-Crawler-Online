<template>
  <div class="settings-page">
    <!-- 功能开关 -->
    <el-card class="settings-card">
      <template #header>
        <h3>功能开关</h3>
      </template>
      <el-form :model="featureFlags" label-width="200px">
        <el-form-item label="S3存储">
          <el-switch
            v-model="featureFlags.s3_enabled"
            :loading="flagsLoading"
            @change="handleUpdateFeatureFlag('s3_enabled', $event)"
          />
          <span class="help-text">启用S3对象存储功能</span>
        </el-form-item>
        <el-form-item label="邮件通知">
          <el-switch
            v-model="featureFlags.email_enabled"
            :loading="flagsLoading"
            @change="handleUpdateFeatureFlag('email_enabled', $event)"
          />
          <span class="help-text">启用邮件通知功能</span>
        </el-form-item>
        <el-form-item label="缓存">
          <el-switch
            v-model="featureFlags.cache_enabled"
            :loading="flagsLoading"
            @change="handleUpdateFeatureFlag('cache_enabled', $event)"
          />
          <span class="help-text">启用本地缓存功能</span>
        </el-form-item>
        <el-form-item label="定时任务">
          <el-switch
            v-model="featureFlags.scheduler_enabled"
            :loading="flagsLoading"
            @change="handleUpdateFeatureFlag('scheduler_enabled', $event)"
          />
          <span class="help-text">启用定时任务功能</span>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- S3配置 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h3>S3配置</h3>
          <div>
            <el-button size="small" @click="handleResetS3">重置</el-button>
            <el-button size="small" type="primary" :loading="s3Testing" @click="handleTestS3">
              测试连接
            </el-button>
            <el-button size="small" type="success" :loading="s3Saving" @click="handleSaveS3">
              保存配置
            </el-button>
          </div>
        </div>
      </template>
      <el-form :model="s3Config" :rules="s3Rules" ref="s3FormRef" label-width="150px">
        <el-form-item label="启用S3">
          <el-switch
            v-model="s3Config.enabled"
            :disabled="!featureFlags.s3_enabled"
            @change="handleS3EnabledChange"
          />
          <span class="help-text">需要先启用功能开关才能配置S3</span>
        </el-form-item>
        <el-form-item label="访问密钥ID" prop="access_key_id">
          <el-input v-model="s3Config.access_key_id" placeholder="请输入S3访问密钥ID" />
        </el-form-item>
        <el-form-item label="秘密访问密钥" prop="secret_access_key">
          <el-input
            v-model="s3Config.secret_access_key"
            type="password"
            show-password
            placeholder="请输入S3秘密访问密钥"
          />
        </el-form-item>
        <el-form-item label="存储桶名称" prop="bucket_name">
          <el-input v-model="s3Config.bucket_name" placeholder="请输入存储桶名称" />
        </el-form-item>
        <el-form-item label="区域" prop="region">
          <el-input v-model="s3Config.region" placeholder="请输入区域（如：us-east-1）" />
        </el-form-item>
        <el-form-item label="端点URL" prop="endpoint_url">
          <el-input
            v-model="s3Config.endpoint_url"
            placeholder="可选，自定义S3端点URL"
          />
        </el-form-item>
      </el-form>
      <el-alert
        v-if="!featureFlags.s3_enabled"
        title="S3功能已禁用"
        type="warning"
        :closable="false"
        style="margin-top: 20px"
      >
        请先启用上方的"S3存储"功能开关，然后才能配置S3。
      </el-alert>
    </el-card>

    <!-- 邮件配置 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h3>邮件配置</h3>
          <div>
            <el-button size="small" @click="handleResetEmail">重置</el-button>
            <el-button size="small" type="primary" :loading="emailTesting" @click="handleTestEmail">
              测试连接
            </el-button>
            <el-button size="small" type="warning" :loading="emailSending" @click="handleShowSendTestEmailDialog">
              发送测试邮件
            </el-button>
            <el-button size="small" type="success" :loading="emailSaving" @click="handleSaveEmail">
              保存配置
            </el-button>
          </div>
        </div>
      </template>
      <el-form :model="emailConfig" :rules="emailRules" ref="emailFormRef" label-width="150px">
        <el-form-item label="SMTP服务器" prop="smtp_host">
          <el-input v-model="emailConfig.smtp_host" placeholder="请输入SMTP服务器地址" />
        </el-form-item>
        <el-form-item label="SMTP端口" prop="smtp_port">
          <el-input-number v-model="emailConfig.smtp_port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="SMTP用户" prop="smtp_user">
          <el-input v-model="emailConfig.smtp_user" placeholder="请输入SMTP用户名" />
        </el-form-item>
        <el-form-item label="SMTP密码" prop="smtp_password">
          <el-input
            v-model="emailConfig.smtp_password"
            type="password"
            show-password
            placeholder="请输入SMTP密码"
          />
        </el-form-item>
        <el-form-item label="发件人地址" prop="from_address">
          <el-input v-model="emailConfig.from_address" placeholder="请输入发件人邮箱地址" />
        </el-form-item>
        <el-form-item label="收件人地址" prop="to_addresses" required>
          <el-input
            v-model="emailConfig.to_addresses"
            type="textarea"
            :rows="3"
            placeholder="请输入收件人邮箱地址，多个地址用逗号分隔（启用邮件服务时必须至少配置一个收件人）"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            启用邮件服务时，必须至少配置一个收件人地址
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 爬虫配置 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h3>爬虫配置</h3>
          <div>
            <el-button size="small" @click="handleResetCrawler">重置</el-button>
            <el-button size="small" type="success" :loading="crawlerSaving" @click="handleSaveCrawler">
              保存配置
            </el-button>
          </div>
        </div>
      </template>
      <el-form :model="crawlerConfig" label-width="150px">
        <el-form-item label="爬取延迟（秒）">
          <el-input-number
            v-model="crawlerConfig.request_delay"
            :min="0"
            :max="10"
            :step="0.1"
            :precision="1"
            style="width: 200px"
          />
          <span class="help-text">每次请求之间的延迟时间，默认0.5秒（目标网站无防护，可以设置较小值）</span>
        </el-form-item>
        <el-form-item label="使用代理">
          <el-switch
            v-model="crawlerConfig.use_proxy"
            disabled
          />
          <span class="help-text">目标网站无防护，无需使用代理（功能已禁用）</span>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 密码管理 -->
    <el-card class="settings-card password-card">
      <template #header>
        <div class="card-header">
          <div>
            <h3>密码管理</h3>
            <el-tag type="warning" size="small" style="margin-left: 10px">重要功能</el-tag>
          </div>
          <el-button type="warning" size="small" @click="handleGeneratePassword">
            生成随机密码
          </el-button>
        </div>
      </template>
      <el-alert
        title="密码安全提示"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #default>
          <ul style="margin: 5px 0; padding-left: 20px">
            <li>修改密码：需要输入当前密码和新密码（至少6位字符）</li>
            <li>生成随机密码：系统将自动生成一个安全的随机密码并重置您的账户密码</li>
            <li>密码修改成功后需要重新登录</li>
          </ul>
        </template>
      </el-alert>
      <el-form
        :model="passwordForm"
        :rules="passwordRules"
        ref="passwordFormRef"
        label-width="150px"
      >
        <el-form-item label="当前密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            show-password
            placeholder="请输入当前密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            show-password
            placeholder="请输入新密码（至少6位）"
          />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="passwordChanging" @click="handleChangePassword">
            <el-icon><Lock /></el-icon>
            修改密码
          </el-button>
          <el-button type="warning" :loading="passwordGenerating" @click="handleGeneratePassword">
            <el-icon><Key /></el-icon>
            生成随机密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 发送测试邮件对话框 -->
    <el-dialog
      v-model="sendTestEmailDialogVisible"
      title="发送测试邮件"
      width="500px"
    >
      <el-form :model="testEmailForm" label-width="120px">
        <el-form-item label="收件人邮箱" required>
          <el-input
            v-model="testEmailForm.toAddress"
            placeholder="请输入收件人邮箱地址"
            clearable
          />
        </el-form-item>
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          style="margin-top: 10px"
        >
          系统将使用当前配置发送一封测试邮件到指定邮箱地址，请确保邮件配置正确。
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="sendTestEmailDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="emailSending" @click="handleSendTestEmail">
          发送
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Lock, Key } from '@element-plus/icons-vue'
import { configApi } from '../api/config'
import { authApi } from '../api/auth'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApiError } from '../types/common'
import type { S3ConfigUpdate, EmailConfigUpdate } from '../types/config'

const router = useRouter()
const authStore = useAuthStore()

const flagsLoading = ref(false)
const s3Loading = ref(false)
const s3Saving = ref(false)
const s3Testing = ref(false)
const emailLoading = ref(false)
const emailSaving = ref(false)
const emailTesting = ref(false)
const passwordChanging = ref(false)
const passwordGenerating = ref(false)
const crawlerSaving = ref(false)
const emailSending = ref(false)
const sendTestEmailDialogVisible = ref(false)

const s3FormRef = ref<FormInstance>()
const emailFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

const featureFlags = reactive({
  s3_enabled: false,
  email_enabled: false,
  cache_enabled: false,
  scheduler_enabled: false,
})

const s3Config = reactive<S3ConfigUpdate>({
  enabled: false,
  access_key_id: '',
  secret_access_key: '',
  bucket_name: '',
  region: '',
  endpoint_url: '',
})

const crawlerConfig = reactive({
  request_delay: 0.5,
  use_proxy: false,
})

const emailConfig = reactive<Omit<EmailConfigUpdate, 'to_addresses'> & { to_addresses: string }>({
  enabled: false,
  smtp_host: '',
  smtp_port: 587,
  smtp_user: '',
  smtp_password: '',
  from_address: '',
  to_addresses: '',
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const testEmailForm = reactive({
  toAddress: '',
})

const s3Rules: FormRules = {
  access_key_id: [{ required: true, message: '请输入访问密钥ID', trigger: 'blur' }],
  secret_access_key: [{ required: true, message: '请输入秘密访问密钥', trigger: 'blur' }],
  bucket_name: [{ required: true, message: '请输入存储桶名称', trigger: 'blur' }],
  region: [{ required: true, message: '请输入区域', trigger: 'blur' }],
}

const validateToAddresses = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (emailConfig.enabled) {
    const addresses = value.split(',').map((addr: string) => addr.trim()).filter(Boolean)
    if (addresses.length === 0) {
      callback(new Error('启用邮件服务时，必须至少配置一个收件人地址'))
      return
    }
    // 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    for (const addr of addresses) {
      if (!emailRegex.test(addr)) {
        callback(new Error(`无效的邮箱地址格式: ${addr}`))
        return
      }
    }
  }
  callback()
}

const emailRules: FormRules = {
  smtp_host: [{ required: true, message: '请输入SMTP服务器', trigger: 'blur' }],
  smtp_port: [{ required: true, message: '请输入SMTP端口', trigger: 'blur' }],
  smtp_user: [{ required: true, message: '请输入SMTP用户', trigger: 'blur' }],
  smtp_password: [{ required: true, message: '请输入SMTP密码', trigger: 'blur' }],
  from_address: [{ required: true, message: '请输入发件人地址', trigger: 'blur' }],
  to_addresses: [
    { validator: validateToAddresses, trigger: 'blur' },
  ],
}

const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

const fetchFeatureFlags = async () => {
  flagsLoading.value = true
  try {
    const flags = await configApi.getFeatureFlags()
    Object.assign(featureFlags, flags)
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '获取功能开关失败')
  } finally {
    flagsLoading.value = false
  }
}

const handleUpdateFeatureFlag = async (flagName: string, enabled: boolean) => {
  flagsLoading.value = true
  try {
    const flags = await configApi.updateFeatureFlag(flagName, enabled)
    Object.assign(featureFlags, flags)
    
    // 如果是 S3 开关，同步更新 S3 配置中的 enabled 状态
    if (flagName === 's3_enabled') {
      s3Config.enabled = enabled
      // 同时更新 S3 配置到后端
      try {
        await configApi.updateS3Config({ enabled })
      } catch {
        // S3配置更新失败不影响功能开关更新
      }
    }
    
        ElMessage.success('功能开关已更新' + (flagName === 's3_enabled' ? '（S3配置将自动重新初始化）' : ''))
  } catch (error) {
    // 恢复原状态
    const apiError = error as ApiError
    ;(featureFlags as Record<string, boolean>)[flagName] = !enabled
    ElMessage.error(apiError.response?.data?.detail || '更新功能开关失败')
  } finally {
    flagsLoading.value = false
  }
}

const fetchS3Config = async () => {
  s3Loading.value = true
  try {
    const config = await configApi.getS3Config()
    Object.assign(s3Config, config)
    
    // 确保S3配置的enabled状态与功能开关同步
    if (config.enabled !== undefined) {
      s3Config.enabled = config.enabled
    } else {
      // 如果配置中没有enabled，使用功能开关的值
      s3Config.enabled = featureFlags.s3_enabled
    }
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '获取S3配置失败')
  } finally {
    s3Loading.value = false
  }
}

const handleSaveS3 = async () => {
  if (!s3FormRef.value) return

  await s3FormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      s3Saving.value = true
      try {
        await configApi.updateS3Config(s3Config)
        ElMessage.success('S3配置已保存并已自动重新初始化，无需重启')
      } catch (error) {
        const apiError = error as ApiError
        ElMessage.error(apiError.response?.data?.detail || '保存S3配置失败')
      } finally {
        s3Saving.value = false
      }
    }
  })
}

const handleS3EnabledChange = async (enabled: boolean) => {
  // 当S3配置中的enabled开关变化时，同步更新功能开关
  if (enabled !== featureFlags.s3_enabled) {
    try {
      const flags = await configApi.updateFeatureFlag('s3_enabled', enabled)
      Object.assign(featureFlags, flags)
      ElMessage.success('S3功能开关已同步更新（配置已自动重新初始化）')
    } catch (error) {
      // 恢复原状态
      s3Config.enabled = !enabled
      const apiError = error as ApiError
      ElMessage.error(apiError.response?.data?.detail || '更新S3功能开关失败')
    }
  }
}

const handleResetS3 = () => {
  fetchS3Config()
}

const handleTestS3 = async () => {
  s3Testing.value = true
  try {
    const result = await configApi.testS3Config(s3Config)
    if (result.success) {
      ElMessage.success(result.message || 'S3连接测试成功')
    } else {
      ElMessage.error(result.message || 'S3连接测试失败')
    }
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || 'S3连接测试失败')
  } finally {
    s3Testing.value = false
  }
}

const fetchEmailConfig = async () => {
  emailLoading.value = true
  try {
    const config = await configApi.getEmailConfig()
    Object.assign(emailConfig, {
      ...config,
      to_addresses: Array.isArray(config.to_addresses)
        ? config.to_addresses.join(', ')
        : config.to_addresses || '',
    })
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '获取邮件配置失败')
  } finally {
    emailLoading.value = false
  }
}

const handleSaveEmail = async () => {
  if (!emailFormRef.value) return

  await emailFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      emailSaving.value = true
      try {
        const toAddresses = emailConfig.to_addresses
          .split(',')
          .map((addr) => addr.trim())
          .filter(Boolean)
        
        await configApi.updateEmailConfig({
          ...emailConfig,
          to_addresses: toAddresses,
        })
        ElMessage.success('邮件配置已保存')
      } catch (error) {
        const apiError = error as ApiError
        ElMessage.error(apiError.response?.data?.detail || '保存邮件配置失败')
      } finally {
        emailSaving.value = false
      }
    }
  })
}

const handleResetEmail = () => {
  fetchEmailConfig()
}

const handleTestEmail = async () => {
  emailTesting.value = true
  try {
    const toAddresses = emailConfig.to_addresses
      .split(',')
      .map((addr) => addr.trim())
      .filter(Boolean)
    
    const result = await configApi.testEmailConfig({
      ...emailConfig,
      to_addresses: toAddresses,
    })
    if (result.success) {
      ElMessage.success(result.message || '邮件连接测试成功')
    } else {
      ElMessage.error(result.message || '邮件连接测试失败')
    }
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '邮件连接测试失败')
  } finally {
    emailTesting.value = false
  }
}

const handleShowSendTestEmailDialog = () => {
  // 如果配置中有收件人地址，默认填入第一个
  if (emailConfig.to_addresses) {
    const addresses = emailConfig.to_addresses.split(',').map((addr) => addr.trim()).filter(Boolean)
    testEmailForm.toAddress = addresses.length > 0 ? addresses[0] : ''
  } else {
    testEmailForm.toAddress = ''
  }
  sendTestEmailDialogVisible.value = true
}

const handleSendTestEmail = async () => {
  if (!testEmailForm.toAddress || !testEmailForm.toAddress.trim()) {
    ElMessage.warning('请输入收件人邮箱地址')
    return
  }

  // 验证邮箱格式
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(testEmailForm.toAddress.trim())) {
    ElMessage.warning('请输入有效的邮箱地址')
    return
  }

  emailSending.value = true
  try {
    const toAddresses = emailConfig.to_addresses
      .split(',')
      .map((addr) => addr.trim())
      .filter(Boolean)
    
    const result = await configApi.sendTestEmail(testEmailForm.toAddress.trim(), {
      ...emailConfig,
      to_addresses: toAddresses,
    })
    
    if (result.success) {
      ElMessage.success(result.message || '测试邮件发送成功，请检查收件箱')
      sendTestEmailDialogVisible.value = false
      testEmailForm.toAddress = ''
    } else {
      ElMessage.error(result.message || '测试邮件发送失败')
    }
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '测试邮件发送失败')
  } finally {
    emailSending.value = false
  }
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      passwordChanging.value = true
      try {
        await authApi.changePassword({
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password,
        })

        // 立即登出并跳转到登录页
        authStore.logout()
        ElMessage.success('密码修改成功，请使用新密码重新登录')
        router.push('/login')

      } catch (error) {
        const apiError = error as ApiError
        ElMessage.error(apiError.response?.data?.detail || '修改密码失败')
      } finally {
        passwordChanging.value = false
      }
    }
  })
}

const handleGeneratePassword = async () => {
  try {
    await ElMessageBox.confirm(
      '生成随机密码后，当前密码将被替换，请妥善保存新密码。是否继续？',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    passwordGenerating.value = true
    try {
      const result = await authApi.generatePassword()
      if (result.success && result.new_password) {
        ElMessageBox.alert(
          `新密码已生成：<strong>${result.new_password}</strong><br/>系统将自动登出，请使用新密码重新登录。`,
          '密码重置成功',
          {
            confirmButtonText: '确定',
            type: 'success',
            dangerouslyUseHTMLString: true,
          }
        ).then(() => {
          // 立即登出并跳转到登录页
          authStore.logout()
          router.push('/login')
        })
      } else {
        ElMessage.error(result.message || '生成随机密码失败')
      }
    } catch (error) {
      if (typeof error === 'string' && error === 'cancel') {
        return
      }
      const apiError = error as ApiError
      ElMessage.error(apiError.response?.data?.detail || '生成随机密码失败')
    } finally {
      passwordGenerating.value = false
    }
  } catch {
    // 用户取消
  }
}

// 监听功能开关变化，同步S3配置
watch(
  () => featureFlags.s3_enabled,
  (enabled) => {
    s3Config.enabled = enabled
  }
)

const fetchCrawlerConfig = async () => {
  try {
    const config = await configApi.getCrawlerConfig()
    crawlerConfig.request_delay = config.request_delay || 0.5
    crawlerConfig.use_proxy = config.use_proxy || false
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '获取爬虫配置失败')
  }
}

const handleSaveCrawler = async () => {
  crawlerSaving.value = true
  try {
    await configApi.updateCrawlerConfig({
      request_delay: crawlerConfig.request_delay,
      use_proxy: false, // 始终禁用代理
    })
    ElMessage.success('爬虫配置已保存')
  } catch (error) {
    const apiError = error as ApiError
    ElMessage.error(apiError.response?.data?.detail || '保存爬虫配置失败')
  } finally {
    crawlerSaving.value = false
  }
}

const handleResetCrawler = () => {
  crawlerConfig.request_delay = 0.5
  crawlerConfig.use_proxy = false
}

onMounted(() => {
  fetchFeatureFlags()
  fetchS3Config()
  fetchEmailConfig()
  fetchCrawlerConfig()
})
</script>

<style lang="scss" scoped>
.settings-page {
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 120px);
  max-height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px 20px 20px 10px;
  box-sizing: border-box;
  
  .settings-card {
    flex-shrink: 0;
    margin-bottom: 0;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    
    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }

    .help-text {
      margin-left: 10px;
      font-size: 12px;
      color: #909399;
    }
    
    // 密码管理卡片特殊样式
    &.password-card {
      border: 2px solid #e6a23c;
      background: linear-gradient(to bottom, #fff9e6 0%, #ffffff 10%);
      
      .card-header {
        h3 {
          display: flex;
          align-items: center;
        }
      }
    }
    
    :deep(.el-card__body) {
      max-height: none;
      overflow: visible;
    }
  }
  
  // 表单响应式
  :deep(.el-form) {
    .el-form-item {
      margin-bottom: 20px;
    }
    
    .el-input,
    .el-select {
      width: 100%;
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
  .settings-page {
    .card-header {
      h3 {
        font-size: 16px;
      }
    }
    
    :deep(.el-form) {
      .el-form-item__label {
        width: 100% !important;
        text-align: left;
      }
      
      .el-form-item__content {
        margin-left: 0 !important;
      }
    }
  }
}
</style>
