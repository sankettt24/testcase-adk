import re
from typing import Dict, List
from pathlib import Path


def extract_ui_elements(html_content: str, markdown_content: str = "") -> Dict:
    """Extract UI elements (buttons, inputs, dropdowns, links, etc.) from HTML/Markdown."""
    
    elements = {
        "buttons": [],
        "inputs": [],
        "dropdowns": [],
        "links": [],
        "forms": [],
        "headings": [],
        "images": [],
        "interactive_elements": []
    }
    
    # Extract buttons
    buttons = re.findall(r'<button[^>]*>([^<]+)</button>', html_content, re.IGNORECASE)
    elements["buttons"] = buttons[:10]  # limit to prevent noise
    
    # Extract input fields
    inputs = re.findall(r'<input[^>]*type=["\'](text|email|password|search|number)["\'][^>]*(?:name=["\']([\w-]+)["\'])?', 
                       html_content, re.IGNORECASE)
    elements["inputs"] = [{"type": inp[0], "name": inp[1]} for inp in inputs]
    
    # Extract select/dropdown menus
    dropdowns = re.findall(r'<select[^>]*(?:name=["\']([\w-]+)["\'])?', html_content, re.IGNORECASE)
    elements["dropdowns"] = dropdowns[:5]
    
    # Extract links
    links = re.findall(r'<a[^>]*href=["\']((?!javascript)[^\'"]+)["\'][^>]*>([^<]+)</a>', html_content, re.IGNORECASE)
    elements["links"] = [{"href": link[0], "text": link[1][:50]} for link in links[:10]]
    
    # Extract forms
    forms = re.findall(r'<form[^>]*(?:action=["\']([\w\-/.]+)["\'])?', html_content, re.IGNORECASE)
    elements["forms"] = forms[:5]
    
    # Extract headings
    headings = re.findall(r'<h[1-6][^>]*>([^<]+)</h[1-6]>', html_content, re.IGNORECASE)
    elements["headings"] = headings[:10]
    
    # Extract images with alt text
    images = re.findall(r'<img[^>]*alt=["\']([\w\s-]+)["\']', html_content, re.IGNORECASE)
    elements["images"] = images[:5]
    
    # Summary stats
    elements["summary"] = {
        "total_buttons": len(re.findall(r'<button', html_content, re.IGNORECASE)),
        "total_forms": len(re.findall(r'<form', html_content, re.IGNORECASE)),
        "total_links": len(re.findall(r'<a\s+href', html_content, re.IGNORECASE)),
        "has_search": bool(re.search(r'<input[^>]*type=["\']?search["\']?', html_content, re.IGNORECASE)),
        "has_cart": bool(re.search(r'(cart|basket|shopping|checkout)', html_content, re.IGNORECASE)),
        "has_login": bool(re.search(r'(login|signin|username|password)', html_content, re.IGNORECASE))
    }
    
    return elements


def extract_ui_from_crawled_files() -> Dict:
    """Extract UI elements from the latest crawled HTML/markdown files."""
    content_dir = Path(__file__).parent.parent / "crawled_content"
    
    if not content_dir.exists():
        return {"success": False, "error": "No crawled content found. Run crawl_website first."}
    
    markdown_files = list(content_dir.glob("*_markdown.md"))
    html_files = list(content_dir.glob("*_html.html"))
    
    if not markdown_files or not html_files:
        return {"success": False, "error": "No crawled content found. Run crawl_website first."}
    
    # Get the most recent files
    latest_md = max(markdown_files, key=lambda x: x.stat().st_mtime)
    latest_html = max(html_files, key=lambda x: x.stat().st_mtime)
    
    html_content = latest_html.read_text(encoding="utf-8")
    markdown_content = latest_md.read_text(encoding="utf-8")
    
    # Extract UI elements
    elements = extract_ui_elements(html_content, markdown_content)
    elements["source_html_file"] = str(latest_html)
    elements["source_markdown_file"] = str(latest_md)
    elements["success"] = True
    
    return elements
