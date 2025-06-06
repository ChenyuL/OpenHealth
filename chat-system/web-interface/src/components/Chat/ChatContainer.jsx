import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import TypingIndicator from './TypingIndicator';
import VentureAnalysisCard from './VentureAnalysisCard';
import MeetingRequestCard from './MeetingRequestCard';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';

const ChatContainer = () => {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [typing, setTyping] = useState(false);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [ventureData, setVentureData] = useState(null);
  const [pendingMeetingRequest, setPendingMeetingRequest] = useState(null);
  const messagesEndRef = useRef(null);
  const retryTimeoutRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, typing]);

  // Load conversation on mount or when conversationId changes
  useEffect(() => {
    if (conversationId) {
      loadConversation(conversationId);
    } else {
      // Start with welcome message for new conversations
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content: `Hello ${user?.name || 'there'}! 👋 I'm OpenHealth AI, your healthcare venture assistant. I'm here to help you explore and develop your healthcare innovation ideas.\n\nFeel free to share:\n• Your healthcare startup concept\n• Market questions or challenges\n• Team or funding needs\n• Technical or regulatory concerns\n\nWhat healthcare idea would you like to discuss today?`,
          timestamp: new Date().toISOString(),
          metadata: { type: 'welcome' }
        }
      ]);
    }
  }, [conversationId, user]);

  const loadConversation = async (id) => {
    try {
      setLoading(true);
      const response = await api.getConversation(id);
      setCurrentConversation(response.conversation);
      setMessages(response.messages || []);
      
      // Load associated venture data if available
      if (response.venture) {
        setVentureData(response.venture);
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
      toast.error('Failed to load conversation');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (content, attachments = []) => {
    if (!content.trim() && attachments.length === 0) return;

    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
      attachments: attachments
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setTyping(true);

    try {
      const response = await api.sendMessage(currentConversation?.id, content, attachments);
      
      // Update conversation ID if this was a new conversation
      if (!currentConversation && response.conversation_id) {
        setCurrentConversation({ id: response.conversation_id });
        navigate(`/chat/${response.conversation_id}`, { replace: true });
      }

      // Add AI response
      const aiMessage = {
        id: response.message_id || `ai-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp || new Date().toISOString(),
        metadata: response.extracted_data || {}
      };

      setMessages(prev => [...prev, aiMessage]);

      // Handle venture analysis
      if (response.venture_data) {
        setVentureData(response.venture_data);
        toast.success('Venture analysis updated!');
      }

      // Handle meeting requests
      if (response.meeting_request) {
        setPendingMeetingRequest(response.meeting_request);
        toast.success('Meeting request detected!');
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: "I apologize, but I'm experiencing some technical difficulties right now. Please try again in a moment, or if the issue persists, our team will be notified to assist you.",
        timestamp: new Date().toISOString(),
        metadata: { type: 'error' }
      };

      setMessages(prev => [...prev, errorMessage]);
      toast.error('Message failed to send. Please try again.');

      // Retry mechanism
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
      retryTimeoutRef.current = setTimeout(() => {
        sendMessage(content, attachments);
      }, 5000);

    } finally {
      setTyping(false);
    }
  };

  const handleFileUpload = async (files) => {
    const uploadedFiles = [];
    
    for (const file of files) {
      try {
        const response = await api.uploadDocument(file, currentConversation?.id);
        uploadedFiles.push({
          id: response.document_id,
          name: file.name,
          type: file.type,
          size: file.size,
          status: response.status
        });
        toast.success(`${file.name} uploaded successfully`);
      } catch (error) {
        console.error('Error uploading file:', error);
        toast.error(`Failed to upload ${file.name}`);
      }
    }

    return uploadedFiles;
  };

  const handleMeetingScheduled = (meetingData) => {
    setPendingMeetingRequest(null);
    toast.success('Meeting scheduled successfully!');
    
    // Add confirmation message
    const confirmationMessage = {
      id: `meeting-${Date.now()}`,
      role: 'assistant',
      content: `Great! I've scheduled a ${meetingData.type} meeting for ${meetingData.date} at ${meetingData.time}. You should receive a calendar invitation shortly with the meeting details.`,
      timestamp: new Date().toISOString(),
      metadata: { type: 'meeting_confirmation', meeting: meetingData }
    };

    setMessages(prev => [...prev, confirmationMessage]);
  };

  const clearChat = () => {
    setMessages([]);
    setCurrentConversation(null);
    setVentureData(null);
    setPendingMeetingRequest(null);
    navigate('/');
  };

  const exportChat = () => {
    const chatData = {
      conversation: currentConversation,
      messages: messages,
      venture: ventureData,
      exportedAt: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(chatData, null, 2)], {
      type: 'application/json'
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `openhealth-chat-${currentConversation?.id || 'export'}.json`;
    link.click();
    URL.revokeObjectURL(url);

    toast.success('Chat exported successfully!');
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading conversation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      {/* Chat Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                {currentConversation?.title || 'Healthcare Discussion'}
              </h1>
              <p className="text-sm text-gray-500">
                AI-powered healthcare venture assistant
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {currentConversation && (
              <>
                <button
                  onClick={exportChat}
                  className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                  title="Export chat"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </button>
                <button
                  onClick={clearChat}
                  className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                  title="New chat"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Main Chat */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            <MessageList messages={messages} />
            {typing && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <div className="border-t border-gray-200 bg-gray-50">
            <MessageInput
              onSendMessage={sendMessage}
              onFileUpload={handleFileUpload}
              disabled={typing}
            />
          </div>
        </div>

        {/* Sidebar for venture data and actions */}
        {(ventureData || pendingMeetingRequest) && (
          <div className="w-80 border-l border-gray-200 bg-gray-50 overflow-y-auto">
            <div className="p-4 space-y-4">
              {ventureData && (
                <VentureAnalysisCard
                  venture={ventureData}
                  onUpdate={(updatedVenture) => setVentureData(updatedVenture)}
                />
              )}
              
              {pendingMeetingRequest && (
                <MeetingRequestCard
                  meetingRequest={pendingMeetingRequest}
                  onSchedule={handleMeetingScheduled}
                  onDismiss={() => setPendingMeetingRequest(null)}
                />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatContainer;