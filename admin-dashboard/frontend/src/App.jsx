import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import Dashboard from './components/Dashboard/Dashboard';
import ConversationList from './components/Conversations/ConversationList';
import ConversationView from './components/Conversations/ConversationView';
import VentureList from './components/Ventures/VentureList';
import VentureDetails from './components/Ventures/VentureDetails';
import AnalyticsDashboard from './components/Analytics/AnalyticsDashboard';
import KnowledgeBase from './components/KnowledgeBase/KnowledgeBase';
import Settings from './components/Settings/Settings';
import AdminLogin from './components/Auth/AdminLogin';
import { AdminAuthProvider, useAdminAuth } from './contexts/AdminAuthContext';
import './App.css';

function AdminAppContent() {
  const { admin, loading, isAuthenticated } = useAdminAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 font-medium">Loading OpenHealth Admin...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AdminLogin />;
  }

  return (
    <div className="h-screen flex overflow-hidden bg-gray-100">
      {/* Sidebar */}
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      {/* Main content */}
      <div className="flex flex-col w-0 flex-1 overflow-hidden">
        {/* Header */}
        <Header setSidebarOpen={setSidebarOpen} admin={admin} />

        {/* Main area */}
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          <Routes>
            {/* Dashboard */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />

            {/* Conversations */}
            <Route path="/conversations" element={<ConversationList />} />
            <Route path="/conversations/:conversationId" element={<ConversationView />} />

            {/* Ventures */}
            <Route path="/ventures" element={<VentureList />} />
            <Route path="/ventures/:ventureId" element={<VentureDetails />} />

            {/* Analytics */}
            <Route path="/analytics" element={<AnalyticsDashboard />} />

            {/* Knowledge Base */}
            <Route path="/knowledge" element={<KnowledgeBase />} />

            {/* Settings */}
            <Route path="/settings" element={<Settings />} />

            {/* Redirect unknown routes to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>

      {/* Toast notifications */}
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10B981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#EF4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
}

function WelcomeScreen() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8 text-center">
        <div className="mb-6">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            OpenHealth Admin
          </h1>
          <p className="text-gray-600">
            Healthcare Venture Management Dashboard
          </p>
        </div>

        <div className="space-y-4 text-sm text-gray-600">
          <div className="flex items-center justify-between py-2 border-b border-gray-100">
            <span>Real-time Conversations</span>
            <span className="text-green-600 font-medium">●</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-gray-100">
            <span>Venture Analytics</span>
            <span className="text-green-600 font-medium">●</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-gray-100">
            <span>AI Processing</span>
            <span className="text-green-600 font-medium">●</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span>Knowledge Base</span>
            <span className="text-green-600 font-medium">●</span>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-gray-100">
          <p className="text-xs text-gray-500">
            Secure admin access required
          </p>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <AdminAuthProvider>
      <Router basename="/admin">
        <AdminAppContent />
      </Router>
    </AdminAuthProvider>
  );
}

export default App;