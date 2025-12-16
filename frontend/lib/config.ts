/**
 * Application configuration
 * Centralized management of environment variables and API endpoints
 */

// Backend API URL - must be set via environment variable
// For local development: http://localhost:8000
// For production: https://your-backend-app.onrender.com
export const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// API Endpoints
export const API_ENDPOINTS = {
    PROCESS_PDF: `${BACKEND_URL}/process_pdf`,
    SIMPLIFY_CHAPTER: `${BACKEND_URL}/simplify_chapter`,
    GENERATE_IMAGES: `${BACKEND_URL}/generate_images`,
} as const;


// Validate required environment variables
if (!process.env.NEXT_PUBLIC_BACKEND_URL && process.env.NODE_ENV === 'production') {
    console.warn('Warning: NEXT_PUBLIC_BACKEND_URL is not set. Using default localhost URL.');
}
