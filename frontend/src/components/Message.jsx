import React from 'react';
import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

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

                    {isUser ? (
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                    ) : (
                        <div className="prose prose-sm max-w-none
                            prose-headings:mt-3 prose-headings:mb-1.5 prose-headings:font-semibold prose-headings:text-gray-800
                            prose-h1:text-base prose-h2:text-sm prose-h3:text-sm
                            prose-p:my-1.5 prose-p:leading-relaxed prose-p:text-gray-700
                            prose-strong:text-gray-800 prose-strong:font-semibold
                            prose-ul:my-1.5 prose-ul:pl-4 prose-ol:my-1.5 prose-ol:pl-4
                            prose-li:my-0.5 prose-li:text-gray-700
                            prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-code:text-pink-600
                            prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-pre:rounded-md prose-pre:p-3 prose-pre:my-2
                            prose-a:text-blue-600 prose-a:underline
                            prose-blockquote:border-l-2 prose-blockquote:border-blue-400 prose-blockquote:pl-3 prose-blockquote:italic prose-blockquote:text-gray-600
                        ">
                            <ReactMarkdown>{message.text}</ReactMarkdown>
                        </div>
                    )}

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

