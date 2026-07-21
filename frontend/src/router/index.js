import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
  {
    path: '/',
    redirect: '/library',
  },
  {
    path: '/library',
    name: 'library',
    component: () => import('../views/LibraryView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/recommender',
    name: 'recommender',
    component: () => import('../views/RecommenderView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/latent-factors',
    name: 'latent-factors',
    component: () => import('../views/LatentFactorsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/movie-map',
    name: 'movie-map',
    component: () => import('../views/MovieMapView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/analysis',
    name: 'analysis',
    component: () => import('../views/AnalysisView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/friends',
    name: 'friends',
    component: () => import('../views/FriendsView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'library' }
  }
  return true
})

export default router
