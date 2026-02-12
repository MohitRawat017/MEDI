import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import Message from './Message';
import { askQuestion } from '../services/api';

const ChatArea = () => {
    const [messages, setMessages] = useState([
        { type: 'bot', text: 'Hello! I am your Medical Assistant. How can I help you today?', sources: [] }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');

        // Add user message immediately
        setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
        setIsLoading(true);

        try {
            // Ideally namespace should be dynamic or fixed. Assuming "medical" or derived from logic. 
            // In backend ask_question takes 'namespace' form field.
            // But where do we get it? Maybe hardcode for now or generic "medical_docs".
            const response = await askQuestion(userMessage, "medical_docs");

            // Standardize response extraction. Backend returns { response: "answer", source: [...] }
            // or { response: "I'm sorry...", source: [] }

            const botResponse = {
                type: 'bot',
                text: response.response,
                sources: response.source || []
            };

            setMessages(prev => [...prev, botResponse]);
        } catch (error) {
            console.error("Error asking question:", error);
            setMessages(prev => [...prev, {
                type: 'bot',
                text: "I apologize, but I encountered an error processing your request. Please try again later.",
                sources: []
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
                {messages.map((msg, index) => (
                    <Message key={index} message={msg} />
                ))}

                {isLoading && (
                    <div className="flex justify-start mb-4">
                        <div className="bg-white border border-gray-200 p-3 rounded-lg rounded-tl-none shadow-sm flex items-center gap-2">
                            <Loader2 size={16} className="animate-spin text-blue-500" />
                            <span className="text-sm text-gray-500">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form onSubmit={handleSend} className="p-4 bg-white border-t border-gray-200 flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask a medical question..."
                    className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className={`p-2 rounded-lg transition-colors ${isLoading || !input.trim()
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
                        }`}
                >
                    <Send size={20} />
                </button>
            </form>
        </div>
    );
};

export default ChatArea;
