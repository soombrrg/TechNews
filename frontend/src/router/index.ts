import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '@/views/HomeView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { title: 'Home' },
  },
  // Auth routes
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: 'Login', guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { title: 'Register', guest: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/auth/ProfileView.vue'),
    meta: { title: 'Profile', requiresAuth: true },
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('@/views/auth/ChangePasswordView.vue'),
    meta: { title: 'Change Password', requiresAuth: true },
  },
  // Posts routes
  {
    path: '/my-posts',
    name: 'MyPosts',
    component: () => import('@/views/posts/MyPostsView.vue'),
    meta: { title: 'My Posts', requiresAuth: true },
  },
  {
    path: '/posts',
    name: 'Posts',
    component: () => import('@/views/posts/PostsListView.vue'),
    meta: { title: 'Posts' },
  },
  {
    path: '/posts/create',
    name: 'PostCreate',
    component: () => import('@/views/posts/PostCreateView.vue'),
    meta: { title: 'Create Post', requiresAuth: true },
  },
  // Routes used in API
  {
    path: '/posts/:slug(popular|recent|pinned|featured)',
    name: 'PostNotFound',
    component: () => import('@/views/posts/PostNotFoundView.vue'),
    meta: { title: 'PostNotFound' },
  },
  {
    path: '/posts/:slug',
    name: 'PostDetail',
    component: () => import('@/views/posts/PostDetailsView.vue'),
    meta: { title: 'Post' },
  },
  {
    path: '/posts/:slug/edit',
    name: 'PostEdit',
    component: () => import('@/views/posts/PostEditView.vue'),
    meta: { title: 'Edit Post', requiresAuth: true },
  },
  // Categories routes
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('@/views/categories/CategoriesView.vue'),
    meta: { title: 'Categories' },
  },
  {
    path: '/categories/:slug',
    name: 'CategoryPosts',
    component: () => import('@/views/categories/CategoryPostsView.vue'),
    meta: { title: 'Category' },
  },
  // Comments routes
  {
    path: '/my-comments',
    name: 'MyComments',
    component: () => import('@/views/comments/MyCommentsView.vue'),
    meta: { title: 'My Comments', requiresAuth: true },
  },
  // Subscriptions routes
  {
    path: '/subscriptions',
    name: 'Subscriptions',
    component: () => import('@/views/subscriptions/SubscriptionPlansView.vue'),
    meta: { title: 'Subscription Plans' },
  },
  {
    path: '/my-subscription',
    name: 'MySubscription',
    component: () => import('@/views/subscriptions/MySubscriptionView.vue'),
    meta: { title: 'My Subscription', requiresAuth: true },
  },
  {
    path: '/subscription-history',
    name: 'SubscriptionHistory',
    component: () => import('@/views/subscriptions/SubscriptionHistoryView.vue'),
    meta: { title: 'Subscription History', requiresAuth: true },
  },
  // Payments routes
  {
    path: '/payments',
    name: 'Payments',
    component: () => import('@/views/payments/PaymentHistoryView.vue'),
    meta: { title: 'Payment History', requiresAuth: true },
  },
  {
    path: '/payment/success',
    name: 'PaymentSuccess',
    component: () => import('@/views/payments/PaymentSuccessView.vue'),
    meta: { title: 'Payment Successful' },
  },
  {
    path: '/payment/cancel',
    name: 'PaymentCancel',
    component: () => import('@/views/payments/PaymentCancelView.vue'),
    meta: { title: 'Payment Cancelled' },
  },
  // About route
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/AboutView.vue'),
    meta: { title: 'About' },
  },
  {
    path: '/payments/analytics',
    name: 'PaymentAnalytics',
    component: () => import('@/views/payments/PaymentAnalyticsView.vue'),
    meta: { title: 'Payment Analytics', requiresAuth: true },
  },
  {
    path: '/payments/refunds',
    name: 'Refunds',
    component: () => import('@/views/payments/RefundsView.vue'),
    meta: { title: 'Refunds', requiresAuth: true },
  },
  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '404 Not Found' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Set page title
  document.title = to.meta.title ? `${to.meta.title} | TechNews` : 'TechNews'

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  }
  // Check if route is for guests only
  else if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
