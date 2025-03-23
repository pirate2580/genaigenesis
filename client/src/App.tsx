import React, { useState, useEffect, useRef } from "react";
import AudioButton from "./RecordButton"

const DarkModeChatbot = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
  }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = {
      role: "user" as const,
      content: input,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    console.log(input);


    try {
      const response = await fetch("http://127.0.0.1:5000/agent/browser_control", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      });
      
      if (!response.ok) {
        throw new Error("Failed to get response");
      }
      
      const data = await response.json();
      
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: data.response || "Task Complete",
          timestamp: new Date()
        }
      ]);
    } catch (error) {
      console.error("Error:", error);
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: "Task Complete",
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
    <div className="h-screen w-screen flex flex-col rounded-xl overflow-hidden shadow-xl font-sans bg-gray-900 text-gray-100">
      {/* Header */}
      <div className="flex justify-between items-center px-6 py-4 bg-gray-800 border-b border-gray-700">
        <div className="text-lg font-medium">AI Assistant</div>
        <AudioButton 

          onTranscriptionStart={() => {
            setIsTranscribing(true);
          }}
          
          onTranscription={(transcription) => {
          setIsTranscribing(false);
          setMessages(prev => [...prev, {
            role: "user",
            content: transcription,
            timestamp: new Date()
          }]);
        }}/>
      </div>
  
      {/* Messages Container (Fills remaining space) */}
      <div className="flex-1 overflow-y-auto p-6">

        {isTranscribing && (
          // CHANGED: Display a temporary notification when audio is being transcribed
          <div className="mb-2 text-center text-gray-400 italic">
            Transcribing audio, please wait...
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`max-w-3/4 ${message.role === "user" ? "self-end" : "self-start"}`}>
            <div className="text-sm mb-1 text-gray-400">
              {message.role === "user" ? "You" : "Assistant"} • {formatTime(message.timestamp)}
            </div>
            <div className={`py-3 px-4 rounded-lg text-sm leading-relaxed ${message.role === "user" ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-100 border border-gray-700"}`}>
              {message.content}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Box */}
      <div className="p-4 bg-gray-800 border-t border-gray-700">
        <div className="flex gap-2 rounded-lg bg-gray-700">
          <textarea
            className="flex-1 py-3 px-4 bg-transparent border-none outline-none resize-none text-sm placeholder-gray-400 text-gray-100"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message..."
            rows={1}
          />
          <button 
            className={`p-3 rounded-lg flex items-center justify-center transition-all ${input.trim() && !isLoading ? "bg-indigo-600 text-white hover:bg-indigo-700" : "bg-gray-600 text-gray-400 cursor-not-allowed"}`}
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
};

export default DarkModeChatbot;
