import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/policies',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'policies',
        name: 'Policies',
        component: () => import('../views/Policies.vue'),
        meta: { title: '政策列表' },
      },
      {
        path: 'policies/:id',
        name: 'PolicyDetail',
        component: () => import('../views/PolicyDetail.vue'),
        meta: { title: '政策详情' },
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('../views/Tasks.vue'),
        meta: { title: '任务管理' },
      },
      {
        path: 'scheduled-tasks',
        name: 'ScheduledTasks',
        component: () => import('../views/ScheduledTasks.vue'),
        meta: { title: '定时任务' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue'),
        meta: { title: '系统设置' },
      },
      {
        path: 'backups',
        name: 'Backups',
        component: () => import('../views/Backups.vue'),
        meta: { title: '备份管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Policies' })
  } else {
    next()
  }
})

export default router


