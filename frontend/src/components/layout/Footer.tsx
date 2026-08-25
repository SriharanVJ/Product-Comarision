/**
 * Footer component with copyright and links
 */

export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between space-y-4 md:flex-row md:space-y-0">
          <p className="text-sm text-gray-600">
            © {new Date().getFullYear()} QuickCompare. All rights reserved.
          </p>
          <div className="flex space-x-6">
            <a href="https://blinkit.com" target="_blank" rel="noopener noreferrer" className="text-sm text-gray-600 hover:text-blue-600">
              BlinkIt
            </a>
            <a href="https://zepto.com" target="_blank" rel="noopener noreferrer" className="text-sm text-gray-600 hover:text-blue-600">
              Zepto
            </a>
            <a href="https://swiggy.com" target="_blank" rel="noopener noreferrer" className="text-sm text-gray-600 hover:text-blue-600">
              Swiggy
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}