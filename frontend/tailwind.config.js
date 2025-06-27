module.exports = {
  darkMode: 'class',
  content: [
    './src/**/*.{html,js,svelte,ts}',
    './src/app.html'
  ],
  safelist: [
    // Modal overlay and popup
    'fixed', 'inset-0', 'z-50', 'flex', 'items-center', 'justify-center',
    'bg-black', 'bg-opacity-40',
    'bg-white', 'dark:bg-gray-800', 'dark:text-gray-100',
    'rounded-lg', 'shadow-lg', 'p-6', 'min-w-[300px]', 'max-w-[90vw]', 'relative', 'border', 'dark:border-gray-700',
    'absolute', 'top-2', 'right-2', 'w-11', 'h-11', 'rounded-full', 'bg-gray-200', 'dark:bg-gray-700', 'text-2xl', 'font-bold', 'shadow', 'hover:bg-gray-300', 'dark:hover:bg-gray-600', 'active:bg-gray-400', 'dark:active:bg-gray-800', 'focus:outline-none', 'focus:ring-2', 'focus:ring-blue-400',
    'mt-4', 'px-4', 'py-2', 'bg-blue-600', 'dark:bg-blue-700', 'text-white', 'rounded', 'hover:bg-blue-700', 'dark:hover:bg-blue-800',
    // Legend formatting
    'flex', 'flex-wrap', 'gap-4', 'gap-2', 'items-center', 'inline-block', 'w-4', 'h-4', 'w-5', 'h-5', 'rounded-full', 'mr-2', 'text-xs', 'mt-4', 'dark:bg-gray-800', 'p-2', 'rounded-lg', 'dark:text-gray-200',
    // Calendar color backgrounds
    'bg-blue-100', 'bg-green-100', 'bg-yellow-100', 'bg-red-100', 'bg-purple-100', 'bg-pink-100', 'bg-indigo-100', 'bg-teal-100', 'bg-orange-100', 'bg-cyan-100', 'bg-lime-100', 'bg-rose-100',
    // Calendar color text
    'text-blue-800', 'text-green-800', 'text-yellow-800', 'text-red-800', 'text-purple-800', 'text-pink-800', 'text-indigo-800', 'text-teal-800', 'text-orange-800', 'text-cyan-800', 'text-lime-800', 'text-rose-800',
    // Calendar color hover
    'hover:bg-blue-200', 'hover:bg-green-200', 'hover:bg-yellow-200', 'hover:bg-red-200', 'hover:bg-purple-200', 'hover:bg-pink-200', 'hover:bg-indigo-200', 'hover:bg-teal-200', 'hover:bg-orange-200', 'hover:bg-cyan-200', 'hover:bg-lime-200', 'hover:bg-rose-200',
    // Calendar color borders
    'border-blue-400', 'border-green-400', 'border-yellow-400', 'border-red-400', 'border-purple-400', 'border-pink-400', 'border-indigo-400', 'border-teal-400', 'border-orange-400', 'border-cyan-400', 'border-lime-400', 'border-rose-400',
    // Calendar grid/cell classes
    'border', 'min-h-[60px]', 'p-1', 'rounded', 'shadow-sm', 'cursor-pointer', 'transition-colors', 'dark:border-gray-700',
    'bg-white', 'dark:bg-gray-900', 'dark:text-gray-100', 'hover:bg-gray-50', 'dark:hover:bg-gray-800',
    'bg-gray-100', 'dark:bg-gray-800', 'dark:text-gray-400', 'hover:bg-gray-200', 'dark:hover:bg-gray-700',
    'bg-yellow-200', 'dark:bg-yellow-600', 'border-yellow-500', 'dark:border-yellow-400', 'hover:bg-yellow-300', 'dark:hover:bg-yellow-500',
    'text-blue-600', 'dark:text-blue-300', 'text-yellow-800',
    'font-bold', 'text-xs', 'underline', 'mt-1',
    'grid', 'grid-cols-7', 'gap-1', 'text-center', 'font-semibold', 'select-none',
    'max-w-2xl', 'mx-auto', 'mt-8', 'dark:bg-gray-900', 'dark:text-white', 'rounded-lg',
    'text-2xl', 'font-bold', 'px-4', 'py-2', 'bg-gray-200', 'dark:bg-gray-800', 'dark:text-white', 'rounded-lg', 'shadow', 'active:bg-gray-300', 'dark:active:bg-gray-700', 'focus:outline-none', 'focus:ring-2', 'focus:ring-blue-400',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms')
  ],
}; 