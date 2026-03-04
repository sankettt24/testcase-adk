import asyncio
import json


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
    """Synchronous wrapper for crawl_page."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(crawl_page(url))
