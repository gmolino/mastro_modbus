import axios from "axios"
import { router } from '../router/index.js'
import { defineStore } from 'pinia'

axios.defaults.baseURL = "http://localhost:5000"
// axios.defaults.baseURL = "https://api.reinvent.witmo.eu"
axios.defaults.headers.common['Authorization'] = "Bearer " + localStorage.getItem("token");

export const useCounter = defineStore('counter', {
  state: () => ({count: 0}),
  actions: {
    increment() {
      this.count++
    },
    resetCount() {
      this.count = 0
    }
  },
  persist: true
})

export const useUser = defineStore('user', {
  state: () => ({
      token: "xxxxxxx-xxxxxx-xxxxxx-xx",
      isAuthenticated: false,
      user: {
          email: null,
          is_active:false,
          is_superuser:false,
          full_name:null,
          id: null
      }
  }),
  actions: {
    async fetchUser(email, password) {
      try {
        const data = await axios.post(
          "/api/v1/login/access-token", {
            username:email, password:password
          }, {
            headers: {'Content-Type': 'multipart/form-data'},
          }
        )
        this.token = data.data.access_token
        this.isAuthenticated = true
        router.push('/');
      } catch (error) {
        alert("Wrong email or password");
        this.isAuthenticated = false
      }

    },
    async tryToken() {
      try {
        const data = await axios.post(
          "/api/v1/login/test-token", {},{
            headers: {
              'Authorization': `Bearer ${this.token}`
            },
          }
        )
        this.user = data.data
        this.isAuthenticated = true
        return true
      } catch (error) {
        this.isAuthenticated = false
        return false
      }
    },
    logout() {
      this.token = null
      this.isAuthenticated = false
      router.push('/login');
    }
  },
  persist: true
})

export const useDatabases = defineStore('databases', {
  state: () => ({
    databases: [],
    selectedDatabase: ""
  }),
  actions: {
    async fetchDatabases() {
      try {
        const data = await axios.get(
          "/api/v1/sincere/databases"
        )
        this.databases = data.data
        this.selectedDatabase = this.databases[0]
      } catch (error) {
        alert(error);
      }
    }
  },
  persist: false
})