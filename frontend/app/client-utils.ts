// Client-side utility functions
import { ProcessedBook } from "./actions";
import { API_ENDPOINTS } from "@/lib/config";

export interface PDFProgress {
    currentChapter: number;
    totalChapters: number;
    status: string;
}

export async function downloadBookPDF(
    book: ProcessedBook,
    onProgress?: (progress: PDFProgress) => void
): Promise<void> {
    try {
        // Calculate how many chapters need images
        const chaptersNeedingImages = book.chapters.filter(ch => !ch.image).length;
        const totalChapters = book.chapters.length;

        // Notify start
        onProgress?.({
            currentChapter: 0,
            totalChapters: chaptersNeedingImages,
            status: `Preparing PDF... (${chaptersNeedingImages} images to generate)`
        });

        // Small delay to show initial status
        await new Promise(resolve => setTimeout(resolve, 500));

        // Estimate time: ~5 seconds per image + 2 seconds for PDF generation
        const estimatedTime = chaptersNeedingImages * 5 + 2;

        // Show progress updates
        let currentProgress = 0;
        const progressInterval = setInterval(() => {
            if (currentProgress < chaptersNeedingImages) {
                currentProgress++;
                onProgress?.({
                    currentChapter: currentProgress,
                    totalChapters: chaptersNeedingImages,
                    status: `Generating image ${currentProgress}/${chaptersNeedingImages}...`
                });
            }
        }, 5000); // Update every 5 seconds (approximate image generation time)

        const response = await fetch(API_ENDPOINTS.DOWNLOAD_PDF, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(book),
        });

        clearInterval(progressInterval);

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        // Final progress update
        onProgress?.({
            currentChapter: chaptersNeedingImages,
            totalChapters: chaptersNeedingImages,
            status: "Creating PDF..."
        });

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

        // Success
        onProgress?.({
            currentChapter: chaptersNeedingImages,
            totalChapters: chaptersNeedingImages,
            status: "Complete!"
        });
    } catch (error) {
        console.error("Download PDF Error:", error);
        throw error;
    }
}
