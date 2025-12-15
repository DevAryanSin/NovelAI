"use server";

import { simplifyText, generatePrompts, generateImage, generateVideo } from "@/lib/gemini";

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
    // 1. Simplify text
    const simplifiedText = await simplifyText(text);

    // 2. Extract prompts
    const prompts = await generatePrompts(simplifiedText);

    // 3. Generate Media (Parallel)
    const [imageUrl, videoUrl] = await Promise.all([
        generateImage(prompts.imagePrompt),
        generateVideo(prompts.videoPrompt),
    ]);

    return {
        originalText: text,
        simplifiedText,
        prompts,
        imageUrl: imageUrl || "",
        videoUrl: videoUrl || "",
    };
}
