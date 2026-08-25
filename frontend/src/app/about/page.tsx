/**
 * About page for QuickCompare
 */

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
      <div className="bg-white rounded-lg shadow-sm p-8 md:p-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">About QuickCompare</h1>

        <div className="prose prose-blue max-w-none">
          <p className="text-lg text-gray-700 mb-6">
            QuickCompare helps you find the best deals across your favorite quick-commerce platforms.
            Search once and instantly compare prices, availability, and delivery times from BlinkIt,
            Zepto, and Swiggy Instamart.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">How it works</h2>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">1.</span>
              <span>Search for any product you want to buy</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">2.</span>
              <span>We compare prices and availability across multiple platforms</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">3.</span>
              <span>You save money and time by choosing the best option</span>
            </li>
          </ul>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">Why use QuickCompare?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">Save Money</h3>
              <p className="text-blue-800 text-sm">
                Find the cheapest prices across all platforms with our real-time comparison
              </p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">Save Time</h3>
              <p className="text-green-800 text-sm">
                No need to check multiple apps - we show you everything in one place
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-900 mb-2">Real-time Data</h3>
              <p className="text-purple-800 text-sm">
                Get accurate, up-to-date pricing and availability information
              </p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h3 className="font-semibold text-yellow-900 mb-2">Smart Recommendations</h3>
              <p className="text-yellow-800 text-sm">
                We highlight the best overall choice based on price and delivery speed
              </p>
            </div>
          </div>

          <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">Supported Platforms</h2>
          <div className="flex flex-wrap gap-4 mt-4">
            {['BlinkIt', 'Zepto', 'Swiggy Instamart'].map((platform) => (
              <div key={platform} className="flex items-center space-x-2 bg-gray-50 px-4 py-2 rounded-lg">
                <span className="text-2xl">🏪</span>
                <span className="font-medium text-gray-800">{platform}</span>
              </div>
            ))}
          </div>

          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              QuickCompare is a proof of concept product comparison tool. We are not affiliated with
              any of the quick-commerce platforms mentioned above.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}