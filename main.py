import os
import argparse
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
import time

# Configuration constants
USER_AGENT = 'sitemap-to-llms/1.0 (+https://github.com/jeroensmink98/sitemap-to-llmstxt)'

def validate_domain(domain):
    """Validate and normalize domain input"""
    if not domain:
        raise ValueError("Domain cannot be empty")
    
    # Remove whitespace
    domain = domain.strip()
    
    # Check if domain already contains protocol
    if domain.startswith(('http://', 'https://')):
        # Validate the full URL
        try:
            parsed = urlparse(domain)
            if not parsed.netloc:
                raise ValueError(f"Invalid URL format: {domain}")
            return domain
        except Exception as e:
            raise ValueError(f"Invalid URL format: {domain} - {str(e)}")
    
    # Validate domain format (basic regex)
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    if not re.match(domain_pattern, domain):
        raise ValueError(f"Invalid domain format: {domain}")
    
    # Add https:// protocol
    return f"https://{domain}"

def validate_output_file(output_path, domain=None):
    """Validate output file path and generate default if not provided"""
    if not output_path:
        if domain:
            # Generate default filename based on domain
            parsed_domain = urlparse(domain)
            domain_name = parsed_domain.netloc.replace('www.', '')
            # Remove any file extensions that might be in the domain
            domain_name = domain_name.split('.')[0]
            default_filename = f"{domain_name}-llms.txt"
            return default_filename
        else:
            return "llms.txt"
    
    # Check if directory exists and is writable
    output_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else "."
    if not os.access(output_dir, os.W_OK):
        raise ValueError(f"Output directory is not writable: {output_dir}")
    
    # Check file extension
    if not output_path.endswith(('.txt', '.md')):
        raise ValueError("Output file must have .txt or .md extension")
    
    return output_path

def validate_batch_size(batch_size):
    """Validate batch size parameter"""
    if batch_size < 1:
        raise ValueError("Batch size must be at least 1")
    if batch_size > 100:
        raise ValueError("Batch size cannot exceed 100 (to prevent overwhelming servers)")
    return batch_size

def validate_batch_delay(delay_ms):
    """Validate batch delay parameter"""
    if delay_ms < 0:
        raise ValueError("Batch delay cannot be negative")
    if delay_ms > 30000:
        raise ValueError("Batch delay cannot exceed 30 seconds (30000ms)")
    return delay_ms

def validate_url(url):
    """Validate individual URL format"""
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False

def validate_and_normalize_args(args):
    """Validate and normalize all command line arguments"""
    errors = []
    
    try:
        # Validate domain first (needed for output file validation)
        normalized_domain = validate_domain(args.domain)
    except ValueError as e:
        errors.append(f"Domain validation error: {str(e)}")
        normalized_domain = None
    
    try:
        # Validate output file (can now use normalized domain for default filename)
        normalized_output = validate_output_file(args.output, normalized_domain)
    except ValueError as e:
        errors.append(f"Output file validation error: {str(e)}")
        normalized_output = None
    
    try:
        # Validate batch size
        normalized_batch_size = validate_batch_size(args.batch_size)
    except ValueError as e:
        errors.append(f"Batch size validation error: {str(e)}")
        normalized_batch_size = None
    
    try:
        # Validate batch delay
        normalized_batch_delay = validate_batch_delay(args.batch_delay)
    except ValueError as e:
        errors.append(f"Batch delay validation error: {str(e)}")
        normalized_batch_delay = None
    
    # Include metadata is a boolean flag, no validation needed
    include_metadata = args.include_metadata
    
    # If any validation failed, raise comprehensive error
    if errors:
        error_message = "Validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        raise ValueError(error_message)
    
    return {
        'domain': normalized_domain,
        'output': normalized_output,
        'batch_size': normalized_batch_size,
        'batch_delay': normalized_batch_delay,
        'include_metadata': include_metadata
    }

def parse_sitemap_xml(sitemap_content):
    """Parse XML sitemap and extract URLs with metadata"""
    try:
        root = ET.fromstring(sitemap_content)
        
        # Handle sitemap index files
        if 'sitemapindex' in root.tag:
            sitemap_urls = []
            for sitemap in root.findall('.//{*}sitemap'):
                loc = sitemap.find('.//{*}loc')
                if loc is not None and loc.text:
                    url = loc.text.strip()
                    if validate_url(url):
                        sitemap_urls.append(url)
            return {'type': 'sitemap_index', 'urls': sitemap_urls}
        
        # Handle regular sitemap files
        elif 'urlset' in root.tag:
            urls = []
            for url_elem in root.findall('.//{*}url'):
                url_data = {}
                loc = url_elem.find('.//{*}loc')
                if loc is not None and loc.text:
                    url = loc.text.strip()
                    if validate_url(url):
                        url_data['url'] = url
                        
                        lastmod = url_elem.find('.//{*}lastmod')
                        if lastmod is not None and lastmod.text:
                            url_data['lastmod'] = lastmod.text.strip()
                        
                        changefreq = url_elem.find('.//{*}changefreq')
                        if changefreq is not None and changefreq.text:
                            url_data['changefreq'] = changefreq.text.strip()
                        
                        priority = url_elem.find('.//{*}priority')
                        if priority is not None and priority.text:
                            url_data['priority'] = priority.text.strip()
                        
                        urls.append(url_data)
            return {'type': 'urlset', 'urls': urls}
        
        else:
            return {'type': 'unknown', 'urls': []}
            
    except ET.ParseError:
        return {'type': 'parse_error', 'urls': []}

def parse_text_sitemap(content):
    """Parse text-based sitemap formats"""
    urls = []
    
    # Try to extract URLs using regex pattern
    url_pattern = r'https?://[^\s<>"\']+'
    found_urls = re.findall(url_pattern, content)
    
    if found_urls:
        for url in found_urls:
            url = url.strip()
            if validate_url(url):
                urls.append({'url': url})
        return {'type': 'text', 'urls': urls}
    
    return {'type': 'unknown', 'urls': []}

def fetch_sitemap(url):
    """Fetch sitemap from URL and return content"""
    try:
        headers = {
            'User-Agent': USER_AGENT
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching sitemap: {e}")
        return None

def fetch_page_title(url):
    """Fetch page title and meta description gracefully from a URL"""
    try:
        headers = {
            'User-Agent': USER_AGENT
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Check if content is HTML
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            # For non-HTML content, try to extract filename or use domain
            parsed_url = urlparse(url)
            path = parsed_url.path
            if path and path != '/':
                filename = os.path.basename(path)
                if filename:
                    return filename, None
            return parsed_url.netloc, None
        
        # Parse HTML to extract title and description
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get parsed URL for fallback purposes
        parsed_url = urlparse(url)
        domain_name = parsed_url.netloc
        
        # Extract title
        title = soup.find('title')
        title_text = None
        if title and title.text.strip():
            title_text = title.text.strip()
            # Remove extra whitespace and newlines
            title_text = ' '.join(title_text.split())
        else:
            # First fallback: try Open Graph title
            og_title = soup.find('meta', attrs={'property': 'og:title'})
            if og_title and og_title.get('content'):
                og_title_text = og_title.get('content').strip()
                og_title_text = ' '.join(og_title_text.split())
                title_text = og_title_text
            else:
                # Second fallback: try to get h1 or use domain name
                h1 = soup.find('h1')
                if h1 and h1.text.strip():
                    h1_text = h1.text.strip()
                    h1_text = ' '.join(h1_text.split())
                    title_text = h1_text
                else:
                    # Use domain name as final fallback
                    title_text = domain_name
        
        # Remove the old Open Graph fallback logic since it's now handled above
        
        # Extract meta description
        description = None
        
        # Try meta name="description" first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc.get('content').strip()
            description = ' '.join(description.split())  # Clean up whitespace
        
        # If no meta description, try og:description
        if not description:
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc and og_desc.get('content'):
                description = og_desc.get('content').strip()
                description = ' '.join(description.split())  # Clean up whitespace
        
        return title_text, description
                
    except requests.exceptions.Timeout:
        # Handle timeout specifically
        parsed_url = urlparse(url)
        return f"{parsed_url.netloc} (timeout)", None
    except requests.exceptions.RequestException:
        # Handle other request errors
        parsed_url = urlparse(url)
        return f"{parsed_url.netloc} (error)", None
    except Exception as e:
        # Gracefully handle any other errors and return domain name
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc, None
        except:
            return url, None

def discover_sitemaps(domain):
    """Discover sitemap locations for a domain"""
    sitemap_locations = []
    
    # Common sitemap locations
    common_paths = [
        '/sitemap.xml',
        '/sitemap_index.xml',
        '/sitemap/sitemap.xml',
        '/sitemap.txt',
        '/robots.txt'
    ]
    
    for path in common_paths:
        url = urljoin(domain, path)
        content = fetch_sitemap(url)
        if content:
            if path == '/robots.txt':
                # Extract sitemap URLs from robots.txt
                sitemap_lines = [line for line in content.split('\n') 
                               if line.lower().startswith('sitemap:')]
                for line in sitemap_lines:
                    sitemap_url = line.split(':', 1)[1].strip()
                    sitemap_locations.append(sitemap_url)
            else:
                sitemap_locations.append(url)
    
    return sitemap_locations

def extract_all_urls(domain):
    """Extract all URLs from all discovered sitemaps"""
    all_urls = []
    
    # Discover sitemaps
    sitemap_locations = discover_sitemaps(domain)
    
    if not sitemap_locations:
        print(f"No sitemaps found for {domain}")
        return []
    
    print(f"Found {len(sitemap_locations)} sitemap location(s)")
    
    for sitemap_url in sitemap_locations:
        print(f"Processing: {sitemap_url}")
        content = fetch_sitemap(sitemap_url)
        
        if not content:
            continue
        
        # Try to parse as XML first
        result = parse_sitemap_xml(content)
        
        if result['type'] == 'parse_error' or result['type'] == 'unknown':
            # Try as text format
            result = parse_text_sitemap(content)
        
        if result['urls']:
            if result['type'] == 'sitemap_index':
                # Recursively process sitemap index files
                for sub_sitemap_url in result['urls']:
                    sub_content = fetch_sitemap(sub_sitemap_url)
                    if sub_content:
                        sub_result = parse_sitemap_xml(sub_content)
                        if sub_result['urls']:
                            all_urls.extend(sub_result['urls'])
            else:
                all_urls.extend(result['urls'])
    
    # Remove duplicate URLs while preserving metadata
    seen_urls = set()
    unique_urls = []
    
    for url_data in all_urls:
        if isinstance(url_data, dict):
            url = url_data['url']
        else:
            url = url_data
            
        if url not in seen_urls:
            seen_urls.add(url)
            unique_urls.append(url_data)
    
    print(f"Removed {len(all_urls) - len(unique_urls)} duplicate URLs")
    
    return unique_urls

def main():
    parser = argparse.ArgumentParser(description="Convert sitemap.xml to LLMS.txt")
    parser.add_argument("domain", help="The URL of the domain to process")
    parser.add_argument("--output", "-o", help="Output file path (default: auto-generated based on domain)")
    parser.add_argument("--batch-size", "-b", type=int, default=10, help="Number of concurrent requests per batch (default: 10)")
    parser.add_argument("--batch-delay", "-d", type=int, default=1000, help="Delay between batches in milliseconds (default: 1000)")
    parser.add_argument("--include-metadata", action="store_true", help="Include sitemap metadata (lastmod, changefreq, priority) in output")
    
    args = parser.parse_args()
    
    try:
        # Validate and normalize all arguments
        validated_args = validate_and_normalize_args(args)
        
        domain = validated_args['domain']
        output_file = validated_args['output']
        batch_size = validated_args['batch_size']
        batch_delay_ms = validated_args['batch_delay']
        include_metadata = validated_args['include_metadata']
        
        print(f"Processing domain: {domain}")
        print(f"Output file: {output_file}")
        print(f"Batch size: {batch_size}, Delay between batches: {batch_delay_ms}ms")
        
        # Extract all URLs from sitemaps
        urls = extract_all_urls(domain)
        
        if not urls:
            print("No URLs found in any sitemaps")
            return
        
        print(f"Found {len(urls)} URLs")
        
        # Generate llms.txt format markdown
        with open(output_file, 'w', encoding='utf-8') as f:
            # Extract domain name for title
            parsed_domain = urlparse(domain)
            domain_name = parsed_domain.netloc.replace('www.', '')
            
            # Write header
            f.write(f"# {domain_name}\n\n")
            f.write(f"> Sitemap-generated content from {domain}\n\n")
            f.write("This file contains all discoverable pages from the website's sitemap.\n\n")
            
            # Group URLs by type or create sections
            f.write("## Pages\n\n")
            
            # Fetch titles in batches
            print("Fetching page titles in batches...")
            valid_urls = 0
            
            # Process URLs in batches
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(urls) + batch_size - 1) // batch_size
                
                print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} URLs)...")
                
                # Process current batch
                for j, url_data in enumerate(batch):
                    if isinstance(url_data, dict):
                        url = url_data['url']
                    else:
                        url = url_data
                    
                    # Validate URL before processing
                    if not validate_url(url):
                        print(f"  Warning: Skipping invalid URL: {url}")
                        continue
                    
                    # Fetch title gracefully
                    title, description = fetch_page_title(url)
                    global_index = i + j + 1
                    print(f"  [{global_index}/{len(urls)}] {title}")
                    
                    # Skip URLs that couldn't get a proper title
                    if title and title != url:
                        valid_urls += 1
                        
                        # Write URL with title, description, and optional metadata
                        if isinstance(url_data, dict) and include_metadata and any(key in url_data for key in ['lastmod', 'changefreq', 'priority']):
                            metadata = []
                            if 'lastmod' in url_data:
                                metadata.append(f"lastmod: {url_data['lastmod']}")
                            if 'changefreq' in url_data:
                                metadata.append(f"changefreq: {url_data['changefreq']}")
                            if 'priority' in url_data:
                                metadata.append(f"priority: {url_data['priority']}")
                            
                            # Include description if available
                            if description:
                                f.write(f"- [{title}]({url}): {description} | {' | '.join(metadata)}\n")
                            else:
                                f.write(f"- [{title}]({url}): {' | '.join(metadata)}\n")
                        else:
                            # Include description if available
                            if description:
                                f.write(f"- [{title}]({url}): {description}\n")
                            else:
                                f.write(f"- [{title}]({url})\n")
                    
                    # No individual delays within batches - we'll delay between batches instead
                
                # Delay between batches (except after the last batch)
                if i + batch_size < len(urls):
                    delay_seconds = batch_delay_ms / 1000.0
                    print(f"Waiting {delay_seconds:.1f}s before next batch...")
                    time.sleep(delay_seconds)
            
            if valid_urls == 0:
                print("Warning: No valid titles could be fetched. Writing URLs without titles.")
                # Fallback: write URLs without titles
                for url_data in urls:
                    if isinstance(url_data, dict):
                        url = url_data['url']
                    else:
                        url = url_data
                    
                    # Validate URL before processing
                    if not validate_url(url):
                        continue
                    
                    # Still try to get description even if title failed
                    _, description = fetch_page_title(url)
                    if description:
                        f.write(f"- [{url}]({url}): {description}\n")
                    else:
                        f.write(f"- [{url}]({url})\n")
            
            # Add optional section for additional resources
            f.write("\n## Optional\n\n")
            f.write(f"- [Sitemap]({domain}/sitemap.xml): XML sitemap for search engines\n")
            f.write(f"- [Robots]({domain}/robots.txt): Robots.txt file\n")
        
        print(f"llms.txt format file written to {output_file}")
        print(f"Successfully processed {valid_urls} URLs with titles")
        
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("\nUsage examples:")
        print("  python main.py example.com")
        print("  python main.py https://example.com --batch-size 20 --batch-delay 500")
        print("  python main.py example.com --output custom.md --batch-size 5 --batch-delay 2000")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()
