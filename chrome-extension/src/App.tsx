import React, { useState, useEffect, useRef } from "react";

const DarkModeChatbot = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
  }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Add user message
    const userMessage = {
      role: "user" as const,
      content: input,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    
    try {
      // Replace with your actual API endpoint
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      
      if (!response.ok) {
        throw new Error("Failed to get response");
      }
      
      const data = await response.json();
      
      // Add assistant message
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: data.response || "I'm sorry, I couldn't process that request.",
          timestamp: new Date()
        }
      ]);
    } catch (error) {
      console.error("Error:", error);
      // Add error message
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: "I'm having trouble connecting right now. Please try again later.",
          timestamp: new Date()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full w-full rounded-xl overflow-hidden shadow-xl font-sans bg-gray-900 text-gray-100">
      {/* Header */}
      <div className="flex justify-between items-center px-6 py-4 bg-gray-800 border-b border-gray-700">
        <div className="text-lg font-medium flex items-center gap-2">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 5C13.66 5 15 6.34 15 8C15 9.66 13.66 11 12 11C10.34 11 9 9.66 9 8C9 6.34 10.34 5 12 5ZM12 19.2C9.5 19.2 7.29 17.92 6 15.98C6.03 13.99 10 12.9 12 12.9C13.99 12.9 17.97 13.99 18 15.98C16.71 17.92 14.5 19.2 12 19.2Z" fill="#6366F1"/>
          </svg>
          AI Assistant
        </div>
        <button className="text-gray-400 hover:text-gray-200 transition-colors">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
          </svg>
        </button>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6 bg-gray-900">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 text-center">
            <div className="text-5xl mb-4">✨</div>
            <div className="text-lg font-light">How can I help you today?</div>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`flex flex-col max-w-3/4 ${message.role === "user" ? "self-end" : "self-start"}`}
          >
            <div className="flex items-center gap-2 mb-2 text-gray-400">
              {message.role === "assistant" && (
                <div className="w-6 h-6 rounded-full bg-indigo-900/30 flex items-center justify-center text-indigo-400">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 5C13.66 5 15 6.34 15 8C15 9.66 13.66 11 12 11C10.34 11 9 9.66 9 8C9 6.34 10.34 5 12 5ZM12 19.2C9.5 19.2 7.29 17.92 6 15.98C6.03 13.99 10 12.9 12 12.9C13.99 12.9 17.97 13.99 18 15.98C16.71 17.92 14.5 19.2 12 19.2Z" fill="currentColor"/>
                  </svg>
                </div>
              )}
              <div className="text-sm">
                {message.role === "user" ? "You" : "Assistant"}
              </div>
              <div className="text-xs opacity-70">{formatTime(message.timestamp)}</div>
              {message.role === "user" && (
                <div className="w-6 h-6 rounded-full bg-indigo-500/30 flex items-center justify-center ml-1 text-indigo-300">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
                  </svg>
                </div>
              )}
            </div>
            <div className={`py-3 px-4 rounded-lg text-sm leading-relaxed ${
              message.role === "user" 
                ? "bg-indigo-600 text-white" 
                : "bg-gray-800 text-gray-100 border border-gray-700"
            }`}>
              {message.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex flex-col max-w-3/4 self-start">
            <div className="flex items-center gap-2 mb-2 text-gray-400">
              <div className="w-6 h-6 rounded-full bg-indigo-900/30 flex items-center justify-center text-indigo-400">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 5C13.66 5 15 6.34 15 8C15 9.66 13.66 11 12 11C10.34 11 9 9.66 9 8C9 6.34 10.34 5 12 5ZM12 19.2C9.5 19.2 7.29 17.92 6 15.98C6.03 13.99 10 12.9 12 12.9C13.99 12.9 17.97 13.99 18 15.98C16.71 17.92 14.5 19.2 12 19.2Z" fill="currentColor"/>
                </svg>
              </div>
              <div className="text-sm">Assistant</div>
              <div className="text-xs opacity-70">{formatTime(new Date())}</div>
            </div>
            <div className="py-3 px-4 rounded-lg bg-gray-800 border border-gray-700 flex items-center gap-1.5">
              <span className="w-2 h-2 bg-gray-500 rounded-full animate-pulse"></span>
              <span className="w-2 h-2 bg-gray-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></span>
              <span className="w-2 h-2 bg-gray-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input */}
      <div className="p-4 bg-gray-800 border-t border-gray-700">
        <div className="flex gap-2 relative rounded-lg bg-gray-700 focus-within:ring-1 focus-within:ring-indigo-500 transition-all">
          <textarea
            className="flex-1 py-3 px-4 bg-transparent border-none outline-none resize-none text-sm placeholder-gray-400 text-gray-100"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message..."
            rows={1}
          />
          <button 
            className={`p-3 self-end rounded-lg flex items-center justify-center transition-all ${
              input.trim() && !isLoading 
                ? "bg-indigo-600 text-white hover:bg-indigo-700" 
                : "bg-gray-600 text-gray-400 cursor-not-allowed"
            }`}
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
            </svg>
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500 px-1">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default DarkModeChatbot;