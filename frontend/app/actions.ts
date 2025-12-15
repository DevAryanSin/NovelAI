"use server";

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
        const response = await fetch("http://localhost:8000/process_pdf", {
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
        const response = await fetch("http://localhost:8000/generate_images", {
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

export async function downloadBookPDF(book: ProcessedBook): Promise<void> {
    try {
        const response = await fetch("http://localhost:8000/download_pdf", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(book),
        });

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        // Get the blob from response
        const blob = await response.blob();

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${book.title.replace(/\s+/g, '_')}_Kids_Edition.pdf`;
        document.body.appendChild(a);
        a.click();

        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error("Download PDF Error:", error);
        throw error;
    }
}
