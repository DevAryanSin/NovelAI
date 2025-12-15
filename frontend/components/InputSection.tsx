"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

interface InputSectionProps {
    onProcess: (text: string) => void;
    isProcessing: boolean;
}

export default function InputSection({ onProcess, isProcessing }: InputSectionProps) {
    const [text, setText] = useState("");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (text.trim()) {
            onProcess(text);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-3xl mx-auto bg-white rounded-2xl shadow-lg p-8 border border-slate-200"
        >
            <h2 className="text-xl font-semibold text-slate-800 mb-4">
                Paste your story
            </h2>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Once upon a time..."
                    className="w-full h-48 p-4 rounded-lg border-2 border-slate-200 focus:border-slate-400 focus:ring-2 focus:ring-slate-200 transition-all outline-none text-base text-slate-700 resize-none"
                    disabled={isProcessing}
                />
                <button
                    type="submit"
                    disabled={isProcessing || !text.trim()}
                    className="self-end px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium shadow-sm hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                    {isProcessing ? (
                        <>
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                            >
                                <Sparkles className="w-5 h-5" />
                            </motion.div>
                            Processing...
                        </>
                    ) : (
                        <>
                            Generate <Sparkles className="w-5 h-5" />
                        </>
                    )}
                </button>
            </form>
        </motion.div>
    );
}
