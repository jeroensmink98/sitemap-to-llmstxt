<script lang="ts">
    let { siteUrl } = $props();
    
    // Form data matching JobRequest model - using $state for reactivity
    let formData = $state({
        domain: '',
        output: '',
        batch_size: 10,
        batch_delay: 1000,
        include_metadata: false
    });
    
    // Form validation state - using $state for reactivity
    let errors = $state<Record<string, string>>({});
    let isSubmitting = $state(false);
    
    // Job tracking state
    let currentJobId = $state<string | null>(null);
    let jobStatus = $state<string | null>(null);
    let jobMessage = $state<string | null>(null);
    let showJobStatus = $state(false);
    let generatedFilename = $state<string | null>(null);
    
    // File content display state
    let fileContent = $state<string | null>(null);
    let showFileContent = $state(false);
    let isLoadingFile = $state(false);
    
    // API configuration
    const API_BASE_URL = 'http://localhost:8000/api/v1';
    
    // Update domain when siteUrl changes
    $effect(() => {
        if (siteUrl) {
            formData.domain = siteUrl;
        }
    });
    
    function validateForm(): boolean {
        errors = {};
        
        if (!formData.domain.trim()) {
            errors.domain = 'Domain is required';
        } else if (!isValidUrl(formData.domain)) {
            errors.domain = 'Please enter a valid URL';
        }
        
        if (formData.batch_size < 1 || formData.batch_size > 100) {
            errors.batch_size = 'Batch size must be between 1 and 100';
        }
        
        if (formData.batch_delay < 100 || formData.batch_delay > 30000) {
            errors.batch_delay = 'Batch delay must be between 100 and 30000 milliseconds';
        }
        
        return Object.keys(errors).length === 0;
    }
    
    function isValidUrl(url: string): boolean {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }
    
    async function createJob(): Promise<{ jobId: string; filename: string } | null> {
        try {
            const response = await fetch(`${API_BASE_URL}/jobs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    domain: formData.domain,
                    output: formData.output || undefined,
                    batch_size: formData.batch_size,
                    batch_delay: formData.batch_delay,
                    include_metadata: formData.include_metadata
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const jobData = await response.json();
            return {
                jobId: jobData.job_id,
                filename: jobData.output || 'auto-generated'
            };
        } catch (error) {
            console.error('Failed to create job:', error);
            throw error;
        }
    }
    
    async function checkJobStatus(jobId: string): Promise<{ status: string; message: string }> {
        try {
            const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/status`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const statusData = await response.json();
            return {
                status: statusData.status,
                message: statusData.message || 'No message available'
            };
        } catch (error) {
            console.error('Failed to check job status:', error);
            throw error;
        }
    }
    
    async function pollJobStatus(jobId: string) {
        const maxAttempts = 60; // 5 minutes with 5-second intervals
        let attempts = 0;
        
        const pollInterval = setInterval(async () => {
            try {
                attempts++;
                const { status, message } = await checkJobStatus(jobId);
                
                jobStatus = status;
                jobMessage = message;
                
                if (status === 'completed' || status === 'failed') {
                    clearInterval(pollInterval);
                    if (status === 'completed') {
                        // Show download link
                        showDownloadLink(jobId);
                    }
                }
                
                if (attempts >= maxAttempts) {
                    clearInterval(pollInterval);
                    jobMessage = 'Job is taking longer than expected. Please check the status manually.';
                }
            } catch (error) {
                console.error('Error polling job status:', error);
                jobMessage = 'Error checking job status. Please try again.';
            }
        }, 5000); // Poll every 5 seconds
    }
    
    function showDownloadLink(jobId: string) {
        // This will be implemented to show a download button
        console.log('Job completed! Download available for job:', jobId);
    }
    
    async function fetchFileContent(jobId: string) {
        try {
            isLoadingFile = true;
            const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/result`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch file: ${response.status} ${response.statusText}`);
            }
            
            const content = await response.text();
            fileContent = content;
            showFileContent = true;
        } catch (error) {
            console.error('Failed to fetch file content:', error);
            errors.submit = 'Failed to load file content. You can still download the file.';
        } finally {
            isLoadingFile = false;
        }
    }
    
    function toggleFileContent() {
        if (showFileContent) {
            showFileContent = false;
            fileContent = null;
        } else if (currentJobId) {
            fetchFileContent(currentJobId);
        }
    }
    
    function closeFileContent() {
        showFileContent = false;
        fileContent = null;
    }
    
    function openInNewTab(jobId: string) {
        const url = `${API_BASE_URL}/jobs/${jobId}/result`;
        window.open(url, '_blank');
    }
    
    async function copyToClipboard() {
        if (fileContent) {
            try {
                await navigator.clipboard.writeText(fileContent);
                // Show a temporary success message
                const originalText = '📋 Copy to Clipboard';
                const button = document.querySelector('[data-copy-button]') as HTMLButtonElement;
                if (button) {
                    button.textContent = '✅ Copied!';
                    setTimeout(() => {
                        button.textContent = originalText;
                    }, 2000);
                }
            } catch (error) {
                console.error('Failed to copy to clipboard:', error);
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = fileContent;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                const button = document.querySelector('[data-copy-button]') as HTMLButtonElement;
                if (button) {
                    button.textContent = '✅ Copied!';
                    setTimeout(() => {
                        button.textContent = '📋 Copy to Clipboard';
                    }, 2000);
                }
            }
        }
    }
    
    async function handleSubmit(event: Event) {
        event.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        isSubmitting = true;
        errors.submit = '';
        
        try {
            // Create the job
            const jobResult = await createJob();
            
            if (jobResult) {
                const { jobId, filename } = jobResult;
                currentJobId = jobId;
                generatedFilename = filename;
                jobStatus = 'pending';
                jobMessage = 'Job created successfully! Processing...';
                showJobStatus = true;
                
                // Start polling for status updates
                pollJobStatus(jobId);
                
                // Reset form
                resetForm();
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            errors.submit = error instanceof Error ? error.message : 'Failed to submit form. Please try again.';
        } finally {
            isSubmitting = false;
        }
    }
    
    function resetForm() {
        formData = {
            domain: '',
            output: '',
            batch_size: 10,
            batch_delay: 1000,
            include_metadata: false
        };
        errors = {};
    }
    
    function resetJobStatus() {
        currentJobId = null;
        jobStatus = null;
        jobMessage = null;
        showJobStatus = false;
        showFileContent = false;
        fileContent = null;
        generatedFilename = null;
    }
    
    function getStatusColor(status: string): string {
        switch (status) {
            case 'pending': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
            case 'processing': return 'text-blue-600 bg-blue-50 border-blue-200';
            case 'completed': return 'text-green-600 bg-green-50 border-green-200';
            case 'failed': return 'text-red-600 bg-red-50 border-red-200';
            default: return 'text-gray-600 bg-gray-50 border-gray-200';
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
</script>

<div>
    <h2 class="text-2xl font-bold mb-6 text-gray-800">Sitemap to LLMS.txt Configuration</h2>
    
    <!-- Job Status Display -->
    {#if showJobStatus && currentJobId && jobStatus}
        <div class="mb-6 p-4 border rounded-md {getStatusColor(jobStatus)}">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <span class="text-2xl">{getStatusIcon(jobStatus)}</span>
                    <div>
                        <h3 class="font-medium">Job Status: {jobStatus.toUpperCase()}</h3>
                        <p class="text-sm opacity-90">{jobMessage}</p>
                        {#if currentJobId}
                            <p class="text-xs opacity-75">Job ID: {currentJobId}</p>
                        {/if}
                        {#if generatedFilename}
                            <p class="text-xs opacity-75">Output: {generatedFilename}</p>
                        {/if}
                    </div>
                </div>
                <button 
                    onclick={resetJobStatus}
                    class="text-sm px-2 py-1 border rounded hover:bg-white hover:bg-opacity-20"
                >
                    Close
                </button>
            </div>
            
            {#if jobStatus === 'completed'}
                <div class="mt-3 pt-3 border-t border-current border-opacity-20">
                    <div class="flex flex-wrap gap-3">
                        <button 
                            onclick={toggleFileContent}
                            class="inline-flex items-center px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
                        >
                            {#if isLoadingFile}
                                <span class="animate-spin mr-2">⏳</span>
                                Loading...
                            {:else if showFileContent}
                                👁️ Hide Content
                            {:else}
                                👁️ View Content
                            {/if}
                        </button>
                        
                        <button 
                            onclick={() => openInNewTab(currentJobId!)}
                            class="inline-flex items-center px-3 py-2 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700 transition-colors"
                        >
                            🔗 Open in New Tab
                        </button>
                        
                        <a 
                            href="{API_BASE_URL}/jobs/{currentJobId}/result"
                            class="inline-flex items-center px-3 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors"
                        >
                            📥 Download LLMS.txt
                        </a>
                        
                        <a 
                            href="/jobs"
                            class="inline-flex items-center px-3 py-2 bg-gray-600 text-white text-sm rounded-md hover:bg-gray-700 transition-colors"
                        >
                            📊 View All Jobs
                        </a>
                    </div>
                </div>
            {/if}
        </div>
    {/if}
    
    <!-- File Content Display -->
    {#if showFileContent && fileContent}
        <div class="mb-6 p-4 border border-gray-200 rounded-md bg-gray-50">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-medium text-gray-800">Generated LLMS.txt Content</h3>
                <div class="flex items-center space-x-2">
                    <button 
                        onclick={copyToClipboard}
                        data-copy-button
                        class="text-sm px-3 py-1 border border-gray-300 rounded hover:bg-white transition-colors flex items-center space-x-1"
                    >
                        📋 Copy to Clipboard
                    </button>
                    <button 
                        onclick={closeFileContent}
                        class="text-sm px-2 py-1 border border-gray-300 rounded hover:bg-white transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
            
            <div class="bg-white border border-gray-200 rounded-md p-4 max-h-96 overflow-y-auto">
                <pre class="text-sm text-gray-800 whitespace-pre-wrap font-mono leading-relaxed">{fileContent}</pre>
            </div>
            
            <div class="mt-3 text-xs text-gray-500">
                <p>💡 <strong>Tip:</strong> You can copy this content or download the file using the button above.</p>
            </div>
        </div>
    {/if}
    
    <form onsubmit={handleSubmit} class="space-y-6">
        <!-- Domain/URL Input -->
        <div>
            <label for="domain" class="block text-sm font-medium text-gray-700 mb-2">
                Site URL *
            </label>
            <input 
                type="url" 
                id="domain"
                bind:value={formData.domain}
                placeholder="https://example.com" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                class:border-red-500={errors.domain}
            />
            {#if errors.domain}
                <p class="mt-1 text-sm text-red-600">{errors.domain}</p>
            {/if}
        </div>
        
        <!-- Output Filename -->
        <div>
            <label for="output" class="block text-sm font-medium text-gray-700 mb-2">
                Output Filename (Optional)
            </label>
            <input 
                type="text" 
                id="output"
                bind:value={formData.output}
                placeholder="Leave empty for auto-generation" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p class="mt-1 text-sm text-gray-500">
                If left empty, will generate: domain-name-llms.txt
            </p>
        </div>
        
        <!-- Batch Size -->
        <div>
            <label for="batch_size" class="block text-sm font-medium text-gray-700 mb-2">
                Batch Size
            </label>
            <input 
                type="number" 
                id="batch_size"
                bind:value={formData.batch_size}
                min="1" 
                max="100"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                class:border-red-500={errors.batch_size}
            />
            {#if errors.batch_size}
                <p class="mt-1 text-sm text-red-600">{errors.batch_size}</p>
            {/if}
            <p class="mt-1 text-sm text-gray-500">
                Number of concurrent requests per batch (1-100)
            </p>
        </div>
        
        <!-- Batch Delay -->
        <div>
            <label for="batch_delay" class="block text-sm font-medium text-gray-700 mb-2">
                Batch Delay (milliseconds)
            </label>
            <input 
                type="number" 
                id="batch_delay"
                bind:value={formData.batch_delay}
                min="100" 
                max="30000"
                step="100"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                class:border-red-500={errors.batch_delay}
            />
            {#if errors.batch_delay}
                <p class="mt-1 text-sm text-red-600">{errors.batch_delay}</p>
            {/if}
            <p class="mt-1 text-sm text-gray-500">
                Delay between batches to be respectful to servers (100-30000ms)
            </p>
        </div>
        
        <!-- Include Metadata -->
        <div class="flex items-center">
            <input 
                type="checkbox" 
                id="include_metadata"
                bind:checked={formData.include_metadata}
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="include_metadata" class="ml-2 block text-sm text-gray-700">
                Include sitemap metadata
            </label>
        </div>
        
        <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
            <h3 class="text-sm font-medium text-blue-800 mb-2">About Metadata</h3>
            <p class="text-sm text-blue-700">
                When enabled, includes additional sitemap information like last modification date, 
                change frequency, and priority for each URL. This is useful for internal documentation 
                but not part of the official LLMS.txt specification.
            </p>
        </div>
        
        <!-- Submit Error -->
        {#if errors.submit}
            <div class="bg-red-50 border border-red-200 rounded-md p-4">
                <p class="text-sm text-red-600">{errors.submit}</p>
            </div>
        {/if}
        
        <!-- Form Actions -->
        <div class="flex space-x-4">
            <button 
                type="submit" 
                disabled={isSubmitting}
                class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isSubmitting ? 'Creating Job...' : 'Generate LLMS.txt'}
            </button>
            
            <button 
                type="button" 
                onclick={resetForm}
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
                Reset
            </button>
        </div>
    </form>
</div>
