import os
import requests
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Configuration constants
USER_AGENT = 'sitemap-to-llms/1.0 (+https://github.com/jeroensmink98/sitemap-to-llmstxt)'

class LLMSGenerator:
    def __init__(self):
        pass
    
    def validate_url(self, url):
        """Validate individual URL format"""
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def fetch_page_title(self, url):
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
    
    def generate_llms_content(self, domain, urls, batch_size, batch_delay, include_metadata):
        """Generate LLMS.txt content from URLs"""
        content_parts = []
        
        # Extract domain name for title
        parsed_domain = urlparse(domain)
        domain_name = parsed_domain.netloc.replace('www.', '')
        
        # Write header
        content_parts.append(f"# {domain_name}")
        content_parts.append("")
        content_parts.append(f"> Sitemap-generated content from {domain}")
        content_parts.append("")
        content_parts.append("This file contains all discoverable pages from the website's sitemap.")
        content_parts.append("")
        
        # Group URLs by type or create sections
        content_parts.append("## Pages")
        content_parts.append("")
        
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
                if not self.validate_url(url):
                    print(f"  Warning: Skipping invalid URL: {url}")
                    continue
                
                # Fetch title gracefully
                title, description = self.fetch_page_title(url)
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
                            content_parts.append(f"- [{title}]({url}): {description} | {' | '.join(metadata)}")
                        else:
                            content_parts.append(f"- [{title}]({url}): {' | '.join(metadata)}")
                    else:
                        # Include description if available
                        if description:
                            content_parts.append(f"- [{title}]({url}): {description}")
                        else:
                            content_parts.append(f"- [{title}]({url})")
                
                # No individual delays within batches - we'll delay between batches instead
            
            # Delay between batches (except after the last batch)
            if i + batch_size < len(urls):
                delay_seconds = batch_delay / 1000.0
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
                if not self.validate_url(url):
                    continue
                
                # Still try to get description even if title failed
                _, description = self.fetch_page_title(url)
                if description:
                    content_parts.append(f"- [{url}]({url}): {description}")
                else:
                    content_parts.append(f"- [{url}]({url})")
        
        # Add optional section for additional resources
        content_parts.append("")
        content_parts.append("## Optional")
        content_parts.append("")
        content_parts.append(f"- [Sitemap]({domain}/sitemap.xml): XML sitemap for search engines")
        content_parts.append(f"- [Robots]({domain}/robots.txt): Robots.txt file")
        
        print(f"Successfully processed {valid_urls} URLs with titles")
        
        return "\n".join(content_parts)
