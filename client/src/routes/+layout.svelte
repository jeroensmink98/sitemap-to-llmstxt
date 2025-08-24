<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<title>Sitemap to LLMS.txt API</title>
	<link rel="icon" href={favicon} />
</svelte:head>

<!-- Navigation Header -->
<header class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <div class="flex items-center">
                <h1 class="text-xl font-semibold text-gray-900">Sitemap to LLMS.txt</h1>
            </div>
            <nav class="flex space-x-4">
                <a 
                    href="/"
                    class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
                >
                    🏠 Home
                </a>
                <a 
                    href="/jobs"
                    class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
                >
                    📊 Job History
                </a>
                <a 
                    href="/about"
                    class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
                >
                    ℹ️ About
                </a>
            </nav>
        </div>
    </div>
</header>

{@render children?.()} 
