<script lang="ts">
    // About page content
</script>

<svelte:head>
    <title>About - Sitemap to LLMS.txt</title>
</svelte:head>

<div class="max-w-7xl mx-auto p-6">
    <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">About Sitemap to LLMS.txt</h1>
        <p class="text-gray-600">Converting website sitemaps into LLM-friendly documentation</p>
    </div>
    
    <div class="bg-white shadow-md rounded-lg overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h2 class="text-lg font-medium text-gray-900">What We Do</h2>
        </div>
        <div class="p-6 space-y-6">
            
            <!-- What is LLMS.txt -->
            <div>
                <h3 class="text-xl font-semibold text-gray-800 mb-3">What is LLMS.txt?</h3>
                <p class="text-gray-700 mb-3">
                    <strong>LLMS.txt</strong> is a proposed web standard that helps Large Language Models (LLMs) understand and navigate website content more effectively. 
                    According to the <a href="https://llmstxt.org/" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">official specification</a>, 
                    it's designed to address a critical limitation: LLM context windows are too small to handle most websites in their entirety.
                </p>
                <p class="text-gray-700">
                    Instead of trying to parse complex HTML pages with navigation, ads, and JavaScript, LLMS.txt provides a clean, 
                    structured markdown file that gives LLMs concise, expert-level information in a single, accessible location.
                </p>
            </div>

            <!-- Our Solution -->
            <div>
                <h3 class="text-xl font-semibold text-gray-800 mb-3">Our Solution</h3>
                <p class="text-gray-700 mb-3">
                    <strong>Sitemap to LLMS.txt</strong> is an API service that automatically converts existing website sitemaps into 
                    properly formatted LLMS.txt files. We bridge the gap between traditional sitemaps and the new LLMS.txt standard.
                </p>
                <p class="text-gray-700">
                    Our service processes sitemaps, extracts relevant content, and generates LLMS.txt files that follow the official specification, 
                    making websites more accessible to AI assistants and LLMs.
                </p>
            </div>

            <!-- How It Works -->
            <div>
                <h3 class="text-xl font-semibold text-gray-800 mb-3">How It Works</h3>
                <div class="bg-gray-50 p-4 rounded-lg">
                    <ol class="list-decimal list-inside space-y-2 text-gray-700">
                        <li><strong>Sitemap Discovery:</strong> We automatically discover and parse sitemaps from your website</li>
                        <li><strong>Content Extraction:</strong> Extract URLs and metadata from sitemap files</li>
                        <li><strong>LLMS.txt Generation:</strong> Convert the sitemap data into properly formatted LLMS.txt files</li>
                        <li><strong>File Delivery:</strong> Provide the generated LLMS.txt file for download or direct use</li>
                    </ol>
                </div>
            </div>

            <!-- LLMS.txt Format -->
            <div>
                <h3 class="text-xl font-semibold text-gray-800 mb-3">LLMS.txt Format</h3>
                <p class="text-gray-700 mb-3">
                    According to the <a href="https://llmstxt.org/" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">llms.txt specification</a>, 
                    each file follows a specific structure:
                </p>
                <div class="bg-gray-50 p-4 rounded-lg font-mono text-sm">
                    <pre class="whitespace-pre-wrap"># Project/Site Name

> Brief description of the project or site

Detailed information about the project

## Section Name

- [Link Title](https://url): Description of the content

## Optional

- [Secondary Info](https://url): Non-essential information</pre>
                </div>
            </div>

            <!-- Benefits -->
            <div>
                <h3 class="text-xl font-semibold text-gray-800 mb-3">Benefits of LLMS.txt</h3>
                <div class="grid md:grid-cols-2 gap-4">
                    <div class="bg-blue-50 p-4 rounded-lg">
                        <h4 class="font-semibold text-blue-800 mb-2">For LLMs & AI Assistants</h4>
                        <ul class="text-blue-700 text-sm space-y-1">
                            <li>• Faster content understanding</li>
                            <li>• Better context for user queries</li>
                            <li>• Reduced processing overhead</li>
                            <li>• More accurate responses</li>
                        </ul>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg">
                        <h4 class="font-semibold text-green-800 mb-2">For Website Owners</h4>
                        <ul class="text-green-700 text-sm space-y-1">
                            <li>• Improved AI accessibility</li>
                            <li>• Better SEO for AI-powered search</li>
                            <li>• Enhanced user experience</li>
                            <li>• Future-proof content strategy</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Use Cases -->
            <div>
                <h3 class="text-xl font-semibold text-gray-800 mb-3">Common Use Cases</h3>
                <div class="grid md:grid-cols-3 gap-4">
                    <div class="text-center p-4 border border-gray-200 rounded-lg">
                        <div class="text-3xl mb-2">📚</div>
                        <h4 class="font-semibold text-gray-800">Documentation Sites</h4>
                        <p class="text-sm text-gray-600">Help LLMs understand API docs and technical content</p>
                    </div>
                    <div class="text-center p-4 border border-gray-200 rounded-lg">
                        <div class="text-3xl mb-2">🏢</div>
                        <h4 class="font-semibold text-gray-800">Business Websites</h4>
                        <p class="text-sm text-gray-600">Provide company information and service details</p>
                    </div>
                    <div class="text-center p-4 border border-gray-200 rounded-lg">
                        <div class="text-3xl mb-2">🎓</div>
                        <h4 class="font-semibold text-gray-800">Educational Resources</h4>
                        <p class="text-sm text-gray-600">Make course materials and resources AI-accessible</p>
                    </div>
                </div>
            </div>

            <!-- Technical Details -->
            <div>
                <h3 class="text-xl font-semibold text-gray-800 mb-3">Technical Implementation</h3>
                <p class="text-gray-700 mb-3">
                    Our API is built with modern technologies to ensure reliability and performance:
                </p>
                <div class="bg-gray-50 p-4 rounded-lg">
                    <ul class="space-y-2 text-gray-700">
                        <li><strong>Backend:</strong> FastAPI with Celery for background processing</li>
                        <li><strong>Processing:</strong> Automated sitemap discovery and content extraction</li>
                        <li><strong>Output:</strong> Standard-compliant LLMS.txt files</li>
                        <li><strong>Delivery:</strong> Direct download or API integration</li>
                    </ul>
                </div>
            </div>

            <!-- Get Started -->
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 class="text-xl font-semibold text-blue-800 mb-3">Ready to Get Started?</h3>
                <p class="text-blue-700 mb-4">
                    Convert your website's sitemap to an LLMS.txt file and make your content more accessible to AI assistants and LLMs.
                </p>
                <div class="flex flex-wrap gap-3">
                    <a 
                        href="/" 
                        class="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                    >
                        🚀 Start Converting
                    </a>
                    <a 
                        href="/jobs" 
                        class="inline-flex items-center px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 transition-colors"
                    >
                        📊 View Job History
                    </a>
                </div>
            </div>

            <!-- Learn More -->
            <div class="border-t border-gray-200 pt-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-3">Learn More</h3>
                <p class="text-gray-700 mb-3">
                    To learn more about the LLMS.txt standard and how it's being adopted across the web:
                </p>
                <div class="flex flex-wrap gap-3">
                    <a 
                        href="https://llmstxt.org/" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        class="inline-flex items-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition-colors"
                    >
                        📖 Official Specification
                    </a>
                    <a 
                        href="https://github.com/jph00/llms_txt" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        class="inline-flex items-center px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 transition-colors"
                    >
                        🔗 GitHub Repository
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>