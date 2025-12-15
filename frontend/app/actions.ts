"use server";

export interface ProcessResult {
    originalText: string;
    simplifiedText: string;
    prompts: {
        imagePrompt: string;
        videoPrompt: string;
    };
    imageUrl: string;
    videoUrl: string;
}

export async function processChapter(text: string): Promise<ProcessResult> {
    try {
        const response = await fetch("http://localhost:8000/process_chapter", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ text }),
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Map backend snake_case to frontend camelCase if needed
        // Our backend currently returns mixed, let's normalize in backend or here
        return {
            originalText: data.original_text,
            simplifiedText: data.simplified_text,
            prompts: data.prompts,
            imageUrl: data.imageUrl || "",
            videoUrl: data.videoUrl || "",
        };
    } catch (error) {
        console.error("Process Chapter Error:", error);
        throw error;
    }
}
