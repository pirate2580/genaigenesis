import { useState } from "react";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([]);
  
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);

    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    });

    const data = await response.json();
    const botMessage = { role: "bot", text: data.response };

    setMessages((prev) => [...prev, botMessage]);
    setInput("");
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      sendMessage(); 
    }
  };

  return (
    <div id="main-container" className="max-w-md mx-auto p-4 bg-gray-800 text-white rounded-lg shadow-lg">
      <div className="h-64 overflow-y-auto border p-2 space-y-2">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`p-2 rounded ${
              msg.role === "user" ? "bg-blue-500 text-right" : "bg-gray-700"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div className="mt-4 flex">
        <input
          className="flex-grow p-2 rounded-l bg-gray-700 text-white"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown} // ✅ Uses correct function
          placeholder="Type a message..."
        />
        <button
          className="bg-blue-500 p-2 rounded-r hover:bg-blue-700"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default App;
