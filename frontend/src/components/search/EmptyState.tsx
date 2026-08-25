/**
 * EmptyState component displays when no search results are found
 */

'use client';

interface EmptyStateProps {
  query: string;
}

export function EmptyState({ query }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      {/* Empty state icon */}
      <div className="mb-6">
        <svg
          className="h-24 w-24 text-gray-300"
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
      </div>

      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        No results found
      </h3>

      <p className="text-gray-600 mb-6 max-w-md">
        We couldn't find any products matching "{query}". Try searching for
        something else or check your spelling.
      </p>

      <div className="text-sm text-gray-500">
        <p className="font-medium mb-2">Try searching for:</p>
        <div className="flex flex-wrap justify-center gap-2">
          {['Milk', 'Eggs', 'Bread', 'Rice', 'Oil', 'Coffee'].map((suggestion) => (
            <span
              key={suggestion}
              className="px-3 py-1 bg-gray-100 rounded-full text-gray-700"
            >
              {suggestion}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}