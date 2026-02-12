import React from 'react';
import { User, Bot } from 'lucide-react';

const Message = ({ message }) => {
    const isUser = message.type === 'user';

    return (
        <div className={`flex w-full mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start gap-2`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? 'bg-blue-500' : 'bg-green-500'}`}>
                    {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
                </div>

                <div className={`p-3 rounded-lg ${isUser
                        ? 'bg-blue-500 text-white rounded-tr-none'
                        : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none shadow-sm'
                    }`}>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>

                    {/* Display sources if available and not user message */}
                    {!isUser && message.sources && message.sources.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-100">
                            <p className="text-xs font-semibold text-gray-500 mb-1">Sources:</p>
                            <div className="flex flex-wrap gap-1">
                                {message.sources.map((source, idx) => (
                                    <span key={idx} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                                        {source}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Message;
