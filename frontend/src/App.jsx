import { useState } from 'react'
import { BookOpen, FileImage } from 'lucide-react'
import ChatArea from './components/ChatArea'
import FileUpload from './components/FileUpload'
import PrescriptionUpload from './components/PrescriptionUpload'
import PrescriptionChat from './components/PrescriptionChat'

function App() {
    const [activeTab, setActiveTab] = useState('knowledge')
    const [sessionId, setSessionId] = useState(null)
    const [prescriptionData, setPrescriptionData] = useState(null)

    const handleSessionCreated = (sid, data) => {
        setSessionId(sid)
        setPrescriptionData(data)
    }

    const tabs = [
        { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
        { id: 'prescription', label: 'Prescription', icon: FileImage },
    ]

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
            <div className="w-full max-w-4xl flex flex-col gap-6">

                {/* Header */}
                <div className="text-center mb-2">
                    <h1 className="text-4xl font-bold text-blue-600 mb-2">Medical Assistant</h1>
                    <p className="text-gray-500">Upload medical documents and ask questions</p>
                </div>

                {/* Tab Navigation */}
                <div className="flex justify-center gap-2">
                    {tabs.map(tab => {
                        const Icon = tab.icon
                        const isActive = activeTab === tab.id
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all
                                    ${isActive
                                        ? tab.id === 'prescription'
                                            ? 'bg-emerald-600 text-white shadow-sm'
                                            : 'bg-blue-600 text-white shadow-sm'
                                        : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                                    }`}
                            >
                                <Icon size={16} />
                                {tab.label}
                            </button>
                        )
                    })}
                </div>

                {/* Knowledge Base Tab */}
                {activeTab === 'knowledge' && (
                    <>
                        <FileUpload />
                        <div className="h-[600px]">
                            <ChatArea />
                        </div>
                    </>
                )}

                {/* Prescription Tab */}
                {activeTab === 'prescription' && (
                    <>
                        <PrescriptionUpload onSessionCreated={handleSessionCreated} />
                        <div className="h-[600px]">
                            <PrescriptionChat sessionId={sessionId} />
                        </div>
                    </>
                )}

            </div>
        </div>
    )
}

export default App
