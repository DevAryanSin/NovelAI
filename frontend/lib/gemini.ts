// import { GoogleGenerativeAI } from "@google/generative-ai";

// const apiKeyTextImage = process.env.GEMINI_API_KEY_TEXT_IMAGE || "";
// const apiKeyVideo = process.env.GEMINI_API_KEY_VIDEO || "";

// const genAITextImage = new GoogleGenerativeAI(apiKeyTextImage);
// const genAIVideo = new GoogleGenerativeAI(apiKeyVideo);

// export async function simplifyText(text: string): Promise<string> {
//     if (!apiKeyTextImage) return "Error: Missing GEMINI_API_KEY_TEXT_IMAGE";

//     try {
//         const model = genAITextImage.getGenerativeModel({ model: "gemini-2.5-flash" });
//         const prompt = `Simplify the following novel chapter for a young child (age 6-8). Make it engaging, easy to read, and split into small paragraphs. Keep the core story intact but remove complex language and dark themes. Return only the story text. Text: ${text}`;

//         const result = await model.generateContent(prompt);
//         return result.response.text();
//     } catch (error) {
//         console.error("Simplify Text Error:", error);
//         return "Failed to simplify text.";
//     }
// }

// export async function generatePrompts(text: string): Promise<{ imagePrompt: string, videoPrompt: string }> {
//     if (!apiKeyTextImage) return { imagePrompt: "A cute story illustration", videoPrompt: "Fun animation for kids" };

//     try {
//         const model = genAITextImage.getGenerativeModel({ model: "gemini-2.5-flash" });
//         const prompt = `Read the following simplified story and extract a short, vivid description for ONE illustration and ONE short video concept suitable for kids. Return strictly JSON in this format: { "imagePrompt": "...", "videoPrompt": "..." }. Story: ${text}`;

//         const result = await model.generateContent(prompt);
//         const textResponse = result.response.text();

//         const jsonStr = textResponse.replace(/```json/g, '').replace(/```/g, '').trim();
//         return JSON.parse(jsonStr);
//     } catch (error) {
//         console.error("Generate Prompts Error:", error);
//         return { imagePrompt: "A magical scene from the story", videoPrompt: "A character walking in a magical land" };
//     }
// }

// // TODO: Implement actual Imagen API call. Currently SDK support varies.
// // This is a placeholder that simulates the call.
// export async function generateImage(prompt: string): Promise<string> {
//     if (!apiKeyTextImage) return "https://placehold.co/800x600?text=No+API+Key";

//     console.log("Generating Image with prompt:", prompt);
//     // In a real implementation with valid Imagen access:
//     // const model = genAITextImage.getGenerativeModel({ model: "imagen-3.0-generate-001" });
//     // const result = await model.generateContent(prompt);
//     // Handle result...

//     return "https://placehold.co/800x600?text=AI+Illustration+Placeholder";
// }

// // TODO: Implement actual Veo API call.
// export async function generateVideo(prompt: string): Promise<string> {
//     if (!apiKeyVideo) return "https://placehold.co/800x600?text=No+Video+Key";

//     console.log("Generating Video with prompt:", prompt);
//     // const model = genAIVideo.getGenerativeModel({ model: "veo-2.0-generate-001-preview" });
//     // const result = await model.generateContent(prompt);

//     return "https://placehold.co/800x600?text=AI+Video+Placeholder";
// }
