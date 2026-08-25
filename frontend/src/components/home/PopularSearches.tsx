/**
 * PopularSearches component displays trending search suggestions
 */

'use client';

import Link from 'next/link';

const POPULAR_SEARCHES = [
  'Milk',
  'Eggs',
  'Bread',
  'Rice',
  'Cooking Oil',
  'Coffee',
  'Butter',
  'Sugar',
  'Tea',
  'Fruits',
  'Vegetables',
  'Chicken',
];

interface PopularSearchesProps {
  selectedPlatforms?: string[];
}

export function PopularSearches({ selectedPlatforms = [] }: PopularSearchesProps) {
  const buildSearchUrl = (query: string) => {
    const url = `/search?q=${encodeURIComponent(query)}`;
    if (selectedPlatforms.length > 0) {
      return `${url}&platforms=${selectedPlatforms.join(',')}`;
    }
    return url;
  };

  return (
    <div className="bg-white border-t border-gray-200">
      <div className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
          Popular searches
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {POPULAR_SEARCHES.map((search) => {
            const href = buildSearchUrl(search);
            return (
              <Link
                key={search}
                href={href}
                className="group"
              >
                <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all">
                  <div className="flex items-center space-x-3">
                    {/* Search icon */}
                    <svg
                      className="h-5 w-5 text-gray-400 group-hover:text-blue-600 transition-colors"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
                      />
                    </svg>

                    {/* Search term */}
                    <span className="text-gray-700 group-hover:text-blue-600 font-medium transition-colors">
                      {search}
                    </span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
