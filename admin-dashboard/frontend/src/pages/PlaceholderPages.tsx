import React from 'react'
import { Link } from 'react-router-dom'

// Login Page
export const LoginPage: React.FC = () => {
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    // Temporary: redirect to dashboard for demo
    window.location.href = '/dashboard'
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-blue-600 mb-2">🏥 OpenHealth</h1>
          <h2 className="text-xl font-semibold text-gray-900">Admin Dashboard</h2>
          <p className="mt-2 text-sm text-gray-600">
            Healthcare venture screening platform
          </p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleLogin}>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  defaultValue="admin@openhealth.com"
                  className="input"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  defaultValue="admin123"
                  className="input"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <div>
              <button type="submit" className="btn btn-primary w-full">
                Sign in
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Demo credentials</span>
              </div>
            </div>

            <div className="mt-4 text-sm text-gray-600 bg-gray-50 p-3 rounded-md">
              <p><strong>Email:</strong> admin@openhealth.com</p>
              <p><strong>Password:</strong> admin123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Layout Component
export const Layout: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-blue-600">🏥 OpenHealth Admin</h1>
            </div>
            <nav className="flex space-x-8">
              <Link to="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
              <Link to="/conversations" className="text-gray-600 hover:text-gray-900">Conversations</Link>
              <Link to="/ventures" className="text-gray-600 hover:text-gray-900">Ventures</Link>
              <Link to="/analytics" className="text-gray-600 hover:text-gray-900">Analytics</Link>
              <Link to="/settings" className="text-gray-600 hover:text-gray-900">Settings</Link>
            </nav>
            <button className="btn btn-secondary btn-sm">Logout</button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}

// Dashboard Page
export const DashboardPage: React.FC = () => {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">🚀 Admin Dashboard</h1>
          <p className="text-gray-600 mb-6">
            Welcome to the OpenHealth admin dashboard. Monitor healthcare ventures and conversations.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="card">
              <h3 className="text-lg font-semibold mb-2">💬 Conversations</h3>
              <p className="text-3xl font-bold text-blue-600">24</p>
              <p className="text-sm text-gray-500">Active chats today</p>
            </div>
            
            <div className="card">
              <h3 className="text-lg font-semibold mb-2">🚀 Ventures</h3>
              <p className="text-3xl font-bold text-green-600">12</p>
              <p className="text-sm text-gray-500">New submissions</p>
            </div>
            
            <div className="card">
              <h3 className="text-lg font-semibold mb-2">📊 Score</h3>
              <p className="text-3xl font-bold text-purple-600">8.4</p>
              <p className="text-sm text-gray-500">Average rating</p>
            </div>
          </div>

          <div className="mt-8">
            <Link to="/conversations" className="btn btn-primary mr-4">
              View Conversations
            </Link>
            <Link to="/ventures" className="btn btn-secondary">
              Manage Ventures
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

// Conversations Page
export const ConversationsPage: React.FC = () => {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">💬 Conversations</h1>
          <p className="text-gray-600 mb-6">
            Monitor and manage healthcare founder conversations with AI assistant.
          </p>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-blue-800">
              Real-time conversation monitoring and venture screening tools will be available here.
            </p>
          </div>

          <Link to="/dashboard" className="btn btn-secondary">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}

// Ventures Page
export const VenturesPage: React.FC = () => {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">🚀 Ventures</h1>
          <p className="text-gray-600 mb-6">
            Healthcare venture pipeline and scoring management.
          </p>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <p className="text-green-800">
              Venture scoring, pipeline tracking, and detailed analysis tools will be available here.
            </p>
          </div>

          <Link to="/dashboard" className="btn btn-secondary">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}

// Analytics Page
export const AnalyticsPage: React.FC = () => {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">📊 Analytics</h1>
          <p className="text-gray-600 mb-6">
            Comprehensive analytics and reporting for healthcare venture insights.
          </p>
          
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
            <p className="text-purple-800">
              Advanced analytics, charts, and reporting dashboards will be available here.
            </p>
          </div>

          <Link to="/dashboard" className="btn btn-secondary">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}

// Settings Page
export const SettingsPage: React.FC = () => {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">⚙️ Settings</h1>
          <p className="text-gray-600 mb-6">
            System configuration and administrative settings.
          </p>
          
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
            <p className="text-gray-800">
              AI configuration, user management, and system settings will be available here.
            </p>
          </div>

          <Link to="/dashboard" className="btn btn-secondary">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}

// Export all components
export default {
  LoginPage,
  Layout,
  DashboardPage,
  ConversationsPage,
  VenturesPage,
  AnalyticsPage,
  SettingsPage,
}