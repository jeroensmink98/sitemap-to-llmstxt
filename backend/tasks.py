from .celery_app import celery_app
from .services.sitemap_service import SitemapService
from .services.llms_generator import LLMSGenerator
import redis
import json
import os
import datetime
import glob

# Redis connection for job status updates
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

@celery_app.task(bind=True)
def process_sitemap_job(self, job_id: str, domain: str, output_filename: str, 
                        batch_size: int, batch_delay: int, include_metadata: bool):
    """Background task to process sitemap and generate LLMS.txt"""
    
    try:
        # Update job status to processing
        update_job_status(job_id, "processing", "Starting sitemap processing...")
        print(f"Job {job_id}: Starting processing for domain: {domain}")
        
        # Initialize services
        sitemap_service = SitemapService()
        llms_generator = LLMSGenerator()
        
        # Validate domain first
        try:
            validated_domain = sitemap_service.validate_domain(domain)
            print(f"Job {job_id}: Domain validated as: {validated_domain}")
        except ValueError as e:
            error_msg = f"Domain validation error: {str(e)}"
            print(f"Job {job_id}: {error_msg}")
            update_job_status(job_id, "failed", error_msg)
            return
        
        # Extract URLs from sitemap
        update_job_status(job_id, "processing", "Discovering sitemaps...")
        print(f"Job {job_id}: Discovering sitemaps for {validated_domain}")
        urls = sitemap_service.extract_all_urls(validated_domain)
        
        if not urls:
            error_msg = "No URLs found in any sitemaps"
            print(f"Job {job_id}: {error_msg}")
            update_job_status(job_id, "failed", error_msg)
            return
        
        print(f"Job {job_id}: Found {len(urls)} URLs to process")
        
        # Generate LLMS.txt content
        update_job_status(job_id, "processing", f"Processing {len(urls)} URLs...")
        content = llms_generator.generate_llms_content(
            validated_domain, urls, batch_size, batch_delay, include_metadata
        )
        
        # Save to file
        output_path = f"outputs/{output_filename}"
        os.makedirs("outputs", exist_ok=True)
        
        # Ensure the output directory exists and handle any potential conflicts
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Job {job_id}: File written to {output_path}")
        except OSError as e:
            error_msg = f"Failed to write output file: {str(e)}"
            print(f"Job {job_id}: {error_msg}")
            update_job_status(job_id, "failed", error_msg)
            return
        
        # Update job status to completed
        success_msg = f"Successfully generated {output_filename} with {len(urls)} URLs"
        print(f"Job {job_id}: {success_msg}")
        update_job_status(job_id, "completed", success_msg)
        
        # Store result path in Redis
        result_data = {
            "output_file": output_path,
            "url_count": len(urls),
            "status": "completed",
            "download_url": f"/api/v1/jobs/{job_id}/result"
        }
        redis_client.setex(f"job_result:{job_id}", 3600, json.dumps(result_data))
        print(f"Job {job_id}: Result data stored in Redis")
        
        # Clean up old files to prevent disk space issues
        cleanup_old_files()
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"Job {job_id}: {error_msg}")
        update_job_status(job_id, "failed", error_msg)
        raise

def update_job_status(job_id: str, status: str, message: str):
    """Update job status in Redis"""
    
    # Get existing job data
    existing_data = redis_client.get(f"job_status:{job_id}")
    if existing_data:
        existing_job = json.loads(existing_data)
        # Preserve existing fields and update status/message
        job_data = {
            **existing_job,
            "status": status,
            "message": message,
            "updated_at": datetime.datetime.utcnow().isoformat()
        }
    else:
        # Create new job data if none exists
        job_data = {
            "job_id": job_id,
            "status": status,
            "message": message,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "updated_at": datetime.datetime.utcnow().isoformat()
        }
    
    # Store updated job data
    redis_client.setex(f"job_status:{job_id}", 3600, json.dumps(job_data))
    
    # Debug logging
    print(f"Updated job {job_id} status to: {status} - {message}")

def cleanup_old_files():
    """Clean up old output files to prevent disk space issues"""
    try:
        outputs_dir = "outputs"
        if not os.path.exists(outputs_dir):
            return
        
        # Get current time
        now = datetime.datetime.utcnow()
        cutoff_time = now - datetime.timedelta(hours=24)  # Keep files for 24 hours
        
        # Find all llms.txt files
        pattern = os.path.join(outputs_dir, "*-llms.txt")
        files = glob.glob(pattern)
        
        cleaned_count = 0
        for file_path in files:
            try:
                # Get file modification time
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime < cutoff_time:
                    os.remove(file_path)
                    cleaned_count += 1
                    print(f"Cleaned up old file: {file_path}")
            except (OSError, ValueError) as e:
                print(f"Error cleaning up file {file_path}: {e}")
                continue
        
        if cleaned_count > 0:
            print(f"Cleanup completed: removed {cleaned_count} old files")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")