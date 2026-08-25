/**
 * PlatformSelector component for selecting platforms to search
 */

'use client';

import { useState } from 'react';

export interface PlatformSelectorProps {
  selectedPlatforms: string[];
  onPlatformChange: (platforms: string[]) => void;
  disabled?: boolean;
}

const PLATFORMS = [
  { id: 'blinkit', name: 'BlinkIt', color: 'bg-yellow-500' },
  { id: 'zepto', name: 'Zepto', color: 'bg-purple-500' },
  { id: 'swiggy', name: 'Swiggy', color: 'bg-orange-500' },
];

export function PlatformSelector({
  selectedPlatforms,
  onPlatformChange,
  disabled = false
}: PlatformSelectorProps) {
  const togglePlatform = (platformName: string) => {
    console.log('Toggle platform:', platformName, 'Current:', selectedPlatforms);
    if (selectedPlatforms.includes(platformName)) {
      onPlatformChange(selectedPlatforms.filter(p => p !== platformName));
    } else {
      onPlatformChange([...selectedPlatforms, platformName]);
    }
  };

  return (
    <div className="flex flex-col sm:flex-row gap-3 mb-4">
      <span className="text-sm font-medium text-gray-700 self-center">
        Select platforms:
      </span>
      <div className="flex flex-wrap gap-2">
        {PLATFORMS.map((platform) => {
          const isSelected = selectedPlatforms.includes(platform.name);

          return (
            <button
              key={platform.id}
              type="button"
              onClick={() => togglePlatform(platform.name)}
              disabled={disabled}
              className={`
                px-4 py-2 rounded-lg font-medium transition-all duration-200
                ${isSelected
                  ? `${platform.color} text-white shadow-md`
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
            >
              <div className="flex items-center gap-2">
                <span className={`w-4 h-4 rounded-full border-2 ${isSelected ? 'border-white' : 'border-gray-300'}`}>
                  {isSelected && (
                    <svg className="w-3 h-3 text-white ml-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </span>
                <span>{platform.name}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
