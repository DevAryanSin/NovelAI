"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, RotateCcw, Loader2 } from "lucide-react";
import { ProcessedBook, generateChapterImages } from "@/app/actions";

interface BookDisplayProps {
    book: ProcessedBook;
    onReset: () => void;
}

export default function BookDisplay({ book, onReset }: BookDisplayProps) {
    const [currentChapter, setCurrentChapter] = useState(0);
    const [direction, setDirection] = useState(0);
    const [loadingImages, setLoadingImages] = useState<{ [key: number]: boolean }>({});
    const [chapterImages, setChapterImages] = useState<{ [key: number]: { image: string; image_prompt: string } }>({});

    const totalChapters = book.chapters.length;

    const getCurrentChapter = () => {
        return book.chapters[currentChapter];
    };

    const getCurrentImage = () => {
        const chapter = getCurrentChapter();
        const images = chapterImages[currentChapter];

        if (images) {
            return images.image;
        }
        return chapter.image;
    };

    const getCurrentImagePrompt = () => {
        const images = chapterImages[currentChapter];

        if (images) {
            return images.image_prompt;
        }
        return "";
    };

    // Load image for current chapter when chapter changes
    useEffect(() => {
        const chapter = getCurrentChapter();

        // Check if image is already loaded or being loaded
        if (!chapterImages[currentChapter] && !loadingImages[currentChapter] && !chapter.image) {
            loadImageForChapter(currentChapter);
        }
    }, [currentChapter]);

    const loadImageForChapter = async (chapterIndex: number) => {
        const chapter = book.chapters[chapterIndex];

        setLoadingImages(prev => ({ ...prev, [chapterIndex]: true }));

        try {
            const images = await generateChapterImages(chapter.chapter_number, chapter.simplified_text);
            setChapterImages(prev => ({
                ...prev,
                [chapterIndex]: images
            }));
        } catch (error) {
            console.error(`Failed to load image for chapter ${chapter.chapter_number}:`, error);
        } finally {
            setLoadingImages(prev => ({ ...prev, [chapterIndex]: false }));
        }
    };

    const nextChapter = () => {
        if (currentChapter < totalChapters - 1) {
            setDirection(1);
            setCurrentChapter(currentChapter + 1);
        }
    };

    const prevChapter = () => {
        if (currentChapter > 0) {
            setDirection(-1);
            setCurrentChapter(currentChapter - 1);
        }
    };

    const pageVariants = {
        enter: (direction: number) => ({
            x: direction > 0 ? 300 : -300,
            opacity: 0,
        }),
        center: {
            x: 0,
            opacity: 1,
        },
        exit: (direction: number) => ({
            x: direction > 0 ? -300 : 300,
            opacity: 0,
        }),
    };

    const chapter = getCurrentChapter();
    const isLoadingCurrentChapter = loadingImages[currentChapter];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-6xl mx-auto"
        >
            {/* Header with Reset Button */}
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-bold text-slate-800">{book.title}</h2>
                <button
                    onClick={onReset}
                    className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-slate-50 text-slate-700 rounded-lg border border-slate-200 transition-colors"
                >
                    <RotateCcw className="w-4 h-4" />
                    New Book
                </button>
            </div>

            {/* Book Layout: Text Left, Image Right */}
            <AnimatePresence initial={false} custom={direction} mode="wait">
                <motion.div
                    key={currentChapter}
                    custom={direction}
                    variants={pageVariants}
                    initial="enter"
                    animate="center"
                    exit="exit"
                    transition={{
                        x: { type: "spring", stiffness: 300, damping: 30 },
                        opacity: { duration: 0.2 },
                    }}
                    className="grid md:grid-cols-2 gap-8 bg-white rounded-2xl shadow-lg overflow-hidden border border-slate-200"
                >
                    {/* Left Side: Text Content */}
                    <div className="p-8 md:p-12 overflow-y-auto max-h-[600px]">
                        <h3 className="text-xl font-semibold text-slate-800 mb-4">
                            Chapter {chapter.chapter_number}: {chapter.title}
                        </h3>
                        <div className="prose prose-slate max-w-none">
                            {chapter.simplified_text.split('\n').filter((p: string) => p.trim()).map((paragraph: string, i: number) => (
                                <p key={i} className="mb-4 text-slate-700 leading-relaxed text-base">
                                    {paragraph}
                                </p>
                            ))}
                        </div>
                        <div className="mt-6 pt-4 border-t border-slate-200 text-sm text-slate-400">
                            Chapter {currentChapter + 1} of {totalChapters}
                        </div>
                    </div>

                    {/* Right Side: Generated Image */}
                    <div className="relative bg-slate-50 flex items-center justify-center p-8">
                        {isLoadingCurrentChapter ? (
                            <div className="text-slate-600 text-center">
                                <Loader2 className="w-12 h-12 mx-auto mb-4 animate-spin" />
                                <p className="text-sm">Generating illustration...</p>
                            </div>
                        ) : getCurrentImage() ? (
                            <div className="w-full flex flex-col">
                                <img
                                    src={getCurrentImage()}
                                    alt={getCurrentImagePrompt() || `Chapter ${chapter.chapter_number} illustration`}
                                    className="w-full h-auto max-h-[500px] object-contain rounded-lg shadow-md"
                                />
                                {getCurrentImagePrompt() && (
                                    <p className="mt-4 text-sm text-slate-500 italic text-center">
                                        "{getCurrentImagePrompt()}"
                                    </p>
                                )}
                            </div>
                        ) : (
                            <div className="text-slate-400 text-center">
                                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-200 flex items-center justify-center">
                                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <p>No image available</p>
                            </div>
                        )}
                    </div>
                </motion.div>
            </AnimatePresence>

            {/* Navigation Controls */}
            <div className="flex items-center justify-center gap-4 mt-8">
                <button
                    onClick={prevChapter}
                    disabled={currentChapter === 0}
                    className="p-2 bg-white hover:bg-slate-50 text-slate-700 rounded-lg border border-slate-200 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                >
                    <ChevronLeft className="w-6 h-6" />
                </button>

                <span className="text-sm text-slate-600 font-medium min-w-[100px] text-center">
                    {currentChapter + 1} / {totalChapters}
                </span>

                <button
                    onClick={nextChapter}
                    disabled={currentChapter === totalChapters - 1}
                    className="p-2 bg-white hover:bg-slate-50 text-slate-700 rounded-lg border border-slate-200 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                >
                    <ChevronRight className="w-6 h-6" />
                </button>
            </div>

            {/* Chapter Quick Navigation */}
            <div className="mt-6 flex gap-2 justify-center flex-wrap">
                {book.chapters.map((ch, idx) => (
                    <button
                        key={idx}
                        onClick={() => {
                            setDirection(idx > currentChapter ? 1 : -1);
                            setCurrentChapter(idx);
                        }}
                        className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${currentChapter === idx
                                ? "bg-slate-800 text-white"
                                : "bg-white text-slate-700 hover:bg-slate-50 border border-slate-200"
                            }`}
                    >
                        Ch. {ch.chapter_number}
                    </button>
                ))}
            </div>
        </motion.div>
    );
}
