/**
 * Utility function to merge Tailwind CSS classes
 * Uses clsx and tailwind-merge for optimal class handling
 */
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { ProductResult, PlatformOffer, ProductComparison } from '@/types/api';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format price in Indian Rupees
 */
export function formatPrice(price: number | null): string {
  if (price === null) return 'N/A';
  return `₹${price.toFixed(0)}`;
}

/**
 * Format delivery time for display
 */
export function formatDeliveryTime(minutes: number | null, text: string | null): string {
  if (text) return text;
  if (minutes === null) return 'N/A';
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
}

/**
 * Generate a stable ID for a product
 */
export function generateProductId(product: ProductResult): string {
  const base = `${product.name}-${product.brand || 'unknown'}-${product.quantity || 0}-${product.unit || 'unit'}`;
  return base.toLowerCase().replace(/[^a-z0-9]+/g, '-');
}

/**
 * Check if a platform is the cheapest
 */
export function isCheapestPlatform(offer: PlatformOffer, comparison: ProductComparison): boolean {
  return comparison.cheapest_platform === offer.platform;
}

/**
 * Check if a platform is the fastest
 */
export function isFastestPlatform(offer: PlatformOffer, comparison: ProductComparison): boolean {
  return comparison.fastest_platform === offer.platform;
}

/**
 * Check if a platform is the best overall
 */
export function isBestOverallPlatform(offer: PlatformOffer, comparison: ProductComparison): boolean {
  return comparison.best_overall_platform === offer.platform;
}

/**
 * Get platform color class
 */
export function getPlatformColor(platform: string): string {
  const colors: Record<string, string> = {
    'BlinkIt': 'text-yellow-600',
    'Zepto': 'text-green-600',
    'Swiggy': 'text-orange-600',
  };
  return colors[platform] || 'text-gray-600';
}

/**
 * Get platform background color class
 */
export function getPlatformBgColor(platform: string): string {
  const colors: Record<string, string> = {
    'BlinkIt': 'bg-yellow-50 border-yellow-200',
    'Zepto': 'bg-green-50 border-green-200',
    'Swiggy': 'bg-orange-50 border-orange-200',
  };
  return colors[platform] || 'bg-gray-50 border-gray-200';
}