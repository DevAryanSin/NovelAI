"use client";

import { motion } from "framer-motion";
import { ProcessResult } from "@/app/actions";
import { Play, Image as ImageIcon } from "lucide-react";

interface StoryDisplayProps {
    result: ProcessResult;
    onReset: () => void;
}

export default function StoryDisplay({ result, onReset }: StoryDisplayProps) {
    const paragraphs = (result.simplifiedText || "").split("\n").filter(p => p.trim());

    return (
        <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-4xl mx-auto space-y-8"
        >
            <div className="flex justify-between items-center">
                <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
                    Your Magic Story
                </h2>
                <button
                    onClick={onReset}
                    className="px-4 py-2 text-purple-600 font-semibold hover:bg-purple-50 rounded-lg transition-colors"
                >
                    Create New
                </button>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
                {/* Left Column: Visuals */}
                <div className="space-y-6">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 0.2 }}
                        className="bg-white p-2 rounded-3xl shadow-lg border-4 border-yellow-200 rotate-1 transform hover:rotate-0 transition-transform duration-500"
                    >
                        <div className="relative aspect-video rounded-2xl overflow-hidden bg-gray-100">
                            {result.imageUrl ? (
                                <img
                                    src={result.imageUrl}
                                    alt={result.prompts.imagePrompt}
                                    className="w-full h-full object-cover"
                                />
                            ) : (
                                <div className="flex items-center justify-center h-full text-gray-300">
                                    <ImageIcon className="w-12 h-12" />
                                </div>
                            )}
                            <div className="absolute bottom-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded-full">
                                AI Illustration
                            </div>
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 0.4 }}
                        className="bg-white p-2 rounded-3xl shadow-lg border-4 border-blue-200 -rotate-1 transform hover:rotate-0 transition-transform duration-500"
                    >
                        <div className="relative aspect-video rounded-2xl overflow-hidden bg-gray-900">
                            {result.videoUrl ? (
                                <video
                                    src={result.videoUrl}
                                    controls
                                    className="w-full h-full object-cover"
                                    poster={result.imageUrl} // Fallback to image
                                />
                            ) : (
                                <div className="flex items-center justify-center h-full text-gray-500">
                                    <Play className="w-12 h-12" />
                                </div>
                            )}
                            <div className="absolute bottom-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded-full">
                                AI Video
                            </div>
                        </div>
                        <p className="mt-2 text-sm text-center text-gray-500 italic">
                            "{result.prompts.videoPrompt}"
                        </p>
                    </motion.div>
                </div>

                {/* Right Column: Text */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-white"
                >
                    <div className="prose prose-lg prose-purple max-w-none">
                        {paragraphs.map((p, i) => (
                            <p key={i} className="mb-4 text-slate-700 leading-relaxed font-sans text-lg">
                                {p}
                            </p>
                        ))}
                    </div>
                </motion.div>
            </div>
        </motion.div>
    );
}
