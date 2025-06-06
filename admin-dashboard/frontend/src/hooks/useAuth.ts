import { useState, useEffect, useCallback, createContext, useContext } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

// Types
interface User {
  id: string
  email: string
  name: string
  role: string
  avatar?: string
  permissions: string[]
  lastLogin?: string
  createdAt: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
  refreshAuth: () => Promise<void>
  hasPermission: (permission: string) => boolean
  hasRole: (role: string) => boolean
}

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const TOKEN_KEY = 'openhealth_admin_token'
const REFRESH_TOKEN_KEY = 'openhealth_admin_refresh_token'
const USER_KEY = 'openhealth_admin_user'

// Axios instance with auth interceptors
const authAPI = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
authAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
authAPI.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token } = response.data
          localStorage.setItem(TOKEN_KEY, access_token)

          // Retry the original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return authAPI(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, clear auth data
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        localStorage.removeItem(USER_KEY)
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// Auth Context
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Auth Hook
export const useAuth = (): AuthContextType => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Computed state
  const isAuthenticated = !!user

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem(TOKEN_KEY)
        const storedUser = localStorage.getItem(USER_KEY)

        if (token && storedUser) {
          const userData = JSON.parse(storedUser)
          setUser(userData)

          // Verify token is still valid
          try {
            await authAPI.get('/auth/me')
          } catch (error) {
            // Token is invalid, clear auth data
            logout()
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error)
        logout()
      } finally {
        setIsLoading(false)
      }
    }

    initializeAuth()
  }, [])

  // Login function
  const login = useCallback(async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)

      const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login`, {
        email,
        password,
      })

      const { access_token, refresh_token, user: userData } = response.data

      // Store tokens and user data
      localStorage.setItem(TOKEN_KEY, access_token)
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token)
      localStorage.setItem(USER_KEY, JSON.stringify(userData))

      setUser(userData)
      
      toast.success(`Welcome back, ${userData.name}!`)
      return true
    } catch (error: any) {
      console.error('Login error:', error)
      
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          'Login failed. Please check your credentials.'
      
      toast.error(errorMessage)
      return false
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Logout function
  const logout = useCallback(() => {
    try {
      // Call logout endpoint to invalidate token on server
      authAPI.post('/auth/logout').catch(() => {
        // Ignore errors, we're logging out anyway
      })
    } catch (error) {
      // Ignore errors during logout
    } finally {
      // Clear local storage
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      localStorage.removeItem(USER_KEY)

      setUser(null)
      toast.success('Logged out successfully')
    }
  }, [])

  // Refresh auth data
  const refreshAuth = useCallback(async (): Promise<void> => {
    try {
      const response = await authAPI.get('/auth/me')
      const userData = response.data
      
      localStorage.setItem(USER_KEY, JSON.stringify(userData))
      setUser(userData)
    } catch (error) {
      console.error('Auth refresh error:', error)
      logout()
    }
  }, [logout])

  // Check if user has specific permission
  const hasPermission = useCallback(
    (permission: string): boolean => {
      if (!user) return false
      return user.permissions.includes(permission) || user.permissions.includes('*')
    },
    [user]
  )

  // Check if user has specific role
  const hasRole = useCallback(
    (role: string): boolean => {
      if (!user) return false
      return user.role === role || user.role === 'admin'
    },
    [user]
  )

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshAuth,
    hasPermission,
    hasRole,
  }
}

// Auth Provider Component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const auth = useAuth()

  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>
}

// Hook to use auth context
export const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider')
  }
  return context
}

// Default admin credentials for development
export const DEFAULT_ADMIN_CREDENTIALS = {
  email: 'admin@openhealth.com',
  password: 'admin123',
}

// Permission constants
export const PERMISSIONS = {
  VIEW_CONVERSATIONS: 'view_conversations',
  MANAGE_CONVERSATIONS: 'manage_conversations',
  VIEW_VENTURES: 'view_ventures',
  MANAGE_VENTURES: 'manage_ventures',
  VIEW_ANALYTICS: 'view_analytics',
  MANAGE_SETTINGS: 'manage_settings',
  MANAGE_USERS: 'manage_users',
  EXPORT_DATA: 'export_data',
} as const

// Role constants
export const ROLES = {
  ADMIN: 'admin',
  MANAGER: 'manager',
  ANALYST: 'analyst',
  VIEWER: 'viewer',
} as const

// Export auth API instance for use in other hooks/services
export { authAPI }