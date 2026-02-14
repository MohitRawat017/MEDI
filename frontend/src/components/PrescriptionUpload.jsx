import React, { useState, useRef } from 'react';
import { Upload, Image, Check, AlertCircle, Loader2, User as UserIcon, Pill, Calendar, Stethoscope } from 'lucide-react';
import { uploadPrescription } from '../services/api';

const PrescriptionUpload = ({ onSessionCreated }) => {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState(null);
    const [prescriptionData, setPrescriptionData] = useState(null);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const selected = e.target.files?.[0];
        if (selected) {
            setFile(selected);
            setUploadStatus(null);
            setPrescriptionData(null);

            // Create image preview
            const reader = new FileReader();
            reader.onloadend = () => setPreview(reader.result);
            reader.readAsDataURL(selected);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setUploadStatus(null);
        try {
            const result = await uploadPrescription(file);
            setUploadStatus('success');
            setPrescriptionData(result.prescription_data);
            onSessionCreated(result.session_id, result.prescription_data);
        } catch (error) {
            console.error("Prescription upload failed", error);
            setUploadStatus('error');
        } finally {
            setUploading(false);
        }
    };

    const handleReset = () => {
        setFile(null);
        setPreview(null);
        setUploadStatus(null);
        setPrescriptionData(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    return (
        <div className="p-5 bg-white rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <Image size={18} className="text-emerald-600" />
                Prescription Upload
            </h3>

            {/* Upload area */}
            {!preview ? (
                <label className="flex flex-col items-center justify-center w-full h-40 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-emerald-400 hover:bg-emerald-50/30 transition-all">
                    <Upload size={28} className="text-gray-400 mb-2" />
                    <span className="text-sm text-gray-500">Click to upload prescription image</span>
                    <span className="text-xs text-gray-400 mt-1">JPG, PNG, or WEBP</span>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        ref={fileInputRef}
                        className="hidden"
                        disabled={uploading}
                    />
                </label>
            ) : (
                <div className="space-y-3">
                    {/* Image Preview */}
                    <div className="relative rounded-xl overflow-hidden border border-gray-200 bg-gray-50">
                        <img
                            src={preview}
                            alt="Prescription preview"
                            className="w-full max-h-64 object-contain"
                        />
                        {!uploading && !prescriptionData && (
                            <button
                                onClick={handleReset}
                                className="absolute top-2 right-2 bg-white/90 hover:bg-white text-gray-600 rounded-full p-1.5 shadow-sm transition-colors"
                                title="Remove"
                            >
                                ✕
                            </button>
                        )}
                    </div>

                    {/* Action buttons */}
                    {!prescriptionData && (
                        <div className="flex gap-2">
                            <button
                                onClick={handleUpload}
                                disabled={uploading}
                                className={`flex-1 px-4 py-2.5 rounded-lg flex items-center justify-center gap-2 text-sm font-medium transition-all
                                    ${uploading
                                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                        : 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm'
                                    }`}
                            >
                                {uploading ? (
                                    <>
                                        <Loader2 size={16} className="animate-spin" />
                                        Processing OCR...
                                    </>
                                ) : (
                                    <>
                                        <Stethoscope size={16} />
                                        Analyze Prescription
                                    </>
                                )}
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* Success — Parsed Data Summary */}
            {uploadStatus === 'success' && prescriptionData && (
                <div className="mt-4 space-y-3">
                    <div className="flex items-center gap-1.5 text-xs text-emerald-600 bg-emerald-50 p-2.5 rounded-lg">
                        <Check size={14} />
                        Prescription analyzed successfully
                    </div>

                    {/* Patient Info */}
                    {prescriptionData.patient_info && (
                        <div className="bg-gray-50 rounded-lg p-3 space-y-1.5">
                            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide flex items-center gap-1.5">
                                <UserIcon size={12} /> Patient
                            </h4>
                            <div className="grid grid-cols-2 gap-1 text-sm text-gray-700">
                                {prescriptionData.patient_info.name && (
                                    <span><strong>Name:</strong> {prescriptionData.patient_info.name}</span>
                                )}
                                {prescriptionData.patient_info.age && (
                                    <span><strong>Age:</strong> {prescriptionData.patient_info.age}</span>
                                )}
                                {prescriptionData.patient_info.sex && (
                                    <span><strong>Sex:</strong> {prescriptionData.patient_info.sex}</span>
                                )}
                                {prescriptionData.patient_info.appointment_date && (
                                    <span><strong>Date:</strong> {prescriptionData.patient_info.appointment_date}</span>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Diagnosis */}
                    {prescriptionData.diagnosis && (
                        <div className="bg-blue-50 rounded-lg p-3">
                            <h4 className="text-xs font-semibold text-blue-600 uppercase tracking-wide flex items-center gap-1.5 mb-1">
                                <Stethoscope size={12} /> Diagnosis
                            </h4>
                            <p className="text-sm text-gray-700">{prescriptionData.diagnosis}</p>
                        </div>
                    )}

                    {/* Medications */}
                    {prescriptionData.medications?.length > 0 && (
                        <div className="bg-amber-50 rounded-lg p-3">
                            <h4 className="text-xs font-semibold text-amber-700 uppercase tracking-wide flex items-center gap-1.5 mb-2">
                                <Pill size={12} /> Medications ({prescriptionData.medications.length})
                            </h4>
                            <div className="space-y-1.5">
                                {prescriptionData.medications.map((med, idx) => (
                                    <div key={idx} className="text-sm text-gray-700 bg-white rounded-md px-3 py-2 border border-amber-200">
                                        <span className="font-medium">{med.name}</span>
                                        {med.dose && <span className="text-gray-500 ml-2">• {med.dose}</span>}
                                        {med.frequency && <span className="text-gray-500 ml-2">• {med.frequency}</span>}
                                        {med.duration && <span className="text-gray-500 ml-2">• {med.duration}</span>}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Follow-up */}
                    {prescriptionData.follow_up?.length > 0 && (
                        <div className="bg-purple-50 rounded-lg p-3">
                            <h4 className="text-xs font-semibold text-purple-600 uppercase tracking-wide flex items-center gap-1.5 mb-1">
                                <Calendar size={12} /> Follow-up
                            </h4>
                            <ul className="text-sm text-gray-700 list-disc list-inside">
                                {prescriptionData.follow_up.map((item, idx) => (
                                    <li key={idx}>{item}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* New prescription button */}
                    <button
                        onClick={handleReset}
                        className="w-full text-xs text-gray-500 hover:text-gray-700 py-2 transition-colors"
                    >
                        Upload a different prescription
                    </button>
                </div>
            )}

            {/* Error */}
            {uploadStatus === 'error' && (
                <div className="mt-3 text-xs text-red-600 flex items-center gap-1 bg-red-50 p-2.5 rounded-lg">
                    <AlertCircle size={14} />
                    Failed to analyze prescription. Please try again.
                </div>
            )}
        </div>
    );
};

export default PrescriptionUpload;
