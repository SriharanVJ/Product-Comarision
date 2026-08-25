/**
 * PlatformOffer component displays individual platform offers within a product card
 */

'use client';

import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { cn, formatPrice, formatDeliveryTime, isCheapestPlatform, isFastestPlatform, isBestOverallPlatform, getPlatformBgColor } from '@/utils/cn';
import type { PlatformOffer as PlatformOfferType, ProductComparison } from '@/types/api';

interface PlatformOfferProps {
  offer: PlatformOfferType;
  comparison: ProductComparison;
}

export function PlatformOffer({ offer, comparison }: PlatformOfferProps) {
  const isCheapest = isCheapestPlatform(offer, comparison);
  const isFastest = isFastestPlatform(offer, comparison);
  const isBestOverall = isBestOverallPlatform(offer, comparison);

  if (!offer.available) {
    return (
      <div
        className={cn(
          'flex items-center justify-between rounded-lg border p-4 opacity-60',
          getPlatformBgColor(offer.platform)
        )}
      >
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-900">{offer.platform}</span>
            <Badge variant="warning" size="sm">Unavailable</Badge>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'flex items-center justify-between rounded-lg border p-4 transition-colors',
        getPlatformBgColor(offer.platform)
      )}
    >
      <div className="flex-1">
        {/* Platform name with badges */}
        <div className="flex items-center flex-wrap gap-2 mb-2">
          <span className="font-medium text-gray-900">{offer.platform}</span>
          {isBestOverall && (
            <Badge variant="best-overall" size="sm">
              ⭐ Best Overall
            </Badge>
          )}
          {isCheapest && (
            <Badge variant="best-price" size="sm">
              🏆 Best Price
            </Badge>
          )}
          {isFastest && (
            <Badge variant="fastest" size="sm">
              ⚡ Fastest
            </Badge>
          )}
        </div>

        {/* Price and delivery */}
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          {offer.price !== null && (
            <span className="font-semibold text-lg text-gray-900">
              {formatPrice(offer.price)}
            </span>
          )}
          {offer.delivery_time_text && (
            <span>• {offer.delivery_time_text}</span>
          )}
          {offer.mrp && offer.price && offer.mrp > offer.price && (
            <span className="text-gray-400 line-through">{formatPrice(offer.mrp)}</span>
          )}
        </div>
      </div>

      {/* Buy button */}
      {offer.product_url ? (
        <a
          href={offer.product_url}
          target="_blank"
          rel="noopener noreferrer"
          className={cn(
            'inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium',
            'bg-blue-600 text-white hover:bg-blue-700 transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
            'shrink-0 ml-4'
          )}
        >
          Buy on {offer.platform}
        </a>
      ) : (
        <Button
          size="sm"
          variant="outline"
          disabled
          className="shrink-0 ml-4"
        >
          N/A
        </Button>
      )}
    </div>
  );
}