# Sitemap to LLMS.txt API Backend

This backend provides a RESTful API that converts sitemaps to LLMS.txt format using background job processing. It wraps the existing CLI logic into a web service with job management capabilities.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Celery Queue  │    │   Redis Store   │
│   (Port 8000)   │◄──►│   (Worker)      │◄──►│   (Job Status)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
   │ API Routes  │       │ Background  │       │ Job Data    │
   │ & Models    │       │ Tasks       │       │ & Results   │
   └─────────────┘       └─────────────┘       └─────────────┘
```

### Components

- **FastAPI**: Web framework providing REST API endpoints
- **Celery**: Background task queue for processing sitemaps
- **Redis**: Message broker and job status storage
- **Services**: Business logic extracted from the original CLI script

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Redis server
- Docker (optional, for containerized deployment)

### Local Development

1. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

2. **Start Redis:**
   ```bash
   # macOS/Linux
   redis-server
   
   # Windows (WSL or Docker)
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. **Start Celery worker:**
   ```bash
   celery -A backend.celery_app worker --loglevel=info
   ```

4. **Run the API:**
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

1. **Start all services:**
   ```bash
   # From project root
   docker-compose -f docker/docker-compose.yml up -d
   ```

2. **Access the API:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health
   - Celery monitoring: http://localhost:5555

## 📚 API Endpoints

### 1. Create Job
```http
POST /api/v1/jobs
Content-Type: application/json

{
  "domain": "example.com",
  "output": "custom-filename.txt",  // Optional
  "batch_size": 10,                 // Default: 10
  "batch_delay": 1000,             // Default: 1000ms
  "include_metadata": false         // Default: false
}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "pending",
  "message": "Job created successfully"
}
```

### 2. Check Job Status
```http
GET /api/v1/jobs/{job_id}/status
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "progress": null,
  "message": "Processing 150 URLs...",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:05:00"
}
```

### 3. Download Result
```http
GET /api/v1/jobs/{job_id}/result
```

Returns the generated LLMS.txt file as a download.

### 4. Get Job Info
```http
GET /api/v1/jobs/{job_id}/info
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "output_file": "outputs/example-llms.txt",
  "url_count": 150,
  "download_url": "/api/v1/jobs/{job_id}/result"
}
```

### 5. List All Jobs
```http
GET /api/v1/jobs
```

Returns a list of all jobs with their current status.

## 🔄 Job Lifecycle

1. **PENDING**: Job created, waiting in queue
2. **PROCESSING**: Job is actively running
3. **COMPLETED**: Job finished successfully
4. **FAILED**: Job encountered an error

## 🏃‍♂️ Running the API

### Development Mode

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
celery -A backend.celery_app worker --loglevel=info

# Terminal 3: Run FastAPI
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Using gunicorn (recommended for production)
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or using uvicorn directly
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables

```bash
# Redis connection
REDIS_URL=redis://localhost:6379/0

# Python path
PYTHONPATH=/path/to/your/project

# Optional: Logging level
LOG_LEVEL=info
```

## 📁 Project Structure

```
backend/
├── __init__.py              # Package initialization
├── main.py                  # FastAPI application entry point
├── celery_app.py            # Celery configuration
├── models.py                # Pydantic data models
├── tasks.py                 # Background task definitions
├── api/                     # API route definitions
│   ├── __init__.py
│   └── routes.py           # HTTP endpoint handlers
└── services/                # Business logic services
    ├── __init__.py
    ├── sitemap_service.py   # Sitemap processing logic
    └── llms_generator.py    # LLMS.txt generation logic
```

## 🧪 Testing the API

### Using curl

1. **Create a job:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/jobs" \
        -H "Content-Type: application/json" \
        -d '{"domain": "example.com"}'
   ```

2. **Check status:**
   ```bash
   curl "http://localhost:8000/api/v1/jobs/{job_id}/status"
   ```

3. **Download result:**
   ```bash
   curl "http://localhost:8000/api/v1/jobs/{job_id}/result" -o result.txt
   ```

### Using the Interactive Docs

Visit http://localhost:8000/docs for the Swagger UI where you can:
- See all available endpoints
- Test the API directly in the browser
- View request/response schemas

## 🔍 Monitoring & Debugging

### Celery Flower

Access Celery Flower at http://localhost:5555 to:
- Monitor task execution
- View worker status
- Inspect task results
- Debug failed tasks

### Health Check

```bash
curl http://localhost:8000/health
```

Returns system health including Redis and Celery worker status.

### Logs

```bash
# View API logs
tail -f logs/api.log

# View Celery worker logs
tail -f logs/celery.log

# View all Docker logs
docker-compose -f docker/docker-compose.yml logs -f
```

## 🚨 Troubleshooting

### Common Issues

1. **Redis Connection Error:**
   - Ensure Redis is running: `redis-cli ping`
   - Check REDIS_URL environment variable

2. **Celery Worker Not Starting:**
   - Verify Redis is accessible
   - Check Python path includes backend directory

3. **Import Errors:**
   - Ensure PYTHONPATH is set correctly
   - Run from project root directory

4. **Port Already in Use:**
   - Change port: `--port 8001`
   - Kill existing process: `lsof -ti:8000 | xargs kill`

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug

# Run with verbose output
uvicorn backend.main:app --reload --log-level debug
```

## 🔧 Configuration

### Celery Settings

Key configuration in `celery_app.py`:
- Task timeout: 30 minutes
- Soft timeout: 25 minutes
- Result backend: Redis
- Task serialization: JSON

### Redis Settings

- Default connection: `redis://localhost:6379/0`
- Job status TTL: 1 hour (3600 seconds)
- Result data TTL: 1 hour

## 📈 Scaling

### Multiple Workers

```bash
# Start multiple Celery workers
celery -A backend.celery_app worker --loglevel=info --concurrency=4

# Or scale with Docker Compose
docker-compose -f docker/docker-compose.yml up --scale celery-worker=3
```

### Load Balancing

Use a reverse proxy (nginx, HAProxy) to distribute requests across multiple API instances.

## 🔒 Security Considerations

- **Input Validation**: All inputs are validated using Pydantic models
- **Rate Limiting**: Consider implementing rate limiting for production
- **Authentication**: Add authentication middleware for production use
- **CORS**: Configure CORS settings for your domain

## 📝 Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update this README for API changes
4. Use type hints and docstrings

## 📄 License

Same as the main project license.
