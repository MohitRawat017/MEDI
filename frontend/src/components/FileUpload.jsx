import React, { useState, useRef } from 'react';
import { Upload, FileText, Check, AlertCircle, Loader2 } from 'lucide-react';
import { uploadPDF } from '../services/api';

const FileUpload = () => {
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState(null); // 'success' | 'error' | null
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setFiles(Array.from(e.target.files));
            setUploadStatus(null);
        }
    };

    const handleUpload = async () => {
        if (files.length === 0) return;

        setUploading(true);
        setUploadStatus(null);
        try {
            await uploadPDF(files);
            setUploadStatus('success');
            setFiles([]); // Clear files after successful upload if desired
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        } catch (error) {
            console.error("Upload failed", error);
            setUploadStatus('error');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <FileText size={18} />
                Knowledge Base Upload
            </h3>

            <div className="flex gap-2 items-center">
                <input
                    type="file"
                    accept=".pdf"
                    multiple
                    onChange={handleFileChange}
                    ref={fileInputRef}
                    className="block w-full text-sm text-gray-500
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-full file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100
                        cursor-pointer
                    "
                    disabled={uploading}
                />

                <button
                    onClick={handleUpload}
                    disabled={files.length === 0 || uploading}
                    className={`px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors
                        ${files.length === 0 || uploading
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
                        }
                    `}
                >
                    {uploading ? (
                        <>
                            <Loader2 size={16} className="animate-spin" />
                            Uploading...
                        </>
                    ) : (
                        <>
                            <Upload size={16} />
                            Upload
                        </>
                    )}
                </button>
            </div>

            {uploadStatus === 'success' && (
                <div className="mt-3 text-xs text-green-600 flex items-center gap-1 bg-green-50 p-2 rounded">
                    <Check size={14} />
                    Files processed and added to knowledge base successfully.
                </div>
            )}

            {uploadStatus === 'error' && (
                <div className="mt-3 text-xs text-red-600 flex items-center gap-1 bg-red-50 p-2 rounded">
                    <AlertCircle size={14} />
                    Failed to upload files. Please try again.
                </div>
            )}
        </div>
    );
};

export default FileUpload;
