<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>MNR法规爬虫系统</h2>
          <p>请登录您的账户</p>
        </div>
      </template>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>
        <el-form-item v-if="emailAvailable">
          <el-button
            link
            type="primary"
            @click="showForgotPassword = true"
            style="width: 100%; text-align: center"
          >
            忘记密码？
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 忘记密码对话框 -->
    <el-dialog
      v-model="showForgotPassword"
      title="忘记密码"
      width="400px"
    >
      <el-form :model="forgotPasswordForm" :rules="forgotPasswordRules" ref="forgotPasswordFormRef" label-width="100px">
        <el-alert
          title="密码重置说明"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <template #default>
            <div style="font-size: 12px; line-height: 1.6">
              <p>请输入您的用户名或邮箱，系统将：</p>
              <ul style="margin: 5px 0; padding-left: 20px">
                <li>如果已启用邮件服务，将发送新密码到您的邮箱</li>
                <li>如果未启用邮件服务，请联系管理员使用后端脚本重置</li>
              </ul>
            </div>
          </template>
        </el-alert>
        <el-form-item label="用户名/邮箱" prop="username">
          <el-input
            v-model="forgotPasswordForm.username"
            placeholder="请输入用户名或邮箱"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForgotPassword = false">取消</el-button>
        <el-button type="primary" :loading="forgotPasswordLoading" @click="handleForgotPassword">
          发送重置邮件
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import { authApi } from '../api/auth'
import { configApi } from '../api/config'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApiError } from '../types/common'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const forgotPasswordFormRef = ref<FormInstance>()
const loading = ref(false)
const showForgotPassword = ref(false)
const forgotPasswordLoading = ref(false)
const emailAvailable = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const forgotPasswordForm = reactive({
  username: '',
})

const forgotPasswordRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
  ],
}

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login({
          username: loginForm.username,
          password: loginForm.password,
        })
        ElMessage.success('登录成功')
        const redirect = (route.query.redirect as string) || '/policies'
        router.push(redirect)
      } catch (error) {
        const apiError = error as import('../types/common').ApiError
        ElMessage.error(apiError.response?.data?.detail || '登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleForgotPassword = async () => {
  if (!forgotPasswordFormRef.value) return

  await forgotPasswordFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      forgotPasswordLoading.value = true
      try {
        const result = await authApi.forgotPassword(forgotPasswordForm.username)
        if (result.success) {
          ElMessage.success(result.message || '密码重置邮件已发送，请查看您的邮箱')
          showForgotPassword.value = false
          forgotPasswordForm.username = ''
        } else {
          ElMessage.warning(result.message || '密码重置失败')
        }
      } catch (error) {
        const apiError = error as ApiError
        ElMessage.error(apiError.response?.data?.detail || apiError.response?.data?.message || '请求失败，请稍后重试')
      } finally {
        forgotPasswordLoading.value = false
      }
    }
  })
}

// 检查邮件服务是否可用
const checkEmailAvailability = async () => {
  try {
    const result = await configApi.checkEmailAvailable()
    emailAvailable.value = result.available || false
  } catch (_error) {
    // 如果检查失败，默认不显示忘记密码功能
    emailAvailable.value = false
  }
}

onMounted(() => {
  checkEmailAvailability()
})
</script>

<style lang="scss" scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow-y: auto;

  .login-card {
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);

    .card-header {
      text-align: center;

      h2 {
        margin: 0 0 10px 0;
        font-size: 24px;
        color: #303133;
        word-wrap: break-word;
      }

      p {
        margin: 0;
        color: #909399;
        font-size: 14px;
      }
    }
    
    :deep(.el-form) {
      .el-form-item {
        margin-bottom: 20px;
      }
    }
  }
}

// 响应式设计
@media (max-width: 480px) {
  .login-container {
    padding: 15px;
    
    .login-card {
      .card-header {
        h2 {
          font-size: 20px;
        }
      }
    }
  }
}
</style>

