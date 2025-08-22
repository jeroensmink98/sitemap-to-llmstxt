# Sitemap to LLMS.txt

A simple CLI tool that converts existing sitemap.xml files to LLMS.txt format files, following the [llms.txt specification](https://llmstxt.org/).

## Features

- **Sitemap Discovery**: Automatically finds sitemaps from common locations
- **Multiple Format Support**: Handles XML sitemaps, sitemap indexes, and text-based sitemaps
- **Page Title Extraction**: Fetches actual page titles from each URL
- **Meta Description Extraction**: Extracts meta descriptions and Open Graph descriptions
- **Duplicate Removal**: Automatically removes duplicate URLs
- **Batch Processing**: Configurable batch sizes for faster processing
- **LLMS.txt Format**: Generates properly formatted markdown files for LLMs
- **Metadata Preservation**: Keeps sitemap metadata (lastmod, changefreq, priority)
- **Input Validation**: Comprehensive validation of domains, URLs, and command line arguments
- **Error Handling**: Graceful error handling with helpful error messages and usage examples

## Installation

```bash
# Install dependencies
uv sync
```

## Usage

### Basic Usage

```bash
python main.py example.com
```

This will:

1. Discover sitemaps for the domain
2. Extract all URLs
3. Fetch page titles
4. Generate a `example-llms.txt` file (automatically named based on domain)

### Advanced Usage

```bash
python main.py example.com --output custom-output.md --batch-size 15 --batch-delay 800
```

### Automatic Filename Generation

When no output file is specified, the tool automatically generates a filename based on the domain:

- `https://devopsfrontier.nl` → `devopsfrontier-llms.txt`
- `https://www.example.com` → `example-llms.txt`
- `https://subdomain.domain.org` → `domain-llms.txt`

The tool removes:

- Protocol (https://, http://)
- www prefix
- File extensions
- Adds "-llms.txt" suffix

### Command Line Options

| Option               | Short | Description                             | Default        |
| -------------------- | ----- | --------------------------------------- | -------------- |
| `--output`           | `-o`  | Output file path                        | Auto-generated |
| `--batch-size`       | `-b`  | Number of concurrent requests per batch | `10`           |
| `--batch-delay`      | `-d`  | Delay between batches in milliseconds   | `1000`         |
| `--include-metadata` |       | Include sitemap metadata in output      | `False`        |

**Note**: The `--include-metadata` flag adds sitemap metadata (lastmod, changefreq, priority) to the output. This is not part of the [llms.txt specification](https://llmstxt.org/) but can be useful for internal documentation purposes.

### Input Validation

The tool performs comprehensive validation of all inputs:

- **Domain Validation**: Checks domain format, automatically adds HTTPS protocol
- **URL Validation**: Validates all URLs found in sitemaps before processing
- **Output File Validation**: Ensures output directory is writable and file has correct extension
- **Batch Parameters**: Validates batch size (1-100) and delay (0-30000ms)

### Error Handling

The tool provides clear error messages and helpful usage examples:

```bash
# Invalid domain format
python main.py "invalid domain"
# Error: Domain validation error: Invalid domain format: invalid domain

# Invalid output file
python main.py example.com --output /invalid/path/file.txt
# Error: Output file validation error: Output directory is not writable: /invalid/path

# Invalid batch size
python main.py example.com --batch-size 0
# Error: Batch size validation error: Batch size must be at least 1
```

### Performance Examples

**Fast Processing (Large batches, short delays):**

```bash
python main.py example.com --batch-size 20 --batch-delay 500
```

**Conservative Processing (Small batches, longer delays):**

```bash
python main.py example.com --batch-size 5 --batch-delay 2000
```

**Custom Output File:**

```bash
python main.py example.com --output my-site-llms.txt
```

**Include Sitemap Metadata (for internal use):**

```bash
python main.py example.com --include-metadata
```

**Standard llms.txt Format (default, follows specification):**

```bash
python main.py example.com
```

## How It Works

1. **Sitemap Discovery**: Checks common locations like `/sitemap.xml`, `/robots.txt`, etc.
2. **URL Extraction**: Parses XML and text-based sitemaps
3. **Deduplication**: Removes duplicate URLs while preserving metadata
4. **Title Fetching**: Processes URLs in configurable batches to fetch page titles
5. **LLMS.txt Generation**: Creates properly formatted markdown following the specification

## Output Format

The generated file follows the [llms.txt specification](https://llmstxt.org/):

```markdown
# example.com

> Sitemap-generated content from https://example.com

This file contains all discoverable pages from the website's sitemap.

## Pages

- [Homepage](https://example.com/): Welcome to our website - discover amazing content and services | lastmod: 2024-01-01 | changefreq: daily
- [About Us](https://example.com/about): Learn more about our company, mission, and values | lastmod: 2024-01-15
- [Contact](https://example.com/contact): Get in touch with our team for support and inquiries | priority: 0.8

## Optional

- [Sitemap](https://example.com/sitemap.xml): XML sitemap for search engines
- [Robots](https://example.com/robots.txt): Robots.txt file
```

**Note**: Meta descriptions are automatically extracted from `<meta name="description">` and `<meta property="og:description">` tags and included after each link to provide context for LLMs.

## Dependencies

- `requests`: HTTP requests for fetching sitemaps and pages
- `beautifulsoup4`: HTML parsing for extracting page titles
- `lxml`: XML parsing (included with beautifulsoup4)

## Error Handling

The tool gracefully handles:

- Network timeouts and connection errors
- Invalid XML sitemaps
- Non-HTML content
- Missing page titles (falls back to domain names)
- Server errors (continues processing other URLs)

## Server Considerations

- **Batch Processing**: Configurable batch sizes prevent overwhelming servers
- **Delays**: Configurable delays between batches respect server capacity
- **User-Agent**: Uses a descriptive user agent `sitemap-to-llms/1.0` for transparency
- **Timeout**: 10-second timeout per request to prevent hanging
- **Respectful**: Follows robots.txt and implements proper delays

## Contributing

Feel free to submit issues and enhancement requests!
