import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import re

# Configuration constants
USER_AGENT = 'sitemap-to-llms/1.0 (+https://github.com/jeroensmink98/sitemap-to-llmstxt)'

class SitemapService:
    def __init__(self):
        pass
    
    def validate_domain(self, domain):
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
    
    def validate_url(self, url):
        """Validate individual URL format"""
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def parse_sitemap_xml(self, sitemap_content):
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
                        if self.validate_url(url):
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
                        if self.validate_url(url):
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
    
    def parse_text_sitemap(self, content):
        """Parse text-based sitemap formats"""
        urls = []
        
        # Try to extract URLs using regex pattern
        url_pattern = r'https?://[^\s<>"\']+'
        found_urls = re.findall(url_pattern, content)
        
        if found_urls:
            for url in found_urls:
                url = url.strip()
                if self.validate_url(url):
                    urls.append({'url': url})
            return {'type': 'text', 'urls': urls}
        
        return {'type': 'unknown', 'urls': []}
    
    def fetch_sitemap(self, url):
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
    
    def discover_sitemaps(self, domain):
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
            content = self.fetch_sitemap(url)
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
    
    def extract_all_urls(self, domain):
        """Extract all URLs from all discovered sitemaps"""
        all_urls = []
        
        # Discover sitemaps
        sitemap_locations = self.discover_sitemaps(domain)
        
        if not sitemap_locations:
            print(f"No sitemaps found for {domain}")
            return []
        
        print(f"Found {len(sitemap_locations)} sitemap location(s)")
        
        for sitemap_url in sitemap_locations:
            print(f"Processing: {sitemap_url}")
            content = self.fetch_sitemap(sitemap_url)
            
            if not content:
                continue
            
            # Try to parse as XML first
            result = self.parse_sitemap_xml(content)
            
            if result['type'] == 'parse_error' or result['type'] == 'unknown':
                # Try as text format
                result = self.parse_text_sitemap(content)
            
            if result['urls']:
                if result['type'] == 'sitemap_index':
                    # Recursively process sitemap index files
                    for sub_sitemap_url in result['urls']:
                        sub_content = self.fetch_sitemap(sub_sitemap_url)
                        if sub_content:
                            sub_result = self.parse_sitemap_xml(sub_content)
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
