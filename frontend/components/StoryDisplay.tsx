"use client";

import { motion } from "framer-motion";
import { ProcessResult } from "@/app/actions";
import { RotateCcw } from "lucide-react";

interface StoryDisplayProps {
    result: ProcessResult;
    onReset: () => void;
}

export default function StoryDisplay({ result, onReset }: StoryDisplayProps) {
    const paragraphs = (result.simplifiedText || "").split("\n").filter(p => p.trim());

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-6xl mx-auto"
        >
            {/* Reset Button */}
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-bold text-slate-800">Your Story</h2>
                <button
                    onClick={onReset}
                    className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-slate-50 text-slate-700 rounded-lg border border-slate-200 transition-colors"
                >
                    <RotateCcw className="w-4 h-4" />
                    New Story
                </button>
            </div>

            {/* Text Left, Image Right */}
            <div className="grid md:grid-cols-2 gap-8 bg-white rounded-2xl shadow-lg overflow-hidden border border-slate-200">

                {/*  Text Content */}
                <div className="p-8 md:p-12 overflow-y-auto max-h-[600px]">
                    <div className="prose prose-slate max-w-none">
                        {paragraphs.map((p, i) => (
                            <p key={i} className="mb-4 text-slate-700 leading-relaxed text-base">
                                {p}
                            </p>
                        ))}
                    </div>
                </div>

                {/*  Generated Image */}
                <div className="relative bg-slate-50 flex items-center justify-center p-8">
                    {result.image ? (
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            transition={{ delay: 0.2 }}
                            className="w-full h-full flex flex-col"
                        >
                            <img
                                src={result.image}
                                alt={result.imagePrompt}
                                className="w-full h-auto rounded-lg shadow-md object-contain"
                            />
                            <p className="mt-4 text-sm text-slate-500 italic text-center">
                                "{result.imagePrompt}"
                            </p>
                        </motion.div>
                    ) : (
                        <div className="text-slate-400 text-center">
                            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-200 flex items-center justify-center">
                                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                            </div>
                            <p>No image generated</p>
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
