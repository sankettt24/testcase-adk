import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os


async def crawl_page(url: str):
    """Crawl a website and extract markdown content using Crawl4AI."""
    try:
        from crawl4ai import AsyncWebCrawler
        
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
        
        return {
            "success": True,
            "url": url,
            "markdown": result.markdown,
            "html": result.cleaned_html
        }
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": str(e)
        }


def crawl_page_sync(url: str):
    """Synchronous wrapper for crawl_page that handles nested event loops and saves output."""
    try:
        loop = asyncio.get_running_loop()
        # Loop is already running, use thread executor
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, crawl_page(url))
            result = future.result()
    except RuntimeError:
        # No running loop, safe to use get_event_loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(crawl_page(url))
    
    # Save output to files if successful
    if result.get("success"):
        # Create crawled_content directory
        output_dir = Path(__file__).parent.parent / "crawled_content"
        output_dir.mkdir(exist_ok=True)
        
        # Remove old files before creating new ones
        for old_file in output_dir.glob("*_markdown.md"):
            try:
                old_file.unlink()
            except:
                pass
        for old_file in output_dir.glob("*_html.html"):
            try:
                old_file.unlink()
            except:
                pass
        
        # Generate safe filename from URL
        safe_filename = url.replace("https://", "").replace("http://", "").replace("/", "_").replace("?", "_").replace("&", "_")[:60]
        
        # Save markdown
        markdown_file = output_dir / f"{safe_filename}_markdown.md"
        markdown_file.write_text(result.get("markdown", ""), encoding="utf-8")
        
        # Save HTML
        html_file = output_dir / f"{safe_filename}_html.html"
        html_file.write_text(result.get("html", ""), encoding="utf-8")
        
        # Add file paths to result
        result["markdown_file"] = str(markdown_file)
        result["html_file"] = str(html_file)
    
    return result


def get_latest_crawled_content() -> dict:
    """Get the latest crawled markdown and HTML files."""
    content_dir = Path(__file__).parent.parent / "crawled_content"
    
    if not content_dir.exists():
        return {"success": False, "error": "No crawled content found"}
    
    markdown_files = list(content_dir.glob("*_markdown.md"))
    html_files = list(content_dir.glob("*_html.html"))
    
    if not markdown_files or not html_files:
        return {"success": False, "error": "No crawled content found"}
    
    # Get the most recent files (by modification time)
    latest_md = max(markdown_files, key=lambda x: x.stat().st_mtime)
    latest_html = max(html_files, key=lambda x: x.stat().st_mtime)
    
    return {
        "success": True,
        "markdown_file": str(latest_md),
        "html_file": str(latest_html),
        "markdown_content": latest_md.read_text(encoding="utf-8"),
        "html_content": latest_html.read_text(encoding="utf-8")
    }
