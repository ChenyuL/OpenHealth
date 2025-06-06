import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { LoadingSpinner } from './components/ui/LoadingSpinner'
import { 
  LoginPage, 
  Layout, 
  DashboardPage, 
  ConversationsPage, 
  VenturesPage, 
  AnalyticsPage, 
  SettingsPage 
} from './pages/PlaceholderPages'
import { NotFoundPage } from './pages/NotFoundPage'

// Simplified route components for demo
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // For demo purposes, always show content
  return <>{children}</>
}

const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // For demo purposes, always show content
  return <>{children}</>
}

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Public routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          {/* Dashboard routes */}
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          
          {/* Conversations routes */}
          <Route path="conversations" element={<ConversationsPage />} />
          <Route path="conversations/:id" element={<ConversationsPage />} />
          
          {/* Ventures routes */}
          <Route path="ventures" element={<VenturesPage />} />
          <Route path="ventures/:id" element={<VenturesPage />} />
          
          {/* Analytics routes */}
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="analytics/:type" element={<AnalyticsPage />} />
          
          {/* Settings routes */}
          <Route path="settings" element={<SettingsPage />} />
          <Route path="settings/:section" element={<SettingsPage />} />
        </Route>

        {/* 404 route */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </div>
  )
}

export default App