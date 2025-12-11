import axios, { type AxiosInstance, type AxiosResponse, type AxiosError } from 'axios'

// API基础URL配置逻辑：
// 1. 如果设置了 VITE_API_BASE_URL 环境变量，优先使用
//    - Docker生产环境：使用空字符串（相对路径），通过Nginx代理到Docker网络中的backend
//    - 本地开发：使用 http://localhost:8000
// 2. 开发环境：使用 http://localhost:8000（Vite代理会处理）
// 3. 生产环境：使用相对路径（空字符串），通过Nginx代理访问后端
function getApiBaseUrl(): string {
  // 优先使用环境变量
  const envApiUrl = import.meta.env.VITE_API_BASE_URL
  if (typeof envApiUrl === 'string') {
    // 空字符串表示使用相对路径（通过Nginx代理）
    return envApiUrl
  }
  
  // 开发环境（Vite dev server）
  if (import.meta.env.DEV) {
    return 'http://localhost:8000'
  }
  
  // 生产环境：使用相对路径，通过Nginx代理
  // Nginx会将 /api 代理到 Docker网络中的 backend:8000
  return ''
}

const API_BASE_URL = getApiBaseUrl()

// 创建axios实例
// 当baseURL为空字符串时，Axios会使用当前页面的origin
// 这样 /api/tasks/ 会被解析为 http://127.0.0.1:3000/api/tasks/
// Nginx会将 /api 代理到 Docker网络中的 backend:8000
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL || undefined, // 空字符串时使用undefined，让Axios使用当前origin
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    // 401错误，清除token并跳转到登录页
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      // 使用router跳转，避免硬刷新
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient


