<script lang="ts">
    import SiteForm from '$lib/components/site-form.svelte';

    let siteUrl = '';
</script>

<!-- Main Content -->
<div class="max-w-7xl mx-auto p-6">
    <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Sitemap to LLMS.txt</h1>
        <p class="text-gray-600">Process sitemaps and generate LLMS.txt files for your websites</p>
    </div>
    
    <div class="bg-white shadow-md rounded-lg overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h2 class="text-lg font-medium text-gray-900">Configuration Form</h2>
        </div>
        <div class="p-6">
            <SiteForm siteUrl={siteUrl} />
        </div>
    </div>
</div>
