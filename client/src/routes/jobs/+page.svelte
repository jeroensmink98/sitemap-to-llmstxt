<script lang="ts">
    import { onMount } from 'svelte';
    
    // Job history state
    let jobs = $state<Array<{
        job_id: string;
        status: string;
        message: string;
        created_at: string;
        updated_at: string;
        output?: string;
        url_count?: number;
        download_url?: string;
    }>>([]);
    
    let isLoading = $state(true);
    let error = $state<string | null>(null);
    
    // API configuration
    const API_BASE_URL = 'http://localhost:8000/api/v1';
    
    // Fetch job history
    async function fetchJobHistory() {
        try {
            isLoading = true;
            error = null;
            
            const response = await fetch(`${API_BASE_URL}/jobs`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch jobs: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Sort by creation date (newest first) and limit to 20
            const sortedJobs = data.jobs
                .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                .slice(0, 20);
            
            // Fetch additional details for completed jobs
            const enrichedJobs = await Promise.all(
                sortedJobs.map(async (job: any) => {
                    if (job.status === 'completed') {
                        try {
                            const infoResponse = await fetch(`${API_BASE_URL}/jobs/${job.job_id}/info`);
                            if (infoResponse.ok) {
                                const jobInfo = await infoResponse.json();
                                return {
                                    ...job,
                                    output: jobInfo.output_file,
                                    url_count: jobInfo.url_count,
                                    download_url: jobInfo.download_url
                                };
                            }
                        } catch (e) {
                            console.warn(`Failed to fetch details for job ${job.job_id}:`, e);
                        }
                    }
                    return job;
                })
            );
            
            jobs = enrichedJobs;
            
        } catch (err) {
            console.error('Failed to fetch job history:', err);
            error = err instanceof Error ? err.message : 'Failed to fetch job history';
        } finally {
            isLoading = false;
        }
    }
    
    // Refresh job history
    function refreshJobs() {
        fetchJobHistory();
    }
    
    // Format date for display
    function formatDate(dateString: string): string {
        try {
            const date = new Date(dateString);
            return date.toLocaleString();
        } catch {
            return dateString;
        }
    }
    
    // Get status color and icon
    function getStatusColor(status: string): string {
        switch (status) {
            case 'pending': return 'text-yellow-600 bg-yellow-50';
            case 'processing': return 'text-blue-600 bg-blue-50';
            case 'completed': return 'text-green-600 bg-green-50';
            case 'failed': return 'text-red-600 bg-red-50';
            default: return 'text-gray-600 bg-gray-50';
        }
    }
    
    function getStatusIcon(status: string): string {
        switch (status) {
            case 'pending': return '⏳';
            case 'processing': return '🔄';
            case 'completed': return '✅';
            case 'failed': return '❌';
            default: return '❓';
        }
    }
    
    // Extract filename from output path
    function getFilename(outputPath: string): string {
        if (!outputPath) return 'N/A';
        return outputPath.split('/').pop() || outputPath;
    }
    
    // Auto-refresh every 30 seconds
    let refreshInterval: number;
    
    onMount(() => {
        fetchJobHistory();
        
        // Set up auto-refresh
        refreshInterval = setInterval(refreshJobs, 30000);
        
        return () => {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        };
    });
</script>

<svelte:head>
    <title>Job History - Sitemap to LLMS.txt</title>
</svelte:head>


<div class="max-w-7xl mx-auto p-6">
    <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Job History</h1>
        <p class="text-gray-600">Overview of the last 20 sitemap processing jobs</p>
    </div>
    
    <!-- Error Display -->
    {#if error}
        <div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <div class="flex items-center">
                <span class="text-red-600 mr-2">❌</span>
                <p class="text-red-800">{error}</p>
            </div>
        </div>
    {/if}
    
    <!-- Loading State -->
    {#if isLoading}
        <div class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="ml-3 text-gray-600">Loading job history...</span>
        </div>
    {:else}
        <!-- Job History Table -->
        <div class="bg-white shadow-md rounded-lg overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div class="flex items-center justify-between">
                    <h2 class="text-lg font-medium text-gray-900">Recent Jobs</h2>
                    <button 
                        onclick={refreshJobs}
                        class="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors flex items-center"
                    >
                        🔄 Refresh
                    </button>
                </div>
            </div>
            
            {#if jobs.length === 0}
                <div class="px-6 py-12 text-center text-gray-500">
                    <p>No jobs found. Start processing a sitemap to see job history.</p>
                </div>
            {:else}
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Status
                                </th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Job ID
                                </th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Output File
                                </th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    URLs
                                </th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Created
                                </th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Updated
                                </th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            {#each jobs as job (job.job_id)}
                                <tr class="hover:bg-gray-50">
                                    <!-- Status -->
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(job.status)}">
                                            <span class="mr-1">{getStatusIcon(job.status)}</span>
                                            {job.status.toUpperCase()}
                                        </span>
                                    </td>
                                    
                                    <!-- Job ID -->
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                                        {job.job_id.slice(0, 8)}...
                                    </td>
                                    
                                    <!-- Output File -->
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {#if job.output}
                                            <span class="font-mono text-xs">{getFilename(job.output)}</span>
                                        {:else}
                                            <span class="text-gray-400">-</span>
                                        {/if}
                                    </td>
                                    
                                    <!-- URL Count -->
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {#if job.url_count !== undefined}
                                            <span class="font-medium">{job.url_count}</span>
                                        {:else}
                                            <span class="text-gray-400">-</span>
                                        {/if}
                                    </td>
                                    
                                    <!-- Created Date -->
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {formatDate(job.created_at)}
                                    </td>
                                    
                                    <!-- Updated Date -->
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {formatDate(job.updated_at)}
                                    </td>
                                    
                                    <!-- Actions -->
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        {#if job.status === 'completed' && job.download_url}
                                            <div class="flex space-x-2">
                                                <a 
                                                    href="{API_BASE_URL}/jobs/{job.job_id}/result"
                                                    class="inline-flex items-center px-3 py-1.5 bg-green-600 text-white text-xs rounded-md hover:bg-green-700 transition-colors"
                                                >
                                                    📥 Download
                                                </a>
                                                <button 
                                                    onclick={() => window.open(`${API_BASE_URL}/jobs/${job.job_id}/result`, '_blank')}
                                                    class="inline-flex items-center px-3 py-1.5 bg-purple-600 text-white text-xs rounded-md hover:bg-purple-700 transition-colors"
                                                >
                                                    🔗 Open
                                                </button>
                                            </div>
                                        {:else if job.status === 'failed'}
                                            <span class="text-red-600 text-xs">Failed</span>
                                        {:else}
                                            <span class="text-gray-400 text-xs">-</span>
                                        {/if}
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {/if}
        </div>
        
        <!-- Auto-refresh Info -->
        <div class="mt-4 text-center text-sm text-gray-500">
            <p>🔄 Auto-refreshing every 30 seconds • Last updated: {new Date().toLocaleTimeString()}</p>
        </div>
    {/if}
</div>
