"""Playwright-based element extraction and interaction tool."""

import asyncio
import json
from playwright.async_api import async_playwright, Page
from typing import List, Dict, Any


async def extract_elements_with_locators(url: str, element_types: List[str] = None) -> Dict[str, Any]:
    """
    Use Playwright to dynamically extract elements with their XPath, CSS selectors, and attributes.
    This handles JavaScript-rendered content properly.
    
    Args:
        url: Website URL to crawl
        element_types: List of element types to extract (button, input, link, form, select)
    
    Returns:
        Dictionary with extracted elements and their locators
    """
    
    if element_types is None:
        element_types = ["button", "input", "link", "form", "select"]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to page
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait for page to settle
            await page.wait_for_load_state("networkidle")
            
            elements = {}
            
            # Extract buttons
            if "button" in element_types:
                elements["buttons"] = await _extract_buttons(page)
            
            # Extract inputs
            if "input" in element_types:
                elements["inputs"] = await _extract_inputs(page)
            
            # Extract links
            if "link" in element_types:
                elements["links"] = await _extract_links(page)
            
            # Extract forms
            if "form" in element_types:
                elements["forms"] = await _extract_forms(page)
            
            # Extract selects
            if "select" in element_types:
                elements["selects"] = await _extract_selects(page)
            
            return {
                "success": True,
                "url": url,
                "elements": elements,
                "element_count": sum(len(v) for v in elements.values())
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
        finally:
            await browser.close()


async def _extract_buttons(page: Page) -> List[Dict]:
    """Extract all buttons with locators."""
    buttons = []
    
    # Get all button elements
    button_handles = await page.query_selector_all("button, input[type='button'], input[type='submit']")
    
    for i, handle in enumerate(button_handles[:20]):  # Limit to 20
        try:
            locator = handle
            
            # Get XPath
            xpath = await page.evaluate("""
                el => {
                    const path = [];
                    let current = el;
                    while (current) {
                        let index = 0;
                        let sibling = current.previousElementSibling;
                        while (sibling) {
                            if (sibling.tagName === current.tagName) index++;
                            sibling = sibling.previousElementSibling;
                        }
                        path.unshift(`${current.tagName.toLowerCase()}[${index+1}]`);
                        current = current.parentElement;
                    }
                    return '/' + path.join('/');
                }
            """, handle)
            
            # Get attributes
            tag = await handle.evaluate("el => el.tagName.toLowerCase()")
            text = await handle.text_content()
            id_attr = await handle.get_attribute("id")
            name_attr = await handle.get_attribute("name")
            class_attr = await handle.get_attribute("class")
            type_attr = await handle.get_attribute("type")
            
            # Get CSS selector
            css_selector = await page.evaluate("""
                el => {
                    if (el.id) return '#' + el.id;
                    if (el.name) return `[name="${el.name}"]`;
                    if (el.className) return '.' + el.className.split(' ')[0];
                    return el.tagName.toLowerCase();
                }
            """, handle)
            
            buttons.append({
                "tag": tag,
                "text": text.strip() if text else "",
                "id": id_attr,
                "name": name_attr,
                "class": class_attr,
                "type": type_attr,
                "xpath": xpath,
                "css_selector": css_selector,
                "visible": await handle.is_visible()
            })
        except Exception as e:
            pass
    
    return buttons[:20]


async def _extract_inputs(page: Page) -> List[Dict]:
    """Extract all input fields with locators."""
    inputs = []
    
    input_handles = await page.query_selector_all("input:not([type='button']):not([type='submit']), textarea")
    
    for i, handle in enumerate(input_handles[:20]):
        try:
            tag = await handle.evaluate("el => el.tagName.toLowerCase()")
            type_attr = await handle.get_attribute("type")
            id_attr = await handle.get_attribute("id")
            name_attr = await handle.get_attribute("name")
            placeholder = await handle.get_attribute("placeholder")
            class_attr = await handle.get_attribute("class")
            
            # Get XPath
            xpath = await page.evaluate("""
                el => {
                    const path = [];
                    let current = el;
                    while (current) {
                        let index = 0;
                        let sibling = current.previousElementSibling;
                        while (sibling) {
                            if (sibling.tagName === current.tagName) index++;
                            sibling = sibling.previousElementSibling;
                        }
                        path.unshift(`${current.tagName.toLowerCase()}[${index+1}]`);
                        current = current.parentElement;
                    }
                    return '/' + path.join('/');
                }
            """, handle)
            
            # CSS selector
            css_selector = await page.evaluate("""
                el => {
                    if (el.id) return '#' + el.id;
                    if (el.name) return `[name="${el.name}"]`;
                    if (el.className) return '.' + el.className.split(' ')[0];
                    return el.tagName.toLowerCase();
                }
            """, handle)
            
            inputs.append({
                "tag": tag,
                "type": type_attr or "text",
                "id": id_attr,
                "name": name_attr,
                "placeholder": placeholder,
                "class": class_attr,
                "xpath": xpath,
                "css_selector": css_selector,
                "visible": await handle.is_visible()
            })
        except Exception as e:
            pass
    
    return inputs[:20]


async def _extract_links(page: Page) -> List[Dict]:
    """Extract all clickable links with locators."""
    links = []
    
    link_handles = await page.query_selector_all("a[href]")
    
    for handle in link_handles[:20]:
        try:
            href = await handle.get_attribute("href")
            text = await handle.text_content()
            id_attr = await handle.get_attribute("id")
            class_attr = await handle.get_attribute("class")
            
            xpath = await page.evaluate("""
                el => {
                    const path = [];
                    let current = el;
                    while (current) {
                        let index = 0;
                        let sibling = current.previousElementSibling;
                        while (sibling) {
                            if (sibling.tagName === current.tagName) index++;
                            sibling = sibling.previousElementSibling;
                        }
                        path.unshift(`${current.tagName.toLowerCase()}[${index+1}]`);
                        current = current.parentElement;
                    }
                    return '/' + path.join('/');
                }
            """, handle)
            
            css_selector = await page.evaluate("""
                el => {
                    if (el.id) return `a#${el.id}`;
                    if (el.className) return `a.${el.className.split(' ')[0]}`;
                    return 'a';
                }
            """, handle)
            
            links.append({
                "tag": "a",
                "text": text.strip() if text else "",
                "href": href,
                "id": id_attr,
                "class": class_attr,
                "xpath": xpath,
                "css_selector": css_selector,
                "visible": await handle.is_visible()
            })
        except Exception as e:
            pass
    
    return links[:20]


async def _extract_forms(page: Page) -> List[Dict]:
    """Extract all form elements with locators."""
    forms = []
    
    form_handles = await page.query_selector_all("form")
    
    for handle in form_handles[:10]:
        try:
            id_attr = await handle.get_attribute("id")
            name_attr = await handle.get_attribute("name")
            action = await handle.get_attribute("action")
            method = await handle.get_attribute("method")
            
            xpath = await page.evaluate("""
                el => {
                    const path = [];
                    let current = el;
                    while (current) {
                        let index = 0;
                        let sibling = current.previousElementSibling;
                        while (sibling) {
                            if (sibling.tagName === current.tagName) index++;
                            sibling = sibling.previousElementSibling;
                        }
                        path.unshift(`${current.tagName.toLowerCase()}[${index+1}]`);
                        current = current.parentElement;
                    }
                    return '/' + path.join('/');
                }
            """, handle)
            
            forms.append({
                "tag": "form",
                "id": id_attr,
                "name": name_attr,
                "action": action,
                "method": method or "GET",
                "xpath": xpath,
                "css_selector": f"form#{id_attr}" if id_attr else "form"
            })
        except Exception as e:
            pass
    
    return forms


async def _extract_selects(page: Page) -> List[Dict]:
    """Extract all select dropdowns with locators."""
    selects = []
    
    select_handles = await page.query_selector_all("select")
    
    for handle in select_handles[:20]:
        try:
            id_attr = await handle.get_attribute("id")
            name_attr = await handle.get_attribute("name")
            class_attr = await handle.get_attribute("class")
            
            # Get options
            options = await handle.evaluate("""
                el => {
                    return Array.from(el.options).map(opt => ({
                        value: opt.value,
                        text: opt.text
                    }));
                }
            """)
            
            xpath = await page.evaluate("""
                el => {
                    const path = [];
                    let current = el;
                    while (current) {
                        let index = 0;
                        let sibling = current.previousElementSibling;
                        while (sibling) {
                            if (sibling.tagName === current.tagName) index++;
                            sibling = sibling.previousElementSibling;
                        }
                        path.unshift(`${current.tagName.toLowerCase()}[${index+1}]`);
                        current = current.parentElement;
                    }
                    return '/' + path.join('/');
                }
            """, handle)
            
            selects.append({
                "tag": "select",
                "id": id_attr,
                "name": name_attr,
                "class": class_attr,
                "options": options[:10],  # Limit options shown
                "xpath": xpath,
                "css_selector": f"select#{id_attr}" if id_attr else f"select[name='{name_attr}']"
            })
        except Exception as e:
            pass
    
    return selects[:20]


def extract_elements_sync(url: str, element_types: List[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for extract_elements_with_locators."""
    try:
        loop = asyncio.get_running_loop()
        # If we're in a running loop, use a thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, extract_elements_with_locators(url, element_types))
            return future.result()
    except RuntimeError:
        # No running loop, safe to use asyncio.run
        return asyncio.run(extract_elements_with_locators(url, element_types))
