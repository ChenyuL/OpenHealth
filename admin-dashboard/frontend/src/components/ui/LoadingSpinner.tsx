import React from 'react'
import { clsx } from 'clsx'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  color?: 'primary' | 'secondary' | 'white' | 'gray'
  className?: string
  text?: string
  fullScreen?: boolean
}

const sizeClasses = {
  sm: 'w-4 h-4 border-2',
  md: 'w-6 h-6 border-2',
  lg: 'w-8 h-8 border-3',
  xl: 'w-12 h-12 border-4',
}

const colorClasses = {
  primary: 'border-blue-200 border-t-blue-600',
  secondary: 'border-gray-200 border-t-gray-600',
  white: 'border-white/20 border-t-white',
  gray: 'border-gray-300 border-t-gray-500',
}

const textSizeClasses = {
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-base',
  xl: 'text-lg',
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className = '',
  text,
  fullScreen = false,
}) => {
  const spinnerElement = (
    <div className={clsx('flex flex-col items-center justify-center', className)}>
      <div
        className={clsx(
          'animate-spin rounded-full',
          sizeClasses[size],
          colorClasses[color]
        )}
        role="status"
        aria-label="Loading"
      />
      {text && (
        <p className={clsx('mt-2 font-medium', textSizeClasses[size], {
          'text-white': color === 'white',
          'text-gray-600': color !== 'white',
        })}>
          {text}
        </p>
      )}
      <span className="sr-only">Loading...</span>
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm">
        {spinnerElement}
      </div>
    )
  }

  return spinnerElement
}

// Preset configurations for common use cases
export const InlineSpinner: React.FC<{ className?: string }> = ({ className }) => (
  <LoadingSpinner size="sm" className={clsx('inline-flex', className)} />
)

export const CardSpinner: React.FC<{ text?: string }> = ({ text = 'Loading...' }) => (
  <div className="flex items-center justify-center py-8">
    <LoadingSpinner size="md" text={text} />
  </div>
)

export const PageSpinner: React.FC<{ text?: string }> = ({ text = 'Loading page...' }) => (
  <div className="flex items-center justify-center min-h-[400px]">
    <LoadingSpinner size="lg" text={text} />
  </div>
)

export const FullScreenSpinner: React.FC<{ text?: string }> = ({ text = 'Loading...' }) => (
  <LoadingSpinner size="xl" text={text} fullScreen />
)

// Button spinner for loading states
export const ButtonSpinner: React.FC<{ size?: 'sm' | 'md' }> = ({ size = 'sm' }) => (
  <LoadingSpinner 
    size={size} 
    color="white" 
    className="mr-2" 
  />
)

export default LoadingSpinner