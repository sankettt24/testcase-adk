"""Test Case Generation Agent using Google ADK with Web Crawling."""

import asyncio
import json
import sys
import os
import re
from pathlib import Path
from google.adk.agents import Agent

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.crawl_tool import crawl_page_sync
from tools.ui_extractor import extract_ui_elements
from tools.ui_graph_builder import build_ui_graph, build_complete_ui_flow
from tools.playwright_extractor import extract_elements_sync
from tools.test_script_generator import generate_playwright_test_script, generate_selenium_test_script


# Tool 1: Parse User Story
def parse_user_story(story: str) -> dict:
    if not story or not story.strip():
        return {
            "status": "error",
            "error_message": "User story text cannot be empty.",
        }

    story = story.strip()
    result = {
        "status": "success",
        "original_story": story,
        "actor": "Unknown",
        "action": "Unknown",
        "goal": "Unknown",
        "notes": "Components extracted. Use generate_test_cases to produce test cases.",
    }

    lower = story.lower()

    if "as a" in lower or "as an" in lower:
        try:
            start = lower.find("as a")
            if start == -1:
                start = lower.find("as an")
                actor_prefix_len = 6
            else:
                actor_prefix_len = 5

            actor_start = start + actor_prefix_len
            want_idx = lower.find("i want", actor_start)
            if want_idx != -1:
                result["actor"] = story[actor_start:want_idx].strip().rstrip(",")

            action_start = want_idx + 7
            so_that_idx = lower.find("so that", action_start)
            if so_that_idx != -1:
                result["action"] = story[action_start:so_that_idx].strip().rstrip(",")
                result["goal"] = story[so_that_idx + 8:].strip().rstrip(".")
            else:
                result["action"] = story[action_start:].strip().rstrip(".")

        except Exception:
            result["notes"] = (
                "Could not fully parse story structure. "
                "Proceeding with full text for test case generation."
            )
    else:
        result["notes"] = (
            "Story does not follow the 'As a ... I want ... so that ...' format. "
            "Proceeding with full text for test case generation."
        )

    return result


# Tool 2: Generate Test Cases
def generate_test_cases(story: str, test_types: str = "positive,negative,edge") -> dict:
    if not story or not story.strip():
        return {
            "status": "error",
            "error_message": "User story text cannot be empty.",
        }

    requested_types = [t.strip().lower() for t in test_types.split(",")]
    valid_types = {"positive", "negative", "edge"}
    invalid = set(requested_types) - valid_types
    
    if invalid:
        return {
            "status": "error",
            "error_message": (
                f"Invalid test types: {invalid}. "
                f"Allowed values are: {valid_types}"
            ),
        }

    test_cases = []
    counter = 1

    type_templates = {
        "positive": {
            "suffix": "Happy Path",
            "priority": "high",
            "description": "Valid inputs and expected successful outcome",
        },
        "negative": {
            "suffix": "Error Handling",
            "priority": "high",
            "description": "Invalid inputs or failure conditions",
        },
        "edge": {
            "suffix": "Edge Case",
            "priority": "medium",
            "description": "Boundary conditions and unusual but valid scenarios",
        },
    }

    # Extract key info from story for better test cases
    story_lower = story.lower()
    
    for t in requested_types:
        tmpl = type_templates[t]
        
        # Generate context-specific test cases
        if t == "positive":
            test_cases.append({
                "id": f"TC-{counter:03d}",
                "title": f"[{tmpl['suffix']}] User successfully performs desired action with valid inputs",
                "type": t,
                "description": tmpl["description"],
                "preconditions": "User is authenticated and on the relevant page with valid permissions",
                "steps": [
                    "1. Locate and open the feature/module mentioned in the story",
                    "2. Provide valid input data as described in the story",
                    "3. Execute the desired action",
                    "4. Verify system processes the request",
                    "5. Confirm the expected outcome is achieved",
                ],
                "expected_result": "Action completes successfully; system provides confirmation; data is correctly processed and returned",
                "priority": tmpl["priority"],
            })
        elif t == "negative":
            test_cases.append({
                "id": f"TC-{counter:03d}",
                "title": f"[{tmpl['suffix']}] System properly handles error conditions and invalid inputs",
                "type": t,
                "description": tmpl["description"],
                "preconditions": "User is on the relevant page",
                "steps": [
                    "1. Attempt to perform action with invalid/missing inputs",
                    "2. Try with null, empty, or malformed data",
                    "3. Attempt with unauthorized access if applicable",
                    "4. Trigger error conditions (timeout, system unavailable, etc.)",
                    "5. Observe system response",
                ],
                "expected_result": "System displays appropriate error message; request is rejected safely; no data corruption occurs; user is guided to correct input",
                "priority": tmpl["priority"],
            })
        else:  # edge case
            test_cases.append({
                "id": f"TC-{counter:03d}",
                "title": f"[{tmpl['suffix']}] System handles boundary conditions and unusual valid scenarios",
                "type": t,
                "description": tmpl["description"],
                "preconditions": "User is on the relevant page with valid permissions",
                "steps": [
                    "1. Test with minimum allowed values/inputs",
                    "2. Test with maximum allowed values/inputs",
                    "3. Test with special characters and edge values",
                    "4. Test with concurrent requests if applicable",
                    "5. Test with very long or very short inputs",
                ],
                "expected_result": "System processes edge cases correctly; maintains data integrity; responds within acceptable time limits; handles limits gracefully",
                "priority": tmpl["priority"],
            })
        counter += 1

    return {
        "status": "success",
        "story": story,
        "total_test_cases": len(test_cases),
        "test_cases": test_cases,
    }


# Tool 3: Format Test Cases as Markdown
def format_test_cases_as_markdown(test_cases_json: str) -> dict:
    if not test_cases_json or not test_cases_json.strip():
        return {
            "status": "error",
            "error_message": "test_cases_json cannot be empty.",
        }

    try:
        data = json.loads(test_cases_json)
        if isinstance(data, dict):
            test_cases = data.get("test_cases", [])
            story = data.get("story", "")
        elif isinstance(data, list):
            test_cases = data
            story = ""
        else:
            return {
                "status": "error",
                "error_message": "Invalid JSON format. Expected a list or object with 'test_cases' key.",
            }
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error_message": f"Failed to parse JSON: {str(e)}",
        }

    if not test_cases:
        return {
            "status": "error",
            "error_message": "No test cases found in the provided JSON.",
        }

    lines = []
    lines.append("# Test Cases Report")
    lines.append("")
    if story:
        lines.append(f"> **User Story:** {story}")
        lines.append("")

    lines.append(f"**Total Test Cases:** {len(test_cases)}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| ID | Title | Type | Priority |")
    lines.append("|----|-------|------|----------|")
    for tc in test_cases:
        tc_id = tc.get("id", "N/A")
        title = tc.get("title", "N/A")
        tc_type = tc.get("type", "N/A")
        priority = tc.get("priority", "N/A")
        lines.append(f"| {tc_id} | {title} | {tc_type} | {priority} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Detailed Test Cases")
    lines.append("")

    type_icons = {"positive": "✅", "negative": "❌", "edge": "⚠️"}

    for tc in test_cases:
        tc_id = tc.get("id", "N/A")
        title = tc.get("title", "N/A")
        tc_type = tc.get("type", "N/A")
        icon = type_icons.get(tc_type, "🔹")
        priority = tc.get("priority", "N/A")
        preconditions = tc.get("preconditions", "N/A")
        steps = tc.get("steps", [])
        expected = tc.get("expected_result", "N/A")

        lines.append(f"### {icon} {tc_id}: {title}")
        lines.append("")
        lines.append(f"- **Type:** `{tc_type}`")
        lines.append(f"- **Priority:** `{priority}`")
        lines.append(f"- **Preconditions:** {preconditions}")
        lines.append("")
        lines.append("**Test Steps:**")
        lines.append("")
        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")
        lines.append(f"**Expected Result:** {expected}")
        lines.append("")
        lines.append("---")
        lines.append("")

    markdown_output = "\n".join(lines)

    return {
        "status": "success",
        "markdown": markdown_output,
        "total_test_cases": len(test_cases),
    }


# Tool 4: Crawl Website
async def crawl_website(url: str) -> dict:
    """Crawl a website and extract content using Crawl4AI."""
    # Run sync wrapper in thread to avoid nested event-loop errors with ADK
    result = await asyncio.to_thread(crawl_page_sync, url)
    return {
        "success": result.get("success"),
        "url": url,
        "preview": result.get("markdown", "")[:1000] if result.get("success") else None,
        "has_html": bool(result.get("html")),
        "markdown_file": result.get("markdown_file"),
        "html_file": result.get("html_file"),
        "error": result.get("error")
    }


# Tool 5: Extract UI Elements
def extract_ui_elements_tool(html_content: str) -> dict:
    """Extract UI elements from HTML content."""
    if not html_content:
        return {"error": "HTML content is empty", "elements": {}}
    
    elements = extract_ui_elements(html_content)
    return {
        "buttons": elements.get("buttons", [])[:5],
        "inputs": elements.get("inputs", [])[:3],
        "dropdowns": elements.get("dropdowns", [])[:3],
        "links": elements.get("links", [])[:5],
        "forms": elements.get("forms", []),
        "summary": elements.get("summary", {})
    }


# Tool 6: Build UI Action Graph
def build_ui_action_graph(html_content: str) -> dict:
    """Build UI action graph from HTML content."""
    if not html_content:
        return {"error": "HTML content is empty", "graph": {}}
    
    elements = extract_ui_elements(html_content)
    graph = build_ui_graph(elements)
    page_type = graph.get("page_type")
    flows = build_complete_ui_flow(page_type, elements)
    
    return {
        "page_type": page_type,
        "available_actions": graph.get("available_actions", []),
        "user_flows": graph.get("user_flows", []),
        "example_flows": [flow["step"] for flow in flows[:3]]
    }


# Tool 7: Extract UI Elements from Crawled Content
def extract_ui_from_crawled() -> dict:
    """Extract UI elements from the latest crawled HTML/markdown files."""
    from tools.ui_extractor import extract_ui_from_crawled_files
    
    result = extract_ui_from_crawled_files()
    
    if not result.get("success"):
        return {"error": result.get("error"), "elements": {}}
    
    return {
        "success": True,
        "source_html_file": result.get("source_html_file"),
        "source_markdown_file": result.get("source_markdown_file"),
        "buttons": result.get("buttons", [])[:5],
        "inputs": result.get("inputs", [])[:3],
        "dropdowns": result.get("dropdowns", [])[:3],
        "links": result.get("links", [])[:5],
        "forms": result.get("forms", []),
        "summary": result.get("summary", {})
    }


# Tool 8: Build Complete UI Flow from Crawled Content
def build_ui_flow_from_crawled() -> dict:
    """Build complete UI action graph and flows from the latest crawled content."""
    from tools.ui_graph_builder import build_complete_ui_flow_from_crawled
    
    result = build_complete_ui_flow_from_crawled()
    
    if not result.get("success"):
        return {"error": result.get("error"), "graph": {}}
    
    return {
        "success": True,
        "source_html_file": result.get("source_html_file"),
        "source_markdown_file": result.get("source_markdown_file"),
        "page_type": result.get("ui_graph", {}).get("page_type"),
        "available_actions": result.get("ui_graph", {}).get("available_actions", []),
        "user_flows": result.get("user_flows", []),
        "interaction_patterns": result.get("ui_graph", {}).get("interaction_patterns", [])
    }


# Tool 9: Generate Test Cases with Website Context
async def generate_test_cases_with_context(user_story: str, website_url: str = None, test_types: str = "positive,negative,edge"):
    """Generate test cases using user story AND actual website HTML/Markdown content."""
    
    if not user_story or not user_story.strip():
        return {"status": "error", "error_message": "User story cannot be empty"}
    
    # Step 1: Check if website was already crawled, if URL provided crawl it
    if website_url and website_url.strip():
        crawl_result = await crawl_website(website_url)
        if not crawl_result.get("success"):
            return {"status": "error", "error_message": f"Failed to crawl website: {crawl_result.get('error')}"}
    
    # Step 2: Read the saved HTML and Markdown files (don't crawl again)
    from pathlib import Path
    content_dir = Path(__file__).parent.parent / "crawled_content"
    
    if not content_dir.exists():
        return {"status": "error", "error_message": "No crawled content found. Please crawl a website first."}
    
    markdown_files = list(content_dir.glob("*_markdown.md"))
    html_files = list(content_dir.glob("*_html.html"))
    
    if not markdown_files or not html_files:
        return {"status": "error", "error_message": "No crawled content found. Please crawl a website first."}
    
    # Get the latest files
    latest_md = max(markdown_files, key=lambda x: x.stat().st_mtime)
    latest_html = max(html_files, key=lambda x: x.stat().st_mtime)
    
    html_content = latest_html.read_text(encoding="utf-8")
    markdown_content = latest_md.read_text(encoding="utf-8")
    
    # Step 3: Extract key information from HTML and Markdown
    ui_elements = extract_ui_elements(html_content, markdown_content)
    
    # Step 4: Build detailed context from actual website content
    context_info = {
        "user_story": user_story,
        "website_url": website_url or "Unknown",
        "html_file": str(latest_html),
        "markdown_file": str(latest_md),
        "page_summary": markdown_content[:2000],  # First 2000 chars of markdown
        "buttons_found": ui_elements.get("buttons", []),
        "inputs_found": ui_elements.get("inputs", []),
        "forms_found": ui_elements.get("forms", []),
        "links_found": [l.get("text", "") for l in ui_elements.get("links", [])[:5]],
        "page_summary_text": markdown_content[:1000]
    }
    
    # Step 5: Create context-aware prompt that references actual page content
    detailed_prompt = f"""You are a QA expert. Generate SPECIFIC and REALISTIC test cases.

USER STORY: {user_story}

ACTUAL WEBSITE CONTENT (from crawled page):
{markdown_content[:3000]}

DETECTED UI ELEMENTS ON THIS PAGE:
- Buttons: {context_info['buttons_found']}
- Input Fields: {context_info['inputs_found']}
- Forms: {context_info['forms_found']}
- Links: {context_info['links_found']}

INSTRUCTIONS:
1. Generate test cases SPECIFIC to this user story
2. Reference the actual UI elements found above
3. Use the page content to create realistic scenarios
4. If ZIP code input mentioned in story, test that specific field
5. If store selection mentioned, reference the actual store elements
6. Make test steps concrete (e.g., "Enter 10001 in the ZIP code field" not generic actions)
7. Include expected results based on what the website offers

Generate {test_types} test cases with the format:
- Test ID: TC-XXX
- Title: [What is being tested]
- Type: {test_types}
- Steps: Numbered, specific steps using actual page elements
- Expected Result: Based on website functionality
"""
    
    # Step 6: Generate test cases using the detailed context
    test_result = generate_test_cases(detailed_prompt, test_types)
    
    if test_result.get("status") == "error":
        return test_result
    
    # Step 7: Add context metadata
    test_result["generation_method"] = "Story + HTML/Markdown Context (No re-crawl)"
    test_result["source_files"] = {
        "html_file": str(latest_html),
        "markdown_file": str(latest_md),
        "ui_elements_analyzed": {
            "buttons": len(context_info['buttons_found']),
            "inputs": len(context_info['inputs_found']),
            "forms": len(context_info['forms_found']),
            "links": len(context_info['links_found'])
        }
    }
    
    return test_result


# Tool 10: Get Element Details (XPath, ID, Tag, Name, etc.)
def get_element_details(element_type: str = "button") -> dict:
    """Extract detailed element information (XPath, ID, tag, name, class) from HTML file."""
    
    from pathlib import Path
    content_dir = Path(__file__).parent.parent / "crawled_content"
    
    if not content_dir.exists():
        return {"status": "error", "error_message": "No crawled content found. Please crawl a website first."}
    
    html_files = list(content_dir.glob("*_html.html"))
    
    if not html_files:
        return {"status": "error", "error_message": "No HTML files found in crawled_content"}
    
    # Get the latest HTML file
    latest_html = max(html_files, key=lambda x: x.stat().st_mtime)
    html_content = latest_html.read_text(encoding="utf-8")
    
    elements = []
    
    # Parse different element types
    if element_type.lower() == "button":
        # Button elements
        button_pattern = r'<button[^>]*>(.*?)</button>'
        for match in re.finditer(button_pattern, html_content, re.IGNORECASE | re.DOTALL):
            button_html = match.group(0)
            elements.append(_extract_element_info(button_html, "button", html_content))
        
        # Input type="button"
        input_btn_pattern = r'<input[^>]*type=["\']button["\'][^>]*>'
        for match in re.finditer(input_btn_pattern, html_content, re.IGNORECASE):
            input_html = match.group(0)
            elements.append(_extract_element_info(input_html, "input", html_content))
    
    elif element_type.lower() == "input":
        # Input elements
        input_pattern = r'<input[^>]*>'
        for match in re.finditer(input_pattern, html_content, re.IGNORECASE):
            input_html = match.group(0)
            elements.append(_extract_element_info(input_html, "input", html_content))
    
    elif element_type.lower() == "form":
        # Form elements
        form_pattern = r'<form[^>]*>.*?</form>'
        for match in re.finditer(form_pattern, html_content, re.IGNORECASE | re.DOTALL):
            form_html = match.group(0)[:200]  # Limit size
            elements.append(_extract_element_info(form_html, "form", html_content))
    
    elif element_type.lower() == "link" or element_type.lower() == "a":
        # Link/Anchor elements
        link_pattern = r'<a[^>]*>(.*?)</a>'
        for match in re.finditer(link_pattern, html_content, re.IGNORECASE):
            link_html = match.group(0)
            elements.append(_extract_element_info(link_html, "a", html_content))
    
    else:
        return {"status": "error", "error_message": f"Element type '{element_type}' not supported. Use: button, input, form, link"}
    
    return {
        "status": "success",
        "element_type": element_type,
        "html_file": str(latest_html),
        "total_found": len(elements),
        "elements": elements[:20]  # Limit to first 20
    }


def _extract_element_info(element_html: str, tag_name: str, full_html: str) -> dict:
    """Extract XPath, ID, name, class, and other attributes from an element."""
    
    # Extract attributes
    id_match = re.search(r'id=["\']([^"\']*)["\']', element_html, re.IGNORECASE)
    name_match = re.search(r'name=["\']([^"\']*)["\']', element_html, re.IGNORECASE)
    class_match = re.search(r'class=["\']([^"\']*)["\']', element_html, re.IGNORECASE)
    type_match = re.search(r'type=["\']([^"\']*)["\']', element_html, re.IGNORECASE)
    placeholder_match = re.search(r'placeholder=["\']([^"\']*)["\']', element_html, re.IGNORECASE)
    value_match = re.search(r'value=["\']([^"\']*)["\']', element_html, re.IGNORECASE)
    
    element_id = id_match.group(1) if id_match else None
    element_name = name_match.group(1) if name_match else None
    element_class = class_match.group(1) if class_match else None
    element_type = type_match.group(1) if type_match else None
    element_placeholder = placeholder_match.group(1) if placeholder_match else None
    element_value = value_match.group(1) if value_match else None
    
    # Extract text content
    text_match = re.search(r'>([^<]+)<', element_html)
    element_text = text_match.group(1).strip() if text_match else None
    
    # Build XPath
    xpath = _build_xpath(element_id, element_name, tag_name, element_class, element_text)
    
    return {
        "tag": tag_name,
        "id": element_id,
        "name": element_name,
        "class": element_class,
        "type": element_type,
        "text": element_text,
        "placeholder": element_placeholder,
        "value": element_value,
        "xpath": xpath,
        "css_selector": _build_css_selector(element_id, element_name, element_class),
        "html_snippet": element_html[:150]  # First 150 chars
    }


def _build_xpath(element_id, element_name, tag_name, element_class, text):
    """Build XPath expression for an element."""
    
    # Prefer ID-based XPath
    if element_id:
        return f"//{tag_name}[@id='{element_id}']"
    
    # Name-based XPath
    if element_name:
        return f"//{tag_name}[@name='{element_name}']"
    
    # Text-based XPath
    if text and len(text) < 50:
        return f"//{tag_name}[contains(text(), '{text}')]"
    
    # Class-based XPath
    if element_class:
        return f"//{tag_name}[contains(@class, '{element_class.split()[0]}')]"
    
    # Generic XPath
    return f"//{tag_name}"


def _build_css_selector(element_id, element_name, element_class):
    """Build CSS selector for an element."""
    
    if element_id:
        return f"#{element_id}"
    
    if element_name:
        return f"[name='{element_name}']"
    
    if element_class:
        return f".{element_class.split()[0]}"
    
    return ""


# Tool 11: Extract UI Elements with Playwright (Dynamic extraction)
async def get_element_details_with_playwright(website_url: str, element_types: str = "button,input,link,form") -> dict:
    """Extract UI element details using Playwright for dynamic/JavaScript-rendered content."""
    
    if not website_url or not website_url.strip():
        return {"status": "error", "error_message": "Website URL cannot be empty"}
    
    try:
        types_list = [t.strip().lower() for t in element_types.split(",")]
        
        # Use sync wrapper that handles nested event loops
        result = extract_elements_sync(website_url, types_list)
        
        if not result.get("success"):
            return {"status": "error", "error_message": result.get("error", "Failed to extract elements")}
        
        return {
            "status": "success",
            "url": website_url,
            "extraction_method": "Playwright (Dynamic Rendering)",
            "total_elements_found": result.get("total_elements_found", 0),
            "elements_by_type": result.get("elements_by_type", {}),
            "elements": result.get("elements", []),
            "note": "These locators are extracted from actual browser rendering, including JavaScript-rendered content"
        }
    
    except Exception as e:
        return {"status": "error", "error_message": f"Playwright extraction failed: {str(e)}"}


# Tool 12: Generate Playwright Test Script
def generate_playwright_test_script_tool(user_story: str, website_url: str = None, test_types: str = "positive,negative,edge") -> dict:
    """Generate Playwright test scripts from test cases and element locators."""
    
    if not user_story or not user_story.strip():
        return {"status": "error", "error_message": "User story cannot be empty"}
    
    try:
        # Extract elements to get locators
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        elements_result = loop.run_until_complete(
            get_element_details_with_playwright(website_url or "https://www.macys.com")
        ) if website_url else {"success": False, "elements": []}
        
        # Generate test cases first
        test_cases_result = generate_test_cases(user_story, test_types)
        
        if test_cases_result.get("status") == "error":
            return test_cases_result
        
        # Parse test cases
        test_cases_text = test_cases_result.get("test_cases", "")
        test_cases_list = []
        
        # Simple parsing of test cases
        if test_cases_text:
            test_blocks = test_cases_text.split("---") if "---" in test_cases_text else [test_cases_text]
            for i, block in enumerate(test_blocks[:9]):  # Limit to 9 test cases
                test_cases_list.append({
                    "id": f"tc_{i+1:03d}",
                    "title": f"Test Case {i+1}",
                    "type": ["positive", "negative", "edge"][i % 3]
                })
        
        # Generate Playwright script
        elements_dict = {
            "buttons": elements_result.get("elements", {}).get("buttons", [])[:5],
            "inputs": elements_result.get("elements", {}).get("inputs", [])[:5],
            "links": elements_result.get("elements", {}).get("links", [])[:3],
            "forms": elements_result.get("elements", {}).get("forms", [])[:2],
        }
        
        script_result = generate_playwright_test_script(user_story, elements_dict, test_cases_list)
        
        return {
            "status": "success",
            "script_format": "Playwright (TypeScript)",
            "filename": script_result.get("filename"),
            "test_script": script_result.get("code"),
            "instructions": script_result.get("instructions", []),
            "elements_used_for_locators": len(elements_dict.get("buttons", [])) + len(elements_dict.get("inputs", []))
        }
    
    except Exception as e:
        return {"status": "error", "error_message": f"Script generation failed: {str(e)}"}


# Tool 13: Generate Selenium Test Script
def generate_selenium_test_script_tool(user_story: str, website_url: str = None, test_types: str = "positive,negative,edge") -> dict:
    """Generate Selenium test scripts from test cases and element locators."""
    
    if not user_story or not user_story.strip():
        return {"status": "error", "error_message": "User story cannot be empty"}
    
    try:
        # Generate test cases first
        test_cases_result = generate_test_cases(user_story, test_types)
        
        if test_cases_result.get("status") == "error":
            return test_cases_result
        
        # Parse test cases
        test_cases_text = test_cases_result.get("test_cases", "")
        test_cases_list = []
        
        # Simple parsing of test cases
        if test_cases_text:
            test_blocks = test_cases_text.split("---") if "---" in test_cases_text else [test_cases_text]
            for i, block in enumerate(test_blocks[:9]):  # Limit to 9 test cases
                test_cases_list.append({
                    "id": f"tc_{i+1:03d}",
                    "title": f"Test Case {i+1}",
                    "type": ["positive", "negative", "edge"][i % 3]
                })
        
        # Get elements if URL provided
        elements_dict = {}
        if website_url:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            elements_result = loop.run_until_complete(
                get_element_details_with_playwright(website_url)
            )
            
            elements_dict = {
                "buttons": elements_result.get("elements", {}).get("buttons", [])[:5],
                "inputs": elements_result.get("elements", {}).get("inputs", [])[:5],
                "forms": elements_result.get("elements", {}).get("forms", [])[:2],
            }
        
        # Generate Selenium script
        script_result = generate_selenium_test_script(user_story, elements_dict, test_cases_list)
        
        return {
            "status": "success",
            "script_format": "Selenium (Python)",
            "filename": script_result.get("filename"),
            "test_script": script_result.get("code"),
            "instructions": script_result.get("instructions", []),
            "elements_used_for_locators": len(elements_dict.get("buttons", [])) + len(elements_dict.get("inputs", []))
        }
    
    except Exception as e:
        return {"status": "error", "error_message": f"Script generation failed: {str(e)}"}


# Master Orchestration Function: Complete Workflow
async def generate_complete_test_suite(user_story: str, website_url: str = None) -> dict:
    """
    MASTER FUNCTION: Complete automated workflow
    1. Crawl website (if URL provided) → saves HTML/Markdown
    2. Extract UI elements from crawled content
    3. Generate test cases (using context from website)
    4. Use Playwright to get element locators for those test cases
    5. Return: Test cases + Element locators + Playwright scripts
    """
    
    if not user_story or not user_story.strip():
        return {"status": "error", "error_message": "User story cannot be empty"}
    
    result = {
        "status": "success",
        "user_story": user_story,
        "workflow_steps": [],
        "website_url": website_url,
        "crawl_data": None,
        "test_cases": None,
        "element_locators": None,
        "playwright_script": None,
        "selenium_script": None
    }
    
    try:
        # STEP 1: Crawl website if URL provided
        if website_url and website_url.strip():
            result["workflow_steps"].append("Step 1: Crawling website...")
            crawl_result = await crawl_website(website_url)
            
            if crawl_result.get("success"):
                result["crawl_data"] = {
                    "status": "success",
                    "html_file": crawl_result.get("html_file"),
                    "markdown_file": crawl_result.get("markdown_file"),
                    "url": website_url
                }
                result["workflow_steps"].append(f"✓ Website crawled: HTML and Markdown saved")
                
                # STEP 2: Generate test cases using website context
                result["workflow_steps"].append("Step 2: Generating context-aware test cases...")
                test_result = await generate_test_cases_with_context(user_story, website_url, "positive,negative,edge")
                
                if test_result.get("status") == "success":
                    result["test_cases"] = {
                        "status": "success",
                        "test_cases": test_result.get("test_cases", ""),
                        "test_count": len(test_result.get("test_cases", "").split("---")) if test_result.get("test_cases") else 0
                    }
                    result["workflow_steps"].append(f"✓ Test cases generated ({result['test_cases']['test_count']} cases)")
                    
                    # STEP 3: Extract element locators with Playwright
                    result["workflow_steps"].append("Step 3: Extracting element locators with Playwright...")
                    pw_result = await get_element_details_with_playwright(website_url, "button,input,form,link,select")
                    
                    if pw_result.get("status") == "success":
                        result["element_locators"] = {
                            "status": "success",
                            "extraction_method": "Playwright (Real Browser)",
                            "total_elements": pw_result.get("total_elements_found", 0),
                            "elements_by_type": pw_result.get("elements_by_type", {}),
                            "elements": pw_result.get("elements", [])
                        }
                        result["workflow_steps"].append(f"✓ Element locators extracted: {pw_result.get('total_elements_found', 0)} elements found")
                        
                        # STEP 4: Generate Playwright test script
                        result["workflow_steps"].append("Step 4: Generating Playwright test script...")
                        pw_script_result = generate_playwright_test_script_tool(user_story, website_url, "positive,negative,edge")
                        
                        if pw_script_result.get("status") == "success":
                            result["playwright_script"] = {
                                "status": "success",
                                "format": pw_script_result.get("script_format"),
                                "code": pw_script_result.get("test_script"),
                                "filename": pw_script_result.get("filename"),
                                "instructions": pw_script_result.get("instructions", [])
                            }
                            result["workflow_steps"].append("✓ Playwright test script generated")
                        
                        # STEP 5: Generate Selenium test script
                        result["workflow_steps"].append("Step 5: Generating Selenium test script...")
                        sel_script_result = generate_selenium_test_script_tool(user_story, website_url, "positive,negative,edge")
                        
                        if sel_script_result.get("status") == "success":
                            result["selenium_script"] = {
                                "status": "success",
                                "format": sel_script_result.get("script_format"),
                                "code": sel_script_result.get("test_script"),
                                "filename": sel_script_result.get("filename"),
                                "instructions": sel_script_result.get("instructions", [])
                            }
                            result["workflow_steps"].append("✓ Selenium test script generated")
                        
                        result["workflow_steps"].append("\n✅ COMPLETE: All steps finished successfully!")
                    else:
                        result["workflow_steps"].append(f"⚠ Playwright extraction: {pw_result.get('error_message', 'Failed')}")
                else:
                    result["workflow_steps"].append(f"⚠ Test case generation failed: {test_result.get('error_message', 'Unknown error')}")
            else:
                result["workflow_steps"].append(f"⚠ Website crawl failed: {crawl_result.get('error', 'Unknown error')}")
        else:
            # No URL provided - just generate test cases from story
            result["workflow_steps"].append("Step 1: No website URL provided - generating test cases from story only...")
            test_result = generate_test_cases(user_story, "positive,negative,edge")
            
            if test_result.get("status") == "success":
                result["test_cases"] = {
                    "status": "success",
                    "test_cases": test_result.get("test_cases", ""),
                    "test_count": len(test_result.get("test_cases", "").split("---")) if test_result.get("test_cases") else 0
                }
                result["workflow_steps"].append(f"✓ Test cases generated ({result['test_cases']['test_count']} cases)")
                result["workflow_steps"].append("💡 TIP: Provide a website URL to get element locators and executable test scripts")
    
    except Exception as e:
        result["status"] = "error"
        result["error_message"] = str(e)
        result["workflow_steps"].append(f"❌ Error: {str(e)}")
    
    return result


root_agent = Agent(
    name="testcase_generation_agent",
    model="gemini-2.0-flash",
    description="An AI QA engineer agent that generates test cases from user stories or websites.",
    instruction="""You are an expert QA Engineer. You can generate comprehensive test cases in two ways:

**Mode 1: Story-Based (Recommended for given user stories)**
1. Use parse_user_story to extract actor, action, and goal
2. Use generate_test_cases to create test cases (positive, negative, edge)
3. Use format_test_cases_as_markdown to format the output

**Mode 2: Website-Based (For URLs)**
1. Use crawl_website to fetch page content (saves HTML and Markdown files automatically)
2. Use extract_ui_from_crawled to extract UI elements from saved files
3. Use build_ui_flow_from_crawled to build UI action graphs and flows
4. Generate test cases based on the UI structure and interactions

**Mode 3: Story + Website Context (RECOMMENDED - Most Realistic)**
1. Use generate_test_cases_with_context(user_story, website_url)
2. This automatically:
   - Crawls the website
   - Reads the HTML file to understand page structure
   - Extracts UI elements (buttons, forms, inputs)
   - Generates test cases SPECIFIC to that website
3. Use format_test_cases_as_markdown to format the output
4. Test cases will reference actual UI elements found on the page

**Alternative Mode 2 (Direct HTML - Legacy):**
1. Use crawl_website to fetch page content
2. Use extract_ui_elements_tool to identify interactive elements
3. Use build_ui_action_graph to understand user flows
4. Generate test cases based on the UI structure and interactions

**Element Details / Locator Information:**
To get XPath, ID, tag, name, and other attributes of UI elements:
1. Use get_element_details(element_type) where element_type is:
   - "button" → Extract all buttons with XPath, ID, name, class
   - "input" → Extract all input fields with XPath, ID, name, type, placeholder
   - "form" → Extract all forms with XPath, ID, name
   - "link" or "a" → Extract all links with XPath, href, text
2. Returns: XPath, CSS Selector, ID, name, class, type, and other attributes
3. Great for: Test automation scripts, Selenium/Playwright locators, element identification

**Test Case Requirements:**
For each type (positive, negative, edge), create 3 detailed test cases:
- **Positive**: Valid inputs, happy path, expected success
- **Negative**: Error handling, invalid inputs, missing fields, unauthorized access
- **Edge**: Boundary conditions, special characters, extreme values, security concerns

Always provide:
- Test ID (TC-P001, TC-N001, TC-E001, etc.)
- Title describing what is tested
- Type, Priority, Description
- Preconditions (setup requirements)
- Numbered steps (1, 2, 3...)
- Expected results

Make test cases specific to the story or website context, not generic.

**Dynamic Element Extraction with Playwright:**
When you need accurate element locators for JavaScript-rendered content:
1. Use get_element_details_with_playwright(website_url, element_types)
2. Automatically renders page in real browser, extracts:
   - XPath locators
   - CSS selectors
   - Element visibility status
   - All attributes (ID, name, class, type, etc.)
3. Returns locators suitable for Playwright, Selenium, or Cypress tests

**Test Script Generation (Automated):**
After analyzing requirements and extracting elements, generate executable test code:
1. Use generate_playwright_test_script_tool(user_story, website_url) for TypeScript/Playwright
2. Use generate_selenium_test_script_tool(user_story, website_url) for Python/Selenium
3. Output: Complete test files ready to run (npm test for Playwright, python test_cases.py for Selenium)
4. Test cases will use actual extracted locators for reliable automation

**Full Workflow Example:**
1. Ask me to test "As a customer, I want to search for shoes"
2. I'll crawl Macy's, extract UI elements with Playwright
3. Generate context-aware test cases
4. Create executable Playwright/Selenium test code
5. You can run tests immediately without modification

**⭐ RECOMMENDED WORKFLOW: Complete Test Suite Generation**
Use this single function for complete end-to-end automation:
1. generate_complete_test_suite(user_story, website_url)
2. This automatically:
   - Crawls website → saves HTML/Markdown
   - Generates context-aware test cases (9 cases total)
   - Extracts element locators with Playwright (real browser)
   - Generates Playwright TypeScript test script
   - Generates Selenium Python test script
   - Returns EVERYTHING in one response
3. Output: Ready-to-run test files + documentation + element locators""",
    tools=[
        generate_complete_test_suite,
        parse_user_story,
        generate_test_cases,
        generate_test_cases_with_context,
        format_test_cases_as_markdown,
        crawl_website,
        extract_ui_elements_tool,
        build_ui_action_graph,
        extract_ui_from_crawled,
        build_ui_flow_from_crawled,
        get_element_details,
        get_element_details_with_playwright,
        generate_playwright_test_script_tool,
        generate_selenium_test_script_tool
    ],
)

