/**
 * TypeScript types matching the FastAPI backend schemas
 * These types correspond to the response formats from app/schemas/search.py
 */

/**
 * Location information from search request/response
 */
export interface Location {
  latitude: number;
  longitude: number;
}

/**
 * Platform offer information for a single platform
 */
export interface PlatformOffer {
  platform: string;
  price: number | null;
  mrp: number | null;
  discount: number | null;
  available: boolean;
  delivery_time_minutes: number | null;
  delivery_time_text: string | null;
  product_url: string | null;
  image_url: string | null;
}

/**
 * Comparison metrics for a product across platforms
 */
export interface ProductComparison {
  lowest_price: number | null;
  highest_price: number | null;
  price_difference: number | null;
  potential_savings: number | null;
  cheapest_platform: string | null;
  fastest_platform: string | null;
  fastest_delivery_time: number | null;
  best_overall_platform: string | null;
  best_overall_score: number | null;
  available_platforms: number;
  total_platforms: number;
}

/**
 * A single product in search results with all platform offers
 */
export interface ProductResult {
  name: string;
  brand: string | null;
  quantity: number | null;
  unit: string | null;
  quantity_display: string | null;
  image_url: string | null;
  comparison: ProductComparison;
  offers: PlatformOffer[];
}

/**
 * Complete search response from the API
 */
export interface SearchResponse {
  query: string;
  location: Location;
  platforms: string[];
  total_results: number;
  results: ProductResult[];
}

/**
 * Error response from the API
 */
export interface SearchErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

/**
 * Search parameters for the API request
 */
export interface SearchParams {
  query: string;
  latitude: number;
  longitude: number;
  platforms?: string[];
}

/**
 * Platform filter options
 */
export type PlatformFilter = 'BlinkIt' | 'Zepto' | 'Swiggy' | 'All';

/**
 * Sort options for search results
 */
export type SortOption = 'best_overall' | 'lowest_price' | 'fastest_delivery' | 'highest_discount';

/**
 * Frontend-specific product with additional computed properties
 */
export interface DisplayProduct extends ProductResult {
  id: string; // Computed ID for React keys
}