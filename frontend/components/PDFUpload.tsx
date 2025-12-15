"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, FileText } from "lucide-react";

interface PDFUploadProps {
    onUpload: (file: File) => void;
    isProcessing: boolean;
}

export default function PDFUpload({ onUpload, isProcessing }: PDFUploadProps) {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            if (file.type === "application/pdf") {
                setSelectedFile(file);
            }
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (selectedFile) {
            onUpload(selectedFile);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-3xl mx-auto bg-white rounded-2xl shadow-lg p-8 border border-slate-200"
        >
            <h2 className="text-xl font-semibold text-slate-800 mb-4">
                Upload your novel
            </h2>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div className="relative">
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={handleChange}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        disabled={isProcessing}
                        id="pdf-upload"
                    />
                    <label
                        htmlFor="pdf-upload"
                        className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-slate-300 rounded-lg hover:border-slate-400 transition-colors cursor-pointer bg-slate-50"
                    >
                        {selectedFile ? (
                            <div className="flex flex-col items-center gap-2">
                                <FileText className="w-12 h-12 text-slate-600" />
                                <p className="text-base font-medium text-slate-800">
                                    {selectedFile.name}
                                </p>
                                <p className="text-sm text-slate-500">
                                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center gap-2">
                                <Upload className="w-12 h-12 text-slate-400" />
                                <p className="text-base text-slate-600">
                                    Click to upload PDF
                                </p>
                                <p className="text-sm text-slate-400">
                                    PDF files only
                                </p>
                            </div>
                        )}
                    </label>
                </div>
                <button
                    type="submit"
                    disabled={!selectedFile || isProcessing}
                    className="self-end px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium shadow-sm hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                    {isProcessing ? (
                        <>
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                            />
                            Processing...
                        </>
                    ) : (
                        <>
                            Generate Book
                        </>
                    )}
                </button>
            </form>
        </motion.div>
    );
}
