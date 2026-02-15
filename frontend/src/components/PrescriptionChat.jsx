import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, AlertCircle, ShieldCheck, ShieldAlert } from 'lucide-react';
import Message from './Message';
import { askPrescription } from '../services/api';

// ==============================
// Hallucination Warning Component
// ==============================
const HallucinationBanner = ({ check }) => {
    if (!check || check.hallucination_count === 0) {
        return (
            <div className="flex items-center gap-1.5 text-xs text-green-600 bg-green-50 px-3 py-1.5 rounded-md mx-4 -mt-2 mb-2">
                <ShieldCheck size={12} />
                <span>Answer grounded in prescription & API data</span>
            </div>
        );
    }

    return (
        <div className="mx-4 -mt-2 mb-2 space-y-1">
            <div className="flex items-center gap-1.5 text-xs text-amber-600 bg-amber-50 px-3 py-1.5 rounded-md">
                <ShieldAlert size={12} />
                <span>
                    {check.hallucination_count} unsupported claim{check.hallucination_count > 1 ? 's' : ''} detected
                </span>
            </div>
            {check.hallucinations?.map((h, idx) => (
                <div key={idx} className="text-xs bg-amber-50/50 border border-amber-100 rounded-md px-3 py-1.5 ml-5">
                    <span className={`font-medium ${h.severity === 'High' ? 'text-red-600' :
                            h.severity === 'Medium' ? 'text-amber-600' : 'text-yellow-600'
                        }`}>
                        [{h.severity}]
                    </span>
                    <span className="text-gray-600 ml-1">{h.claim}</span>
                </div>
            ))}
        </div>
    );
};


const PrescriptionChat = ({ sessionId }) => {
    const [messages, setMessages] = useState([
        {
            type: 'bot',
            text: 'Your prescription has been analyzed! Ask me anything about the medications, dosages, diagnosis, or follow-up instructions.',
            sources: []
        }
    ]);
    const [hallucinationChecks, setHallucinationChecks] = useState({});
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const quickQuestions = [
        "What medications were prescribed?",
        "Are there any side effects I should know about?",
        "What is the dosage schedule?",
        "Any dietary restrictions with these medicines?",
    ];

    const handleSend = async (questionText) => {
        const userMessage = (questionText || input).trim();
        if (!userMessage || isLoading) return;

        setInput('');
        setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
        setIsLoading(true);

        try {
            const response = await askPrescription(sessionId, userMessage);

            const newMsgIndex = messages.length + 1; // +1 for user msg we just added
            setMessages(prev => [...prev, {
                type: 'bot',
                text: response.answer || "I couldn't generate an answer. Please try again.",
                sources: []
            }]);

            // Store hallucination check for this message
            if (response.hallucination_check) {
                setHallucinationChecks(prev => ({
                    ...prev,
                    [newMsgIndex]: response.hallucination_check
                }));
            }
        } catch (error) {
            console.error("Error asking prescription question:", error);
            setMessages(prev => [...prev, {
                type: 'bot',
                text: "I apologize, but I encountered an error. Please try again.",
                sources: []
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    if (!sessionId) {
        return (
            <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border border-gray-200 items-center justify-center p-8">
                <AlertCircle size={32} className="text-gray-300 mb-3" />
                <p className="text-gray-400 text-sm text-center">
                    Upload and analyze a prescription first to start asking questions
                </p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
                {messages.map((msg, index) => (
                    <React.Fragment key={index}>
                        <Message message={msg} />
                        {/* Show hallucination check after bot messages */}
                        {msg.type === 'bot' && hallucinationChecks[index] && (
                            <HallucinationBanner check={hallucinationChecks[index]} />
                        )}
                    </React.Fragment>
                ))}

                {/* Quick Questions (show only at the start) */}
                {messages.length <= 1 && !isLoading && (
                    <div className="mt-3 space-y-2">
                        <p className="text-xs text-gray-400 font-medium">Quick questions:</p>
                        <div className="flex flex-wrap gap-2">
                            {quickQuestions.map((q, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => handleSend(q)}
                                    className="text-xs bg-white border border-emerald-200 text-emerald-700 px-3 py-1.5 rounded-full hover:bg-emerald-50 transition-colors"
                                >
                                    {q}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {isLoading && (
                    <div className="flex justify-start mb-4">
                        <div className="bg-white border border-gray-200 p-3 rounded-lg rounded-tl-none shadow-sm flex items-center gap-2">
                            <Loader2 size={16} className="animate-spin text-emerald-500" />
                            <span className="text-sm text-gray-500">Analyzing...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="p-4 bg-white border-t border-gray-200 flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about your prescription..."
                    className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className={`p-2 rounded-lg transition-colors ${isLoading || !input.trim()
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm'
                        }`}
                >
                    <Send size={20} />
                </button>
            </form>
        </div>
    );
};

export default PrescriptionChat;
