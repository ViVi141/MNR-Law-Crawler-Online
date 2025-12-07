import apiClient from './client'
import type { LoginRequest, LoginResponse, UserInfo } from '../types/auth'

export interface PasswordChangeRequest {
  old_password: string
  new_password: string
}

export interface PasswordResetRequest {
  new_password: string
}

export interface PasswordResetResponse {
  success: boolean
  message: string
  new_password?: string
}

export const authApi = {
  // 登录
  login(data: LoginRequest): Promise<LoginResponse> {
    return apiClient.post('/api/auth/login', data).then((res) => res.data)
  },

  // 获取当前用户信息
  getCurrentUser(): Promise<UserInfo> {
    return apiClient.get('/api/auth/me').then((res) => res.data)
  },

  // 刷新token（如果需要）
  refreshToken(): Promise<LoginResponse> {
    return apiClient.post('/api/auth/refresh').then((res) => res.data)
  },

  // 修改密码
  changePassword(data: PasswordChangeRequest): Promise<{ message: string }> {
    return apiClient.post('/api/auth/change-password', data).then((res) => res.data)
  },

  // 重置密码
  resetPassword(data: PasswordResetRequest): Promise<PasswordResetResponse> {
    return apiClient.post('/api/auth/reset-password', data).then((res) => res.data)
  },

  // 生成随机密码
  generatePassword(length: number = 12): Promise<PasswordResetResponse> {
    return apiClient.post(`/api/auth/generate-password?length=${length}`).then((res) => res.data)
  },

  // 忘记密码（通过邮件重置）
  forgotPassword(username: string): Promise<PasswordResetResponse> {
    return apiClient.post('/api/auth/forgot-password', { username }).then((res) => res.data)
  },
}


