/**
 * Custom React hook for search functionality
 * Manages search state, API calls, and error handling
 */

'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { searchProducts, APIError } from '@/services/api';
import type { SearchResponse, SearchParams } from '@/types/api';

interface UseSearchResult {
  query: string;
  results: SearchResponse | null;
  loading: boolean;
  error: string | null;
  search: (query: string, platforms: string) => Promise<void>;
  clearError: () => void;
}

const DEFAULT_LATITUDE = 13.0827;
const DEFAULT_LONGITUDE = 80.2707;

/**
 * Custom hook for managing product search functionality
 * @returns Search state and search function
 */
export function useSearch(): UseSearchResult {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState<string>('');

  // Track the last search key to prevent duplicate API calls
  const lastSearchKeyRef = useRef<string | null>(null);

  /**
   * Manual search function - ONLY updates URL, lets useEffect handle the API call
   */
  const search = useCallback(async (searchQuery: string, platforms: string) => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setError('Please enter at least 2 characters');
      return;
    }

    if (!platforms || platforms.split(',').filter(Boolean).length === 0) {
      setError('Please select at least one platform');
      return;
    }

    // Only update the URL - useEffect will handle the API call
    const urlParams = new URLSearchParams({
      q: searchQuery.trim(),
      platforms: platforms,
    });
    router.push(`/search?${urlParams.toString()}`, { scroll: false });
  }, [router]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // SINGLE source of API calls - only useEffect triggers the API
  useEffect(() => {
    const urlQuery = searchParams.get('q');
    const urlPlatforms = searchParams.get('platforms');

    // Clear results if no search params
    if (!urlQuery || !urlPlatforms || urlQuery.trim().length < 2) {
      setResults(null);
      setQuery('');
      lastSearchKeyRef.current = null;
      return;
    }

    const platformList = urlPlatforms.split(',').filter(Boolean);
    if (platformList.length === 0) {
      return;
    }

    const searchKey = `${urlQuery.trim()}:${urlPlatforms}`;

    // Prevent duplicate calls for the same search
    if (lastSearchKeyRef.current === searchKey) {
      console.log('useSearch: Skipping duplicate API call for:', searchKey);
      return;
    }

    console.log('useSearch: Making API call for:', searchKey);
    lastSearchKeyRef.current = searchKey;
    setLoading(true);
    setError(null);

    searchProducts({
      query: urlQuery.trim(),
      latitude: DEFAULT_LATITUDE,
      longitude: DEFAULT_LONGITUDE,
      platforms: platformList,
    })
      .then((response) => {
        console.log('useSearch: API call successful for:', searchKey, 'results:', response?.results?.length || 0);
        setResults(response);
        setQuery(urlQuery.trim());
      })
      .catch((err) => {
        console.error('useSearch: API call failed for:', searchKey, err);
        if (err instanceof APIError) {
          setError(err.message);
        } else {
          setError('An unexpected error occurred. Please try again.');
        }
        setResults(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [searchParams]);

  return {
    query,
    results,
    loading,
    error,
    search,
    clearError,
  };
}
