# Sitemap to LLMS.txt - Project Knowledge Base

## 🏗️ **Project Overview**

**Sitemap to LLMS.txt** is a web application that processes sitemaps from websites and generates LLMS.txt files. The application consists of a FastAPI backend with Celery for background processing and a Svelte 5 frontend with Tailwind CSS styling.

## 📁 **Project Structure**

```
sitemap-to-llmstxt/
├── backend/                    # FastAPI backend
│   ├── api/
│   │   └── routes.py         # API endpoints
│   ├── services/
│   │   ├── sitemap_service.py # Sitemap processing logic
│   │   └── llms_generator.py  # LLMS.txt generation logic
│   ├── celery_app.py         # Celery configuration
│   ├── main.py               # FastAPI app entry point
│   ├── models.py             # Pydantic models
│   └── tasks.py              # Background tasks
├── client/                    # Svelte 5 frontend
│   ├── src/
│   │   ├── lib/components/
│   │   │   └── site-form.svelte # Main form component
│   │   └── routes/
│   │       ├── +page.svelte      # Home page
│   │       └── jobs/+page.svelte # Job history page
│   └── package.json
├── docker/                    # Docker configuration
├── outputs/                   # Generated LLMS.txt files
└── pyproject.toml            # Python dependencies
```

## 🔧 **Backend Architecture**

### **FastAPI Application**
- **Port**: 8000
- **API Base**: `/api/v1`
- **Background Processing**: Celery with Redis
- **File Storage**: Local `outputs/` directory

### **Key Dependencies**
- **FastAPI**: Web framework
- **Celery**: Background task queue
- **Redis**: Job status storage and message broker
- **Pydantic**: Data validation and models
- **uv**: Python package manager (used instead of pip)

### **API Endpoints**

#### **POST `/api/v1/jobs`**
- Creates new sitemap processing job
- Generates unique filename using timestamp + job ID
- Returns `JobResponse` with job details

#### **GET `/api/v1/jobs/{job_id}/status`**
- Returns current job status
- Used for frontend polling

#### **GET `/api/v1/jobs/{job_id}/result`**
- Downloads generated LLMS.txt file
- Only available for completed jobs

#### **GET `/api/v1/jobs/{job_id}/info`**
- Returns job metadata without file download
- Includes URL count and file information

#### **GET `/api/v1/jobs`**
- Lists all jobs (for monitoring)
- Used by job history page

### **Data Models**

#### **JobRequest**
```python
class JobRequest(BaseModel):
    domain: str                    # Website URL
    output: Optional[str] = None   # Custom filename (optional)
    batch_size: int = 10          # Concurrent requests per batch
    batch_delay: int = 1000       # Delay between batches (ms)
    include_metadata: bool = False # Include sitemap metadata
```

#### **JobResponse**
```python
class JobResponse(BaseModel):
    job_id: str                   # Unique job identifier
    status: JobStatus             # Current job status
    message: str                  # Status message
    output: Optional[str] = None  # Generated filename
```

#### **JobStatusResponse**
```python
class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
    created_at: str
    updated_at: str
```

#### **JobResultResponse**
```python
class JobResultResponse(BaseModel):
    job_id: str
    status: str
    output_file: str
    url_count: int
    download_url: str
```

### **Job Statuses**
- **pending**: Job created, waiting to be processed
- **processing**: Currently processing sitemap
- **completed**: Successfully generated LLMS.txt
- **failed**: Processing failed with error

## 🎨 **Frontend Architecture**

### **Svelte 5 Features Used**
- **`$state()`**: Reactive state management
- **`$props()`**: Component props
- **`$effect()`**: Side effects and reactivity
- **`onsubmit`/`onclick`**: Event handlers (Svelte 5 syntax)

### **Key Components**

#### **SiteForm Component (`site-form.svelte`)**
- **Purpose**: Main form for submitting sitemap processing jobs
- **Features**:
  - Form validation with client-side error handling
  - Real-time job status polling
  - File content preview with copy-to-clipboard
  - Download, view, and open-in-new-tab options
  - Job status display with visual indicators

#### **Job History Page (`/jobs`)**
- **Purpose**: Display last 20 jobs in table format
- **Features**:
  - Real-time job status updates
  - Auto-refresh every 30 seconds
  - Download and open buttons for completed jobs
  - Responsive table with status indicators
  - Manual refresh capability

### **State Management**
```typescript
// Form data state
let formData = $state({
    domain: '',
    output: '',
    batch_size: 10,
    batch_delay: 1000,
    include_metadata: false
});

// Job tracking state
let currentJobId = $state<string | null>(null);
let jobStatus = $state<string | null>(null);
let jobMessage = $state<string | null>(null);
let showJobStatus = $state(false);
let generatedFilename = $state<string | null>(null);

// File content state
let fileContent = $state<string | null>(null);
let showFileContent = $state(false);
let isLoadingFile = $state(false);
```

### **API Integration**
- **Base URL**: `http://localhost:8000/api/v1`
- **Job Creation**: POST to `/jobs`
- **Status Polling**: GET from `/jobs/{id}/status`
- **File Download**: GET from `/jobs/{id}/result`
- **Job Info**: GET from `/jobs/{id}/info`

## 🚀 **Key Features & Implementation**

### **1. Unique Filename Generation**
```python
# Prevents file collisions for concurrent users
if not request.output:
    domain_name = request.domain.replace("https://", "").replace("http://", "").replace("www.", "")
    domain_name = domain_name.split('.')[0]
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    request.output = f"{domain_name}-{timestamp}-{job_id[:8]}-llms.txt"
```

### **2. Job Status Polling**
```typescript
async function pollJobStatus(jobId: string) {
    const maxAttempts = 60; // 5 minutes with 5-second intervals
    const pollInterval = setInterval(async () => {
        const { status, message } = await checkJobStatus(jobId);
        jobStatus = status;
        jobMessage = message;
        
        if (status === 'completed' || status === 'failed') {
            clearInterval(pollInterval);
        }
    }, 5000); // Poll every 5 seconds
}
```

### **3. File Content Preview**
```typescript
async function fetchFileContent(jobId: string) {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/result`);
    const content = await response.text();
    fileContent = content;
    showFileContent = true;
}
```

### **4. Copy to Clipboard**
```typescript
async function copyToClipboard() {
    try {
        await navigator.clipboard.writeText(fileContent);
        // Show success feedback
    } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = fileContent;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    }
}
```

### **5. Auto-refresh Job History**
```typescript
onMount(() => {
    fetchJobHistory();
    refreshInterval = setInterval(refreshJobs, 30000); // 30 seconds
    
    return () => {
        if (refreshInterval) {
            clearInterval(refreshInterval);
        }
    };
});
```

## 🛡️ **Security & Error Handling**

### **File Collision Prevention**
- **Unique Filenames**: Timestamp + job ID ensures uniqueness
- **Concurrent Safety**: Multiple users can process same domain simultaneously
- **File Cleanup**: Automatic removal of files older than 24 hours

### **Error Handling**
```python
try:
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
except OSError as e:
    error_msg = f"Failed to write output file: {str(e)}"
    update_job_status(job_id, "failed", error_msg)
    return
```

### **Frontend Error Handling**
- **API Errors**: Graceful fallbacks and user-friendly messages
- **Validation**: Client-side form validation with clear error messages
- **Network Issues**: Retry logic and offline state handling

## 🎯 **User Experience Features**

### **Form Validation**
- **URL Validation**: Ensures valid website URLs
- **Batch Size**: 1-100 concurrent requests
- **Batch Delay**: Minimum 100ms, maximum 30 seconds
- **Real-time Feedback**: Immediate validation errors

### **Job Progress Tracking**
- **Visual Status**: Color-coded status indicators
- **Progress Messages**: Detailed status updates
- **Job ID Display**: Easy reference for support
- **Filename Preview**: Shows generated output filename

### **File Access Options**
- **Download**: Direct file download
- **View Content**: In-browser content preview
- **Copy to Clipboard**: One-click content copying
- **Open in New Tab**: Browser-native file viewing

### **Navigation & History**
- **Consistent Header**: Navigation between pages
- **Job History**: Complete overview of all jobs
- **Auto-refresh**: Always up-to-date information
- **Responsive Design**: Works on all devices

## 🔄 **Background Processing**

### **Celery Task Flow**
1. **Job Creation**: API creates job and stores status in Redis
2. **Task Dispatch**: Celery task queued with job parameters
3. **Sitemap Processing**: Extract URLs from sitemaps
4. **LLMS Generation**: Generate formatted content
5. **File Writing**: Save to unique filename
6. **Status Update**: Mark job as completed
7. **Cleanup**: Remove old files

### **Redis Usage**
- **Job Status**: `job_status:{job_id}` with 1-hour TTL
- **Job Results**: `job_result:{job_id}` with 1-hour TTL
- **Message Broker**: Celery task queue

### **File Management**
- **Output Directory**: `outputs/` folder
- **File Naming**: `{domain}-{timestamp}-{job_id}-llms.txt`
- **Cleanup Policy**: Remove files older than 24 hours
- **Storage**: Local filesystem (can be changed to cloud storage)

## 🚀 **Deployment & Configuration**

### **Environment Variables**
```bash
REDIS_URL=redis://localhost:6379/0  # Redis connection string
```

### **Docker Support**
- **docker-compose.yml**: Redis + Backend + Frontend
- **Dockerfile.simple**: Backend container
- **Port Mappings**: 8000 (API), 3000 (Frontend), 6379 (Redis)

### **Development Setup**
```bash
# Backend
cd backend
uv install
uv run python main.py

# Frontend
cd client
pnpm install
pnpm dev

# Redis
docker run -d -p 6379:6379 redis:alpine
```

## 📊 **Performance Considerations**

### **Batch Processing**
- **Configurable Batch Size**: 1-100 concurrent requests
- **Rate Limiting**: Configurable delays between batches
- **Memory Management**: Process URLs in chunks

### **File Cleanup**
- **Automatic Cleanup**: 24-hour retention policy
- **Disk Space**: Prevents unlimited file accumulation
- **Background Process**: Cleanup runs after each job

### **API Optimization**
- **Status Polling**: 5-second intervals with timeout
- **Lazy Loading**: Only fetch job details when needed
- **Caching**: Redis-based job status storage

## 🔮 **Future Enhancements**

### **Potential Improvements**
- **Cloud Storage**: S3/Google Cloud for file storage
- **User Authentication**: Multi-user support
- **Job Scheduling**: Recurring sitemap processing
- **API Rate Limiting**: Prevent abuse
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Webhooks**: Notify external systems of job completion

### **Scalability Considerations**
- **Horizontal Scaling**: Multiple Celery workers
- **Load Balancing**: Multiple API instances
- **Database**: PostgreSQL for persistent job storage
- **Message Queue**: RabbitMQ for high-volume processing

## 🐛 **Common Issues & Solutions**

### **Svelte 5 Migration**
- **Deprecation Warnings**: Use `onsubmit` instead of `on:submit`
- **Reactivity**: Ensure all state variables use `$state()`
- **Event Handling**: Use `onclick` instead of `on:click`

### **File Permission Issues**
- **Output Directory**: Ensure `outputs/` folder is writable
- **File Conflicts**: Unique filenames prevent overwrites
- **Cleanup Errors**: Graceful handling of file deletion failures

### **Redis Connection Issues**
- **Connection String**: Verify `REDIS_URL` environment variable
- **Network Access**: Ensure Redis is accessible from backend
- **Authentication**: Configure Redis password if required

## 📚 **Technical Decisions & Rationale**

### **Why Svelte 5?**
- **Modern Reactivity**: `$state()` provides better performance
- **TypeScript Support**: Excellent type safety
- **Bundle Size**: Smaller than React/Vue alternatives
- **Developer Experience**: Intuitive syntax and tooling

### **Why FastAPI?**
- **Async Support**: Native async/await for I/O operations
- **Type Safety**: Pydantic integration for data validation
- **Performance**: High-performance Python web framework
- **Documentation**: Auto-generated API docs

### **Why Celery?**
- **Background Processing**: Non-blocking job execution
- **Scalability**: Multiple worker processes
- **Reliability**: Task retry and error handling
- **Monitoring**: Built-in task monitoring and metrics

### **Why Redis?**
- **Speed**: In-memory storage for fast access
- **TTL Support**: Automatic expiration of old data
- **Message Broker**: Celery backend integration
- **Simplicity**: Easy setup and configuration

---

## 📝 **Usage Examples**

### **Creating a Job**
```typescript
const jobResult = await createJob();
if (jobResult) {
    const { jobId, filename } = jobResult;
    // Start polling for status updates
    pollJobStatus(jobId);
}
```

### **Checking Job Status**
```typescript
const { status, message } = await checkJobStatus(jobId);
if (status === 'completed') {
    // Show download options
    showDownloadLink(jobId);
}
```

### **Downloading Results**
```typescript
// Direct download
window.location.href = `${API_BASE_URL}/jobs/${jobId}/result`;

// Open in new tab
window.open(`${API_BASE_URL}/jobs/${jobId}/result`, '_blank');
```

This knowledge base covers all the essential aspects of the Sitemap to LLMS.txt project, including architecture decisions, implementation details, and technical considerations for future development.
