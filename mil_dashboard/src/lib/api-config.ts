/**
 * API Configuration
 * Points to deployed Render backend
 */

// Always use the deployed backend URL
export const API_BASE_URL = "https://military-hierarchy-backend.onrender.com";

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
