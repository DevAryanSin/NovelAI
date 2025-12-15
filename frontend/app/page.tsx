"use client";

import { useState } from "react";
import InputSection from "@/components/InputSection";
import StoryDisplay from "@/components/StoryDisplay";
import { processChapter, ProcessResult } from "@/app/actions";
import { BookOpen } from "lucide-react";

export default function Home() {
  const [result, setResult] = useState<ProcessResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState("");

  const handleProcess = async (text: string) => {
    setIsProcessing(true);
    setError("");
    try {
      const res = await processChapter(text);
      setResult(res);
    } catch (err) {
      console.error(err);
      setError("Something went wrong! Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError("");
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-[family-name:var(--font-geist-sans)] p-4 sm:p-8">
      <main className="max-w-6xl mx-auto flex flex-col items-center gap-12 pt-8">

        {/* Header */}
        <div className="text-center space-y-4">
          <div className="inline-block p-3 bg-white rounded-full shadow-sm mb-2">
            <BookOpen className="w-8 h-8 text-slate-700" />
          </div>
          <h1 className="text-4xl font-bold text-slate-800 tracking-tight">
            Story Illustrator
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Transform your stories into illustrated children's books
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="w-full max-w-lg bg-red-50 text-red-600 p-4 rounded-xl border border-red-200 text-center">
            {error}
          </div>
        )}

        {/* Content Area */}
        <div className="w-full transition-all duration-500">
          {!result ? (
            <InputSection onProcess={handleProcess} isProcessing={isProcessing} />
          ) : (
            <StoryDisplay result={result} onReset={handleReset} />
          )}
        </div>

      </main>

      {/* Footer */}
      <footer className="mt-20 text-center text-slate-400 text-sm pb-8">
        Powered by Google Gemini
      </footer>
    </div>
  );
}
