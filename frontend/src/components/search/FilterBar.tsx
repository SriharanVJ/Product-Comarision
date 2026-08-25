/**
 * FilterBar component for filtering search results by platform and availability
 */

'use client';

import { useState } from 'react';
import { cn } from '@/utils/cn';

interface FilterBarProps {
  platforms: string[];
  onPlatformFilterChange?: (platforms: string[]) => void;
  onAvailabilityChange?: (availableOnly: boolean) => void;
}

const PLATFORM_COLORS: Record<string, string> = {
  'BlinkIt': 'bg-yellow-50 border-yellow-200 text-yellow-800',
  'Zepto': 'bg-purple-50 border-purple-200 text-purple-800',
  'Swiggy': 'bg-green-50 border-green-200 text-green-800',
};

export function FilterBar({
  platforms,
  onPlatformFilterChange,
  onAvailabilityChange,
}: FilterBarProps) {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [availableOnly, setAvailableOnly] = useState(false);

  const handlePlatformToggle = (platform: string) => {
    const newSelection = selectedPlatforms.includes(platform)
      ? selectedPlatforms.filter(p => p !== platform)
      : [...selectedPlatforms, platform];

    setSelectedPlatforms(newSelection);
    onPlatformFilterChange?.(newSelection);
  };

  const handleAvailabilityToggle = () => {
    const newValue = !availableOnly;
    setAvailableOnly(newValue);
    onAvailabilityChange?.(newValue);
  };

  if (platforms.length === 0) {
    return null;
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
      {/* Platform filters */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Platforms</h3>
        <div className="flex flex-wrap gap-2">
          {platforms.map((platform) => (
            <button
              key={platform}
              onClick={() => handlePlatformToggle(platform)}
              className={cn(
                'px-3 py-1.5 rounded-md border text-sm font-medium transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-500',
                selectedPlatforms.includes(platform)
                  ? PLATFORM_COLORS[platform] || 'bg-blue-50 border-blue-200 text-blue-800'
                  : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
              )}
            >
              {platform}
            </button>
          ))}
        </div>
      </div>

      {/* Availability filter */}
      <div className="flex items-center">
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={availableOnly}
            onChange={handleAvailabilityToggle}
            className="h-4 w-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          />
          <span className="text-sm text-gray-700">Available only</span>
        </label>
      </div>
    </div>
  );
}