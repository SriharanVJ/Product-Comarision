/**
 * Homepage for QuickCompare application
 */

'use client';

import { useState } from 'react';
import { Hero } from '@/components/home/Hero';
import { PopularSearches } from '@/components/home/PopularSearches';

export default function Home() {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);

  return (
    <div className="flex flex-col">
      <Hero
        selectedPlatforms={selectedPlatforms}
        onPlatformChange={setSelectedPlatforms}
      />
      <PopularSearches selectedPlatforms={selectedPlatforms} />
    </div>
  );
}
