/**
 * LoadingSkeleton component displays skeleton loaders for product cards
 */

export function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
          {/* Product header */}
          <div className="flex items-start space-x-4">
            {/* Image skeleton */}
            <div className="h-20 w-20 bg-gray-200 rounded-lg animate-pulse" />

            {/* Product info skeleton */}
            <div className="flex-1 space-y-2">
              <div className="h-6 bg-gray-200 rounded w-3/4 animate-pulse" />
              <div className="h-4 bg-gray-200 rounded w-1/2 animate-pulse" />
              <div className="h-5 bg-gray-200 rounded w-1/4 animate-pulse" />
            </div>
          </div>

          {/* Platform offer skeletons */}
          <div className="space-y-3 pt-4 border-t border-gray-200">
            {[...Array(2)].map((_, j) => (
              <div key={j} className="flex items-center justify-between">
                <div className="flex-1 space-y-2">
                  <div className="h-5 bg-gray-200 rounded w-1/4 animate-pulse" />
                  <div className="flex items-center space-x-4">
                    <div className="h-6 bg-gray-200 rounded w-20 animate-pulse" />
                    <div className="h-4 bg-gray-200 rounded w-24 animate-pulse" />
                  </div>
                </div>
                <div className="h-9 bg-gray-200 rounded w-32 animate-pulse ml-4" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}