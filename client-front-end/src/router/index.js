import { createRouter, createWebHistory } from 'vue-router';
import Cookies from "js-cookie";
import HomeView from '@/views/HomeView.vue';
import RegisterView from '@/views/RegisterView.vue';
import LoginView from "@/views/LoginView.vue";
import LoginInbox from "@/views/LoginInbox.vue";
import StaffHomeView from '@/views/StaffViews/StaffHomeView.vue';

const routes = [
  {
    path: '/',
    redirect: '/inbox',
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {title: '账号密码登录'}
  },
  {
    path: '/inbox',
    name: 'inbox',
    component: LoginInbox,
    meta: {title: '体育俱乐部'}
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: {title: '注册账号'}
  },
  {
    path: '/findAccount',
    name: 'findAccount',
    component: () => import('../views/FindAccount.vue'),
    meta: {title: '找回用户名'}
  },
  {
    path: '/adminFindAccount',
    name: 'adminFindAccount',
    component: () => import('../views/FindAccount.vue'),
    meta: {title: '找回用户名 · 体育俱乐部'}
  },
  {
    path: '/resetPassword',
    name: 'resetPassword',
    component: () => import('../views/ResetPassword.vue'),
    meta: {title: '重置密码'}
  },
  {
    path: '/adminResetPassword',
    name: 'adminResetPassword',
    component: () => import('../views/ResetPassword.vue'),
    meta: {title: '重置密码 · 体育俱乐部'}
  }
  ,{
    path: '/main',
    name: 'MemberHomeView',
    component: HomeView,
    meta: {title: '体育俱乐部'},
    children: [
      { path: '',
        redirect: '/main/action'},
      { path: 'membership',
        name: 'member_membership',
        component: () => import('../views/MemberViews/InboxView.vue')},
      { path: 'action',
        component: () => import('../views/MemberViews/ActionView.vue')},
      { path: 'records',
        component: () => import('../views/MemberViews/RecordsView.vue')},
      { path: 'others',
        component: () => import('../views/MemberViews/OthersView.vue'),
      }
    ]
  },{
    path:'/staff',
    name: 'StaffHomeView',
    component: StaffHomeView,
    meta: {title: '工作人员值班'},
    children: [
      { path: 'membership',
        name: 'staff_membership',
        component: () => import('../views/MemberViews/InboxView.vue')},
      { path: 'work',
        component: () => import('../views/StaffViews/StaffWorkView.vue')},
      { path: '',
        redirect: '/staff/work'}
    ]
  },
  {
    path: '/staff/scan',
    name: 'StaffScanView',
    component: () => import('../views/StaffViews/StaffScanView.vue'),
    meta: {title: '签到核验'}
  },
  {
    path: '/:catchAll(.*)',
    meta: {title: '页面不存在'},
    component: () => import('../views/404.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta && to.meta.title) {
    document.title = to.meta.title; // 设置页面标题
  }
  next();
});
export default router
