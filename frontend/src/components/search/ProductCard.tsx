/**
 * ProductCard component displays a product with all platform offers and comparison metrics
 */

'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { PlatformOffer } from './PlatformOffer';
import { cn, formatPrice, generateProductId } from '@/utils/cn';
import type { ProductResult } from '@/types/api';

interface ProductCardProps {
  product: ProductResult;
}

export function ProductCard({ product }: ProductCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const hasMultipleOffers = product.offers.length > 1;
  const availableOffers = product.offers.filter(o => o.available);
  const potentialSavings = product.comparison.potential_savings;
  const [imageError, setImageError] = useState(false);

  return (
    <Card variant="outlined" className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start space-x-4">
          {/* Product image placeholder */}
          <div className="flex-shrink-0 h-20 w-20 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
            {product.image_url && !imageError ? (
              <img
                src={product.image_url}
                alt={product.name}
                className="h-20 w-20 object-cover rounded-lg"
                onError={() => setImageError(true)}
                loading="lazy"
              />
            ) : (
              <div className="flex flex-col items-center justify-center p-2 text-center">
                <svg className="h-8 w-8 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                </svg>
                <span className="text-xs text-gray-400 mt-1">No image</span>
              </div>
            )}
          </div>

          {/* Product info */}
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {product.name}
            </h3>

            {/* Brand and quantity */}
            <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600 mb-2">
              {product.brand && (
                <span className="font-medium">{product.brand}</span>
              )}
              {product.quantity_display && (
                <>
                  <span>•</span>
                  <span>{product.quantity_display}</span>
                </>
              )}
              {!product.quantity_display && product.quantity && product.unit && (
                <>
                  <span>•</span>
                  <span>{product.quantity} {product.unit}</span>
                </>
              )}
              {!product.quantity_display && !product.quantity && (
                <>
                  <span>•</span>
                  <span className="text-gray-500 italic">Quantity unavailable</span>
                </>
              )}
              {product.comparison.available_platforms > 0 && (
                <>
                  <span>•</span>
                  <span className="text-green-600">
                    {product.comparison.available_platforms} platform{product.comparison.available_platforms !== 1 ? 's' : ''} available
                  </span>
                </>
              )}
            </div>

            {/* Savings highlight */}
            {potentialSavings && potentialSavings > 0 && (
              <div className="flex items-center space-x-2 text-sm">
                <Badge variant="success" size="sm">
                  You save {formatPrice(potentialSavings)}
                </Badge>
              </div>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Platform offers */}
        <div className="space-y-3">
          {product.offers.slice(0, isExpanded ? undefined : 2).map((offer) => (
            <PlatformOffer
              key={`${product.name}-${offer.platform}`}
              offer={offer}
              comparison={product.comparison}
            />
          ))}
        </div>

        {/* Expand/Collapse button */}
        {hasMultipleOffers && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-full"
            >
              {isExpanded ? (
                <>
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
                  </svg>
                  Show less
                </>
              ) : (
                <>
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                  </svg>
                  Compare all {product.offers.length} platforms
                </>
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}