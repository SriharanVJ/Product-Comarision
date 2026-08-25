/**
 * Reusable Input component with variants and sizes
 */

import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/utils/cn';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  variant?: 'default' | 'search';
  error?: string;
}

const variantStyles: Record<string, string> = {
  default: 'border-gray-300 focus:ring-blue-500 focus:border-blue-500',
  search: 'border-gray-300 focus:ring-blue-500 focus:border-blue-500 pl-12',
};

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, variant = 'default', error, ...props }, ref) => {
    return (
      <div className="relative">
        <input
          ref={ref}
          className={cn(
            'block w-full rounded-lg border px-4 py-3 text-gray-900 placeholder-gray-500',
            'focus:outline-none focus:ring-2 focus:ring-offset-2',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            variantStyles[variant],
            error && 'border-red-500 focus:ring-red-500 focus:border-red-500',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';