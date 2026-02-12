import { useState } from 'react'
import ChatArea from './components/ChatArea'
import FileUpload from './components/FileUpload'

function App() {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
            <div className="w-full max-w-4xl flex flex-col gap-6">

                {/* Header */}
                <div className="text-center mb-4">
                    <h1 className="text-4xl font-bold text-blue-600 mb-2">Medical Assistant</h1>
                    <p className="text-gray-500">Upload medical documents and ask questions</p>
                </div>

                {/* Components */}
                <FileUpload />

                <div className="h-[600px]">
                    <ChatArea />
                </div>

            </div>
        </div>
    )
}

export default App
