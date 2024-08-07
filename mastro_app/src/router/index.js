import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DevicesView from '../views/DevicesView.vue'
import DataTable from '../views/DataTableView.vue'

import { useUser } from '../store/counter';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/measurements',
    name: 'measurements',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/MeasurementsView.vue')
  },
  {
    path: '/devices',
    name: 'devices',
    component: DevicesView
  },
  {
    path: '/data_table',
    name: 'data_table',
    component: DataTable
  },
  {
    path: '/graphql',
    name: 'graphql',
    component: () => import('../views/GraphqlView.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/pinia',
    name: 'pinia',
    component: () => import('../views/TryPiniaView.vue')
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue')
  }
]

export const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Middleware de autenticación
router.beforeEach(async (to) => {
  const useUserStore = useUser();
  const isAuthenticated = await useUserStore.tryToken()

  if (!isAuthenticated && to.name !== 'login')
  {
    router.push('/login');
  }
  if (isAuthenticated && to.name === 'login')
  {
    router.push('/');
  }
})

export default router
