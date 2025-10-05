/**
 * API Configuration
 * Automatically uses the correct API URL for local development or production
 */

// For Next.js, environment variables must be prefixed with NEXT_PUBLIC_ to be available in the browser
// In production (Render), this will be set to the backend URL
// In local development, defaults to localhost:8000
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * API endpoint helper
 * @param path - API endpoint path (e.g., "/hierarchy")
 * @returns Full API URL
 */
export function getApiUrl(path: string): string {
  // Ensure path starts with /
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

// Export commonly used endpoints
export const API_ENDPOINTS = {
  hierarchy: getApiUrl("/hierarchy"),
  soldiers: getApiUrl("/soldiers"),
  reports: getApiUrl("/reports"),
  aiChat: getApiUrl("/ai/chat"),
  suggestions: getApiUrl("/api/suggestions"),
  casevacSuggest: getApiUrl("/casevac/suggest"),
  casevacGenerate: getApiUrl("/casevac/generate"),
  eoincrepSuggest: getApiUrl("/eoincrep/suggest"),
  eoincrepGenerate: getApiUrl("/eoincrep/generate"),
} as const;
