from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from ..models import JobRequest, JobResponse, JobStatusResponse, JobResultResponse
from ..tasks import process_sitemap_job
import redis
import json
import os
import uuid
import datetime

router = APIRouter()
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

@router.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    try:
        # Check Redis connection
        redis_client.ping()
        return {"status": "healthy", "redis": "connected", "timestamp": datetime.datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@router.post("/jobs", response_model=JobResponse)
async def create_job(request: JobRequest):
    """Create a new sitemap processing job"""
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Generate output filename if not provided
    if not request.output:
        domain_name = request.domain.replace("https://", "").replace("http://", "").replace("www.", "")
        # Remove any file extensions that might be in the domain
        domain_name = domain_name.split('.')[0]
        # Add timestamp and job ID for uniqueness to prevent file collisions
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        request.output = f"{domain_name}-{timestamp}-{job_id[:8]}-llms.txt"
        print(f"Generated unique filename: {request.output} for job {job_id}")
    else:
        print(f"Using custom filename: {request.output} for job {job_id}")
    
    # Store initial job status
    job_data = {
        "job_id": job_id,
        "status": "pending",
        "message": "Job created, waiting to be processed",
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat()
    }
    
    redis_client.setex(f"job_status:{job_id}", 3600, json.dumps(job_data))
    
    # Start background task
    process_sitemap_job.delay(
        job_id, 
        request.domain, 
        request.output,
        request.batch_size,
        request.batch_delay,
        request.include_metadata
    )
    
    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Job created successfully",
        output=request.output
    )

@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of a job"""
    
    job_data = redis_client.get(f"job_status:{job_id}")
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(**json.loads(job_data))

@router.get("/jobs/{job_id}/result")
async def get_job_result(job_id: str):
    """Download the generated LLMS.txt file"""
    
    # Check if job is completed
    job_data = redis_client.get(f"job_status:{job_id}")
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_status = json.loads(job_data)
    if job_status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    # Get result data
    result_data = redis_client.get(f"job_result:{job_id}")
    if not result_data:
        raise HTTPException(status_code=404, detail="Job result not found")
    
    result = json.loads(result_data)
    output_file = result["output_file"]
    
    if not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        output_file,
        media_type="text/plain",
        filename=os.path.basename(output_file)
    )

@router.get("/jobs/{job_id}/info", response_model=JobResultResponse)
async def get_job_info(job_id: str):
    """Get job result information (without downloading the file)"""
    
    # Check if job is completed
    job_data = redis_client.get(f"job_status:{job_id}")
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_status = json.loads(job_data)
    if job_status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    # Get result data
    result_data = redis_client.get(f"job_result:{job_id}")
    if not result_data:
        raise HTTPException(status_code=404, detail="Job result not found")
    
    result = json.loads(result_data)
    
    return JobResultResponse(
        job_id=job_id,
        status=job_status["status"],
        output_file=result["output_file"],
        url_count=result["url_count"],
        download_url=result["download_url"]
    )

@router.get("/jobs")
async def list_jobs():
    """List all jobs (for monitoring purposes)"""
    
    # Get all job status keys
    job_keys = redis_client.keys("job_status:*")
    jobs = []
    
    for key in job_keys:
        job_data = redis_client.get(key)
        if job_data:
            jobs.append(json.loads(job_data))
    
    return {"jobs": jobs}