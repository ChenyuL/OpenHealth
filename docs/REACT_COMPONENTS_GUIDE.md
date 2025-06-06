# React Components Guide for OpenHealth

## 🎯 Overview
This guide will help you understand and create React components for the OpenHealth application. We'll cover the essential concepts you need to know and provide practical examples.

## 📚 Essential React Concepts to Learn

### 1. **Functional Components & Hooks**
Modern React uses functional components with hooks instead of class components.

```jsx
import React, { useState, useEffect } from 'react';

function ChatMessage({ message, user }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className={`message ${isVisible ? 'visible' : ''}`}>
      <span className="user">{user}:</span>
      <span className="content">{message}</span>
    </div>
  );
}
```

### 2. **State Management with useState**
```jsx
const [conversations, setConversations] = useState([]);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
```

### 3. **Side Effects with useEffect**
```jsx
useEffect(() => {
  // Fetch data when component mounts
  fetchConversations();
}, []); // Empty dependency array = run once

useEffect(() => {
  // Run when userId changes
  fetchUserData(userId);
}, [userId]); // Run when userId changes
```

### 4. **Props & Component Communication**
```jsx
// Parent component
function ChatApp() {
  const [messages, setMessages] = useState([]);
  
  return (
    <div>
      <MessageList messages={messages} />
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
}

// Child component
function MessageInput({ onSendMessage }) {
  const [input, setInput] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onSendMessage(input);
    setInput('');
  };
}
```

## 🏗️ OpenHealth Component Architecture

### 1. **Chat System Components**
```
src/
├── components/
│   ├── Chat/
│   │   ├── ChatContainer.jsx       # Main chat interface
│   │   ├── MessageList.jsx         # Display messages
│   │   ├── MessageInput.jsx        # User input
│   │   ├── MessageBubble.jsx       # Individual message
│   │   └── TypingIndicator.jsx     # Show AI thinking
│   ├── User/
│   │   ├── UserProfile.jsx         # User info display
│   │   └── UserSettings.jsx        # User preferences
│   └── Layout/
│       ├── Header.jsx              # App header
│       ├── Sidebar.jsx             # Navigation
│       └── Footer.jsx              # App footer
```

### 2. **Admin Dashboard Components**
```
src/
├── components/
│   ├── Dashboard/
│   │   ├── DashboardHome.jsx       # Main dashboard
│   │   ├── MetricsCard.jsx         # KPI displays
│   │   └── QuickActions.jsx        # Action buttons
│   ├── Conversations/
│   │   ├── ConversationList.jsx    # List all chats
│   │   ├── ConversationView.jsx    # View single chat
│   │   └── ConversationFilters.jsx # Filter/search
│   ├── Ventures/
│   │   ├── VentureList.jsx         # List ventures
│   │   ├── VentureCard.jsx         # Venture summary
│   │   ├── VentureDetails.jsx      # Detailed view
│   │   └── VentureScoring.jsx      # Scoring interface
│   └── Analytics/
│       ├── AnalyticsDashboard.jsx  # Analytics overview
│       ├── Charts.jsx              # Data visualizations
│       └── Reports.jsx             # Generate reports
```

## 🎨 Styling with Tailwind CSS

OpenHealth uses Tailwind CSS for styling. Here are common patterns:

### Layout Classes
```jsx
<div className="flex flex-col h-screen bg-gray-50">
  <header className="bg-white shadow-sm border-b">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header content */}
    </div>
  </header>
  
  <main className="flex-1 overflow-y-auto">
    {/* Main content */}
  </main>
</div>
```

### Message Styling
```jsx
<div className={`
  flex mb-4 
  ${message.role === 'user' ? 'justify-end' : 'justify-start'}
`}>
  <div className={`
    max-w-xs lg:max-w-md px-4 py-2 rounded-lg
    ${message.role === 'user' 
      ? 'bg-blue-500 text-white' 
      : 'bg-white text-gray-800 shadow-sm'
    }
  `}>
    {message.content}
  </div>
</div>
```

## 🔌 API Integration Patterns

### 1. **Custom Hooks for API Calls**
```jsx
// hooks/useAPI.js
import { useState, useEffect } from 'react';

export function useConversations() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchConversations() {
      try {
        const response = await fetch('/api/v1/conversations', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        const data = await response.json();
        setConversations(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchConversations();
  }, []);

  return { conversations, loading, error };
}
```

### 2. **API Service Functions**
```jsx
// services/api.js
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = {
  async sendMessage(conversationId, message) {
    const response = await fetch(`${API_BASE}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        message: message
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to send message');
    }
    
    return response.json();
  },

  async getConversations() {
    const response = await fetch(`${API_BASE}/api/v1/conversations`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    });
    return response.json();
  }
};
```

## 🚀 Component Templates

### 1. **Basic Chat Component**
```jsx
import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

function ChatContainer() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await api.sendMessage(null, inputValue);
      
      const aiMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}
        {loading && <TypingIndicator />}
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Tell me about your healthcare idea..."
            className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 2. **Admin Dashboard Card**
```jsx
function MetricsCard({ title, value, change, icon: Icon }) {
  const isPositive = change >= 0;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
        </div>
        <div className="p-3 bg-blue-50 rounded-full">
          <Icon className="h-6 w-6 text-blue-600" />
        </div>
      </div>
      
      {change !== undefined && (
        <div className="mt-4 flex items-center">
          <span className={`text-sm font-medium ${
            isPositive ? 'text-green-600' : 'text-red-600'
          }`}>
            {isPositive ? '+' : ''}{change}%
          </span>
          <span className="text-sm text-gray-500 ml-2">vs last month</span>
        </div>
      )}
    </div>
  );
}
```

## 🛠️ Development Tools & Setup

### 1. **Required Dependencies**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0",
    "tailwindcss": "^3.2.0",
    "@headlessui/react": "^1.7.0",
    "@heroicons/react": "^2.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^3.1.0",
    "vite": "^4.1.0",
    "eslint": "^8.34.0",
    "prettier": "^2.8.0"
  }
}
```

### 2. **Project Structure Best Practices**
```
src/
├── components/          # Reusable UI components
├── pages/              # Page-level components
├── hooks/              # Custom React hooks
├── services/           # API calls and external services
├── utils/              # Helper functions
├── contexts/           # React Context providers
├── assets/             # Images, icons, etc.
└── styles/             # Global styles and Tailwind config
```

## 📝 Key Learning Resources

### 1. **Essential Concepts to Master**
- **React Hooks**: useState, useEffect, useContext, useReducer
- **Component Patterns**: Props, composition, conditional rendering
- **State Management**: Local state vs global state
- **API Integration**: fetch, axios, error handling
- **Routing**: React Router for navigation
- **Styling**: Tailwind CSS classes and responsive design

### 2. **Recommended Learning Path**
1. **Start with**: React official tutorial
2. **Practice**: Build simple components (buttons, forms, lists)
3. **Learn**: API integration with useEffect
4. **Advance**: Custom hooks and context
5. **Master**: Performance optimization and testing

### 3. **Quick Prompts for ChatGPT/Claude**
- "Create a React component for displaying a list of conversations"
- "Show me how to handle form submission in React with hooks"
- "Help me create a custom hook for API calls with loading states"
- "Create a responsive card component using Tailwind CSS"
- "Show me how to implement real-time chat with WebSockets in React"

## 🎯 Next Steps

1. **Start Small**: Create basic components (buttons, inputs, cards)
2. **Build Up**: Combine components into larger features
3. **Add Interactivity**: Handle user events and state changes
4. **Connect APIs**: Integrate with the OpenHealth backend
5. **Style & Polish**: Apply Tailwind CSS for professional look

Remember: React is about breaking down complex UIs into smaller, reusable components. Start simple and gradually add complexity!