/**
 * SearchBar component with autocomplete support
 */

'use client';

import { useState, FormEvent } from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

interface SearchBarProps {
  initialValue?: string;
  initialPlatforms?: string;
  onSubmit?: (query: string, platforms?: string) => void;
  selectedPlatforms?: string[];
  onInputChange?: (query: string) => void;
}

export function SearchBar({
  initialValue = '',
  initialPlatforms = '',
  onSubmit,
  selectedPlatforms,
  onInputChange
}: SearchBarProps) {
  const [query, setQuery] = useState(initialValue);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (value: string) => {
    setQuery(value);
    setError(null);
    if (onInputChange) {
      onInputChange(value);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (query.trim().length < 2) {
      setError('Please enter at least 2 characters');
      return;
    }

    setError(null);

    const platforms = selectedPlatforms && selectedPlatforms.length > 0
      ? selectedPlatforms.join(',')
      : initialPlatforms;

    if (onSubmit) {
      onSubmit(query.trim(), platforms);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        {/* Search icon */}
        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
        </div>

        {/* Search input */}
        <Input
          type="text"
          variant="search"
          placeholder="Search for products (e.g., Milk, Bread, Rice...)"
          value={query}
          onChange={(e) => handleChange(e.target.value)}
          className="pr-28 bg-white/90 backdrop-blur-sm"
        />

        {/* Search button */}
        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center space-x-2">
          <Button
            type="submit"
            size="sm"
            className="shrink-0 shadow-lg"
          >
            Search
          </Button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="mt-2 text-sm text-red-600 flex items-center gap-1">
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </div>
      )}
    </form>
  );
}
