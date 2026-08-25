/**
 * ErrorState component displays error messages with retry functionality
 */

'use client';

import { Button } from '@/components/ui/Button';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      {/* Error icon */}
      <div className="mb-6">
        <svg
          className="h-24 w-24 text-red-300"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
          />
        </svg>
      </div>

      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        Something went wrong
      </h3>

      <p className="text-gray-600 mb-6 max-w-md">
        {message || 'We encountered an error while searching. Please try again.'}
      </p>

      {onRetry && (
        <Button onClick={onRetry} size="md">
          Try Again
        </Button>
      )}
    </div>
  );
}