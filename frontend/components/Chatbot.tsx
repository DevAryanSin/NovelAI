"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, MessageCircle, Loader2 } from "lucide-react";
import { sendChatMessage, ProcessedBook } from "@/app/actions";

interface Message {
    role: "user" | "assistant";
    content: string;
}

interface ChatbotProps {
    book: ProcessedBook;
}

export default function Chatbot({ book }: ChatbotProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: "assistant",
            content: `Hi! Ask me anything about "${book.title}"! `,
        },
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput("");

        // user message
        setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
        setIsLoading(true);

        try {
            // Combine all chapter texts for context
            const bookContext = book.chapters
                .map((ch) => `Chapter ${ch.chapter_number}: ${ch.title}\n${ch.simplified_text || ch.raw_text}`)
                .join("\n\n");

            const response = await sendChatMessage(userMessage, bookContext, book.title);

            if (response.success) {
                setMessages((prev) => [
                    ...prev,
                    { role: "assistant", content: response.response },
                ]);
            } else {
                setMessages((prev) => [
                    ...prev,
                    {
                        role: "assistant",
                        content: "Sorry, I couldn't answer that. Please try again!",
                    },
                ]);
            }
        } catch (error) {
            console.error("Chat error:", error);
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: "Oops! Something went wrong. Please try again!",
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="w-full max-w-6xl mx-auto mt-12"
        >
            {/* Header */}
            <div className="flex items-center gap-3 mb-4">
                <MessageCircle className="w-5 h-5 text-slate-600" />
                <h3 className="text-lg font-semibold text-slate-800">Ask About the Story</h3>
            </div>

            {/* Chat  */}
            <div className="bg-white rounded-lg shadow-lg border border-slate-200 overflow-hidden">
                {/* Messages Area */}
                <div className="h-[400px] overflow-y-auto p-6 space-y-4 bg-slate-50">
                    <AnimatePresence>
                        {messages.map((message, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                transition={{ duration: 0.3 }}
                                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"
                                    }`}
                            >
                                <div
                                    className={`max-w-[80%] rounded-lg px-4 py-3 ${message.role === "user"
                                            ? "bg-slate-800 text-white"
                                            : "bg-white border border-slate-200 text-slate-700"
                                        }`}
                                >
                                    <span className="text-sm leading-relaxed">{message.content}</span>
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {/* Loading  */}
                    {isLoading && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex justify-start"
                        >
                            <div className="bg-white border border-slate-200 rounded-lg px-4 py-3">
                                <Loader2 className="w-4 h-4 animate-spin text-slate-600" />
                            </div>
                        </motion.div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 bg-white border-t border-slate-200">
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask a question..."
                            disabled={isLoading}
                            className="flex-1 px-4 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-400 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed text-slate-800 placeholder-slate-400"
                        />
                        <button
                            onClick={handleSend}
                            disabled={!input.trim() || isLoading}
                            className="px-4 py-2 bg-slate-800 text-white rounded-lg font-medium hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            <Send className="w-4 h-4" />
                            Send
                        </button>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
