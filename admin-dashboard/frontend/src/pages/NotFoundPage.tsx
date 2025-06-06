import React from 'react'
import { Link } from 'react-router-dom'

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          {/* 404 Icon */}
          <div className="mx-auto h-32 w-32 text-gray-300 mb-6">
            <svg
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              className="w-full h-full"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.467-.881-6.08-2.33m0 0L3.34 15.25M20.66 15.25l-2.58-2.58M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </div>

          {/* Error Message */}
          <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
          <h2 className="text-xl font-semibold text-gray-700 mb-6">
            Page Not Found
          </h2>
          <p className="text-gray-600 mb-8 max-w-sm mx-auto">
            The page you're looking for doesn't exist or has been moved to a different location.
          </p>

          {/* Action Buttons */}
          <div className="space-y-4">
            <Link
              to="/dashboard"
              className="w-full inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              🏠 Go to Dashboard
            </Link>
            
            <button
              onClick={() => window.history.back()}
              className="w-full inline-flex items-center justify-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              ← Go Back
            </button>
          </div>

          {/* Quick Links */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500 mb-4">Quick Links:</p>
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <Link
                to="/conversations"
                className="text-blue-600 hover:text-blue-800 transition-colors"
              >
                💬 Conversations
              </Link>
              <Link
                to="/ventures"
                className="text-blue-600 hover:text-blue-800 transition-colors"
              >
                🚀 Ventures
              </Link>
              <Link
                to="/analytics"
                className="text-blue-600 hover:text-blue-800 transition-colors"
              >
                📊 Analytics
              </Link>
              <Link
                to="/settings"
                className="text-blue-600 hover:text-blue-800 transition-colors"
              >
                ⚙️ Settings
              </Link>
            </div>
          </div>

          {/* Support Info */}
          <div className="mt-8 text-xs text-gray-400">
            <p>If you believe this is an error, please contact support.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default NotFoundPage