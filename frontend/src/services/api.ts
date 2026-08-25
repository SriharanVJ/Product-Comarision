/**
 * API client service for communicating with the FastAPI backend
 * Handles all HTTP requests with proper error handling and type safety
 */

import type {
  SearchResponse,
  SearchErrorResponse,
  SearchParams,
} from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Custom error class for API errors
 */
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Perform a search request to the backend API
 * @param params - Search parameters including query, latitude, longitude, and optional platforms
 * @returns Promise with search results
 * @throws APIError for failed requests
 */
export async function searchProducts(params: SearchParams): Promise<SearchResponse> {
  const { query, latitude, longitude, platforms } = params;

  // Build URL with query parameters
  const url = new URL(`${API_BASE_URL}/api/v1/search`);
  url.searchParams.append('q', query);
  url.searchParams.append('latitude', latitude.toString());
  url.searchParams.append('longitude', longitude.toString());

  if (platforms && platforms.length > 0) {
    url.searchParams.append('platforms', platforms.join(','));
  }

  console.log('API call:', url.toString()); // Debug log

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      signal: controller.signal,
      cache: 'no-store',
    });

    clearTimeout(timeoutId);
    console.log('API response status:', response.status); // Debug log

    if (!response.ok) {
      // Try to parse error response
      let errorData: SearchErrorResponse | null = null;
      try {
        errorData = await response.json() as SearchErrorResponse;
      } catch {
        // If JSON parsing fails, use default error
      }

      throw new APIError(
        errorData?.message || 'Search request failed',
        response.status,
        errorData?.details
      );
    }

    const data = await response.json() as SearchResponse;
    console.log('API results count:', data.results?.length || 0); // Debug log
    return data;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    // Handle specific error types
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new APIError('Request timeout. Please try again.');
      }
      if (error.message.includes('fetch')) {
        throw new APIError('Unable to connect to backend. Please ensure the backend is running.');
      }
    }

    // Handle network errors or other exceptions
    throw new APIError(
      error instanceof Error ? error.message : 'Network error occurred',
      undefined,
      { originalError: error }
    );
  }
}

/**
 * Check backend API health
 * @returns Promise with health status
 */
export async function checkHealth(): Promise<{ status: string; service: string; version: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new APIError('Health check failed', response.status);
    }

    return await response.json() as { status: string; service: string; version: string };
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError('Network error during health check');
  }
}
