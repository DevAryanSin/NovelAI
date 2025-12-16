"use server";

import { API_ENDPOINTS } from "@/lib/config";

export interface ProcessResult {
    simplifiedText: string;
    imagePrompt: string;
    image: string;
}

export interface Chapter {
    chapter_number: number;
    title: string;
    simplified_text: string;
    image: string;
    image_prompt: string;
}

export interface ProcessedBook {
    title: string;
    total_chapters: number;
    chapters: Chapter[];
}

export async function processPDF(formData: FormData): Promise<ProcessedBook> {
    try {
        const response = await fetch(API_ENDPOINTS.PROCESS_PDF, {
            method: "POST",
            body: formData,
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        return data;
    } catch (error) {
        console.error("Process PDF Error:", error);
        throw error;
    }
}

export async function generateChapterImages(chapterNumber: number, simplifiedText: string) {
    try {
        const response = await fetch(API_ENDPOINTS.GENERATE_IMAGES, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                chapter_number: chapterNumber,
                simplified_text: simplifiedText,
            }),
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Generate Images Error:", error);
        throw error;
    }
}
