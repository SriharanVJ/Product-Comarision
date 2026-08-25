/**
 * Hero component with eye-friendly animated background and floating products
 */

'use client';

import { useCallback, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { SearchBar } from '@/components/layout/SearchBar';
import { PlatformSelector } from '@/components/search/PlatformSelector';

interface HeroProps {
  selectedPlatforms: string[];
  onPlatformChange: (platforms: string[]) => void;
}

// Soft floating products with gentle animations
const FLOATING_PRODUCTS = [
  { icon: '🥛', size: 45, delay: 0, duration: 18, x: '8%', y: '15%' },
  { icon: '🍞', size: 40, delay: 1, duration: 20, x: '88%', y: '12%' },
  { icon: '🥑', size: 48, delay: 2, duration: 22, x: '78%', y: '72%' },
  { icon: '🍎', size: 42, delay: 3, duration: 19, x: '12%', y: '78%' },
  { icon: '🥕', size: 44, delay: 4, duration: 21, x: '92%', y: '42%' },
  { icon: '🍌', size: 45, delay: 5, duration: 23, x: '6%', y: '48%' },
  { icon: '🧀', size: 38, delay: 6, duration: 18, x: '58%', y: '88%' },
  { icon: '🥬', size: 40, delay: 7, duration: 20, x: '22%', y: '8%' },
  { icon: '🍊', size: 45, delay: 8, duration: 22, x: '72%', y: '22%' },
  { icon: '🥚', size: 36, delay: 9, duration: 19, x: '38%', y: '82%' },
  { icon: '🍇', size: 42, delay: 10, duration: 24, x: '82%', y: '8%' },
  { icon: '🥒', size: 44, delay: 11, duration: 21, x: '10%', y: '32%' },
  { icon: '🍓', size: 40, delay: 12, duration: 23, x: '90%', y: '62%' },
  { icon: '🍯', size: 46, delay: 13, duration: 18, x: '28%', y: '6%' },
  { icon: '🥜', size: 42, delay: 14, duration: 20, x: '62%', y: '52%' },
];

// Popular products for autocomplete suggestions
const POPULAR_PRODUCTS = [
  'Milk', 'Eggs', 'Bread', 'Rice', 'Cooking Oil',
  'Coffee', 'Butter', 'Sugar', 'Tea', 'Fruits',
  'Vegetables', 'Chicken', 'Cheese', 'Yogurt',
  'Juice', 'Cereal', 'Pasta', 'Flour', 'Honey',
  'Jam', 'Chips', 'Chocolate', 'Ice Cream',
  'Tomatoes', 'Onions', 'Potatoes', 'Banana',
  'Apple', 'Orange', 'Mango', 'Grapes'
];

export function Hero({ selectedPlatforms, onPlatformChange }: HeroProps) {
  const router = useRouter();
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleSearch = useCallback((query: string) => {
    if (selectedPlatforms.length === 0) {
      alert('Please select at least one platform');
      return;
    }

    const platforms = selectedPlatforms.join(',');
    const url = `/search?q=${encodeURIComponent(query)}&platforms=${platforms}`;
    router.push(url);
    setShowSuggestions(false);
  }, [selectedPlatforms, router]);

  const handleInputChange = (query: string) => {
    if (query.length >= 1) {
      const filtered = POPULAR_PRODUCTS.filter(product =>
        product.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 8); // Show max 8 suggestions
      setSuggestions(filtered);
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setSuggestions([]);
    setShowSuggestions(false);
    handleSearch(suggestion);
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setShowSuggestions(false);
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  return (
    <div className="relative min-h-[700px] lg:min-h-[800px] flex items-center justify-center overflow-hidden">
      {/* Eye-friendly soft gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50 to-emerald-50">
        {/* Soft animated overlay */}
        <div className="absolute inset-0 opacity-40">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-100/30 via-teal-100/30 to-emerald-100/30 animate-gradient-shift" />
        </div>

        {/* Soft pulsing orbs */}
        <div className="absolute top-20 left-10 w-80 h-80 bg-blue-200/20 rounded-full blur-3xl animate-pulse-soft" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-teal-200/20 rounded-full blur-3xl animate-pulse-soft-delayed" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-emerald-100/20 rounded-full blur-3xl animate-pulse-soft-slow" />
      </div>

      {/* Floating product icons */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {FLOATING_PRODUCTS.map((product, index) => (
          <div
            key={index}
            className="absolute animate-float opacity-30"
            style={{
              fontSize: `${product.size}px`,
              left: product.x,
              top: product.y,
              animationDelay: `${product.delay}s`,
              animationDuration: `${product.duration}s`,
            }}
          >
            {product.icon}
          </div>
        ))}
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto px-4 py-16 sm:px-6 lg:px-8 text-center">
        {/* Animated badge */}
        <div className="animate-fade-in-down mb-8" style={{ animationDelay: '0ms' }}>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/60 backdrop-blur-sm shadow-lg border border-gray-100">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <span className="text-sm font-medium text-gray-700">Live price comparison</span>
          </div>
        </div>

        {/* Main headline */}
        <h1 className="animate-fade-in-up mb-4" style={{ animationDelay: '100ms' }}>
          <span className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-800 tracking-tight">
            Compare prices
          </span>
          <div className="mt-4 relative inline-block">
            <span className="text-5xl sm:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent tracking-tight">
              across platforms
            </span>
          </div>
        </h1>

        {/* Subtitle */}
        <p
          className="animate-fade-in-up text-lg sm:text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed"
          style={{ animationDelay: '200ms' }}
        >
          Search once and compare prices, availability, and delivery times across
          <span className="font-semibold text-gray-700"> all your favorite platforms</span> — instantly.
        </p>

        {/* Platform selector */}
        <div
          className="animate-fade-in-up max-w-2xl mx-auto mb-6 relative"
          style={{ animationDelay: '300ms' }}
        >
          <PlatformSelector
            selectedPlatforms={selectedPlatforms}
            onPlatformChange={onPlatformChange}
          />
        </div>

        {/* Search bar with autocomplete */}
        <div
          className="animate-fade-in-up max-w-2xl mx-auto mb-10 relative"
          style={{ animationDelay: '400ms' }}
        >
          <SearchBar
            onSubmit={handleSearch}
            selectedPlatforms={selectedPlatforms}
            onInputChange={handleInputChange}
          />

          {/* Autocomplete dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50 animate-fade-in-up">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-4 py-3 text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-3"
                >
                  <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                  </svg>
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Trust indicators */}
        <div
          className="animate-fade-in-up flex flex-wrap justify-center items-center gap-8"
          style={{ animationDelay: '500ms' }}
        >
          {[
            { icon: '⚡', text: 'Real-time prices', color: 'text-yellow-600' },
            { icon: '🔗', text: 'Multiple platforms', color: 'text-blue-600' },
            { icon: '💰', text: 'Save money', color: 'text-emerald-600' },
          ].map((item, index) => (
            <div
              key={index}
              className="group flex flex-col items-center space-y-1"
            >
              <span className={`text-3xl transform group-hover:scale-110 transition-transform duration-300 ${item.color}`}>
                {item.icon}
              </span>
              <span className="font-medium text-gray-700">{item.text}</span>
            </div>
          ))}
        </div>

        {/* Scroll indicator */}
        <div
          className="animate-bounce-slow mt-16"
          style={{ animationDelay: '1000ms' }}
        >
          <div className="flex flex-col items-center gap-2 text-gray-400">
            <span className="text-sm font-medium">Scroll to explore</span>
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>

      {/* Bottom fade gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-white to-transparent" />
    </div>
  );
}
