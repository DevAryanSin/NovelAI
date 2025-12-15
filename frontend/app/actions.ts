"use server";

export interface ProcessResult {
    simplifiedText: string;
    imagePrompt: string;
    image: string;
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

        return {
            simplifiedText: data.simplified_text,
            imagePrompt: data.image_prompt,
            image: data.image || "",
        };
    } catch (error) {
        console.error("Process Chapter Error:", error);
        throw error;
    }
}
