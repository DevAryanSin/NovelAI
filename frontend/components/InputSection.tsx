"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Wand2 } from "lucide-react";

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
            className="w-full max-w-3xl mx-auto bg-white rounded-3xl shadow-xl p-8 border border-purple-100"
        >
            <h2 className="text-2xl font-bold text-purple-600 mb-4 flex items-center gap-2">
                <Wand2 className="w-6 h-6" /> paste your story here!
            </h2>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Once upon a time..."
                    className="w-full h-48 p-4 rounded-xl border-2 border-purple-100 focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all outline-none text-lg text-slate-700 resize-none font-medium"
                    disabled={isProcessing}
                />
                <button
                    type="submit"
                    disabled={isProcessing || !text.trim()}
                    className="self-end px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-full font-bold text-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                    {isProcessing ? (
                        <>
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                            >
                                <Wand2 className="w-5 h-5" />
                            </motion.div>
                            Working Magic...
                        </>
                    ) : (
                        <>
                            Magicify! <Wand2 className="w-5 h-5" />
                        </>
                    )}
                </button>
            </form>
        </motion.div>
    );
}
